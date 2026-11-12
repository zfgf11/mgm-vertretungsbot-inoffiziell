#!/usr/bin/env python3
"""
MGM Vertretungsplan Checker & Notifier
Liest den tagesaktuellen Vertretungsplan des Michaeli-Gymnasiums via Microsoft SAML SSO
und sendet persönliche Push-Benachrichtigungen via Telegram.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright
from parse_plan import parse_html

# .env laden
load_dotenv()

MGM_EMAIL = os.getenv("MGM_EMAIL")
MGM_PASSWORD = os.getenv("MGM_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CONFIG_FILE = Path("config.json")
CACHE_FILE = Path("seen_cache.json")
HEADLESS = "--visible" not in sys.argv and "--gui" not in sys.argv


def load_config():
    config = {
        "grade": "Q13",
        "my_courses": [],
        "include_grade_wide_announcements": True
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"[!] Fehler beim Lesen von {CONFIG_FILE}: {e}")

    # Umgebungsvariablen (z. B. aus GitHub Variables oder Workflow Inputs) haben Vorrang
    env_grade = os.getenv("MGM_GRADE")
    if env_grade:
        config["grade"] = env_grade.strip()

    env_courses = os.getenv("MGM_COURSES")
    if env_courses:
        # Kommagetrennte Liste parsen: "2D5, 2ku4, 2b2, 2smw4_Volleyb.1"
        courses_list = [c.strip() for c in env_courses.split(",") if c.strip()]
        config["my_courses"] = courses_list

    return config


def load_cache():
    if not CACHE_FILE.exists():
        return set()
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("seen_ids", []))
    except Exception:
        return set()


def save_cache(seen_ids):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"seen_ids": list(seen_ids)}, f, indent=2)


def fetch_vplan_html():
    if not MGM_EMAIL or not MGM_PASSWORD:
        raise ValueError("MGM_EMAIL oder MGM_PASSWORD fehlen!")

    print(f"[*] Starte Firefox (Headless: {HEADLESS})...")
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=HEADLESS, slow_mo=200 if not HEADLESS else 0)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # 1. Login-Seite aufrufen
        print("[*] Öffne Login...")
        page.goto("https://www.michaeli-gymnasium.de/login", wait_until="networkidle")

        # 2. SAML Anmelden klicken
        submit_btn = page.locator("form[action*='login'] input[type='submit']")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit'][value*='Anmelden']")
        submit_btn.first.click()

        # 3. Microsoft SSO weiterleiten
        page.wait_for_url(lambda u: "login.microsoftonline.com" in u, timeout=20000)

        # 4. E-Mail eingeben
        email_input = page.locator("input[type='email'], input[name='loginfmt']")
        email_input.wait_for(state="visible", timeout=15000)
        email_input.click()
        email_input.fill(MGM_EMAIL)
        time.sleep(0.5)
        page.locator("#idSIButton9, input[type='submit']").click()

        # 5. Passwort eingeben
        pwd_input = page.locator("input[type='password'], input[name='passwd']")
        pwd_input.wait_for(state="visible", timeout=15000)
        time.sleep(1.0)
        pwd_input.click()
        pwd_input.fill(MGM_PASSWORD)
        time.sleep(0.5)
        page.locator("#idSIButton9, input[type='submit']").click()

        # Warten auf Login-Verarbeitung
        pwd_input.wait_for(state="hidden", timeout=15000)
        time.sleep(1.5)

        # 6. "Angemeldet bleiben?" Dialog
        if "login.microsoftonline.com" in page.url:
            try:
                kmsi_btn = page.locator("#idSIButton9, input[value='Ja'], input[value='Yes']")
                if kmsi_btn.is_visible():
                    kmsi_btn.click()
            except Exception:
                pass

        # 7. Warten auf Rückkehr zu Schulwebsite
        page.wait_for_url(lambda u: u.startswith("https://www.michaeli-gymnasium.de"), timeout=30000)
        page.wait_for_load_state("networkidle")
        print("[+] Login erfolgreich!")

        # 8. Direkt Vertretungsplan aufrufen
        vplan_url = "https://www.michaeli-gymnasium.de/infos-und-termine/vertretungsplan"
        print(f"[*] Rufe Vertretungsplan ab ({vplan_url})...")
        page.goto(vplan_url, wait_until="networkidle")

        html_content = page.content()
        browser.close()
        return html_content


def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Kein Telegram Bot-Token oder Chat-ID konfiguriert. Ausgabe nur im Terminal:")
        print(text)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("[+] Telegram-Benachrichtigung erfolgreich gesendet!")
    except Exception as e:
        print(f"[FEHLER] Telegram-Senden fehlgeschlagen: {e}")


def format_entry(e):
    if e["entfall"]:
        icon = "❌"
        status_line = "<b>ENTFALL</b>"
    else:
        icon = "🔄"
        status_line = "<b>VERTRETUNG</b>"

    kurs_display = e["orig_fach"] or e["fach"] or e["kurs"]
    lehrer_display = e["orig_lehrer"]
    if e["vertreter"] and e["vertreter"] != "---":
        lehrer_display += f" ➡️ <b>{e['vertreter']}</b>"

    lines = [
        f"{icon} {status_line} | <b>{e['date']}</b>",
        f"⏰ <b>Stunde:</b> {e['stunde']}",
        f"📚 <b>Kurs/Fach:</b> <code>{kurs_display}</code> ({e['klasse']})",
    ]

    if e["raum"] and e["raum"] != "---":
        lines.append(f"🚪 <b>Raum:</b> {e['raum']}")
    if lehrer_display:
        lines.append(f"👤 <b>Lehrer:</b> {lehrer_display}")
    if e["text"]:
        lines.append(f"💬 <b>Hinweis:</b> <i>{e['text']}</i>")

    return "\n".join(lines)


def main():
    config = load_config()
    print(f"[*] Geladene Konfiguration: Stufe={config.get('grade')}, Kurse={config.get('my_courses')}")

    try:
        html = fetch_vplan_html()
    except Exception as e:
        print(f"[FEHLER] Konnte Vertretungsplan nicht laden: {e}")
        sys.exit(1)

    entries = parse_html(html, config)
    print(f"[*] Relevante Einträge im Plan: {len(entries)}")

    seen_ids = load_cache()
    new_entries = []

    for entry in entries:
        if entry["id"] not in seen_ids:
            new_entries.append(entry)
            seen_ids.add(entry["id"])

    if not new_entries:
        print("[*] Keine neuen Vertretungen für dich vorhanden.")
    else:
        print(f"[+] {len(new_entries)} NEUE Vertretung(en) gefunden! Sende Benachrichtigung...")
        header = f"🔔 <b>Vertretungsplan Update ({config.get('grade', 'MGM')})</b>\n\n"
        messages = [format_entry(e) for e in new_entries]
        full_text = header + "\n\n────────────────\n\n".join(messages)
        send_telegram(full_text)

    # Cache aktualisieren
    save_cache(seen_ids)
    print("[*] Durchlauf abgeschlossen.")


if __name__ == "__main__":
    main()
