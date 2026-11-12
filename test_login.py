#!/usr/bin/env python3
"""
Testskript für den Microsoft-Login auf michaeli-gymnasium.de
Speichert nach erfolgreichem Login die Seite als HTML und Screenshot.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# .env Datei laden
load_dotenv()

MGM_EMAIL = os.getenv("MGM_EMAIL")
MGM_PASSWORD = os.getenv("MGM_PASSWORD")

if not MGM_EMAIL or not MGM_PASSWORD:
    print("\n[FEHLER] Bitte trage deine Zugangsdaten in eine .env-Datei ein:")
    print('  MGM_EMAIL="dein.name@onmicrosoft.michaeli-gymnasium.de"')
    print('  MGM_PASSWORD="dein_passwort"\n')
    print("Oder erstelle die Datei .env basierend auf .env.example.\n")
    sys.exit(1)

HEADLESS = "--visible" not in sys.argv and "--gui" not in sys.argv

def run():
    print(f"[*] Starte Firefox (Headless: {HEADLESS})...")
    with sync_playwright() as p:
        # Browser starten (Firefox)
        browser = p.firefox.launch(headless=HEADLESS, slow_mo=300 if not HEADLESS else 0)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # 1. Startseite / Login-Seite aufrufen
        print("[*] Rufe Login-Seite auf...")
        page.goto("https://www.michaeli-gymnasium.de/login", wait_until="networkidle")

        # 2. Auf "Anmelden" (SAML Button) klicken
        print("[*] Klicke auf 'Anmelden' (Microsoft SAML)...")
        # Sucht den Submit-Button im felogin-Formular
        submit_btn = page.locator("form[action*='login'] input[type='submit']")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit'][value*='Anmelden']")
        
        submit_btn.first.click()

        # 3. Warten auf Weiterleitung zu Microsoft Online
        print("[*] Warte auf Weiterleitung zu Microsoft SSO (login.microsoftonline.com)...")
        page.wait_for_url(lambda u: "login.microsoftonline.com" in u, timeout=15000)

        # 4. E-Mail eingeben
        print(f"[*] Gebe E-Mail ein: {MGM_EMAIL}")
        email_input = page.locator("input[type='email'], input[name='loginfmt']")
        email_input.wait_for(state="visible", timeout=15000)
        email_input.click()
        email_input.fill(MGM_EMAIL)
        time.sleep(0.5)
        
        # Klick auf "Weiter" / "Next"
        print("[*] Klicke 'Weiter'...")
        page.locator("#idSIButton9, input[type='submit']").click()

        # 5. Passwort eingeben
        print("[*] Warte auf Passwort-Feld...")
        pwd_input = page.locator("input[type='password'], input[name='passwd']")
        pwd_input.wait_for(state="visible", timeout=15000)
        time.sleep(1.0)
        print("[*] Gebe Passwort ein...")
        pwd_input.click()
        pwd_input.fill(MGM_PASSWORD)
        time.sleep(0.5)

        # Klick auf "Anmelden" / "Sign in"
        print("[*] Klicke 'Anmelden'...")
        page.locator("#idSIButton9, input[type='submit']").click()

        # Warten, bis das Passwortfeld verschwindet (Login wird verarbeitet)
        print("[*] Warte auf Verarbeitung des Logins...")
        pwd_input.wait_for(state="hidden", timeout=15000)
        time.sleep(1.5)

        # 6. "Angemeldet bleiben?" (Stay signed in / KMSI) Dialog behandeln
        if "login.microsoftonline.com" in page.url:
            print("[*] Noch auf Microsoft-Seite. Prüfe auf 'Angemeldet bleiben?'-Dialog...")
            try:
                # Warten auf den KMSI Button
                kmsi_btn = page.locator("#idSIButton9, input[value='Ja'], input[value='Yes']")
                if kmsi_btn.is_visible():
                    print("[*] Bestätige 'Angemeldet bleiben'...")
                    kmsi_btn.click()
            except Exception as e:
                print(f"[*] KMSI-Hinweis: {e}")

        # 7. Warten auf ECHTE Rückkehr zu michaeli-gymnasium.de
        # Wichtig: u.startswith prüfen, da die Microsoft-URL den Schulnamen im Query-Parameter (RelayState) enthält!
        print("[*] Warte auf Weiterleitung zurück zu https://www.michaeli-gymnasium.de/ ...")
        page.wait_for_url(lambda u: u.startswith("https://www.michaeli-gymnasium.de"), timeout=30000)
        page.wait_for_load_state("networkidle")

        current_url = page.url
        print(f"[+] Erfolgreich eingeloggt! Aktuelle URL: {current_url}")

        # Prüfen, ob wir direkt auf dem Vertretungsplan sind oder ein Link im Menü ist
        print("[*] Suche nach Links zum Vertretungsplan...")
        vplan_link = page.locator("a[href*='vertretung'], a:has-text('Vertretungsplan')")
        if vplan_link.count() > 0:
            href = vplan_link.first.get_attribute("href")
            print(f"[+] Link zum Vertretungsplan gefunden: {href}")
            if href.startswith("/"):
                target_url = "https://www.michaeli-gymnasium.de" + href
            elif href.startswith("http"):
                target_url = href
            else:
                target_url = f"https://www.michaeli-gymnasium.de/{href}"
            
            print(f"[*] Navigiere direkt zu: {target_url} ...")
            page.goto(target_url, wait_until="networkidle")
            current_url = page.url
            print(f"[+] Erfolgreich aufgerufen: {current_url}")
        else:
            print("[-] Kein expliziter Link mit 'Vertretung' im Menü gefunden.")
            print("[*] Auszug gefundener Navigations-Links:")
            all_links = page.locator("nav a, main a")
            count = 0
            for i in range(all_links.count()):
                t = all_links.nth(i).inner_text().strip()
                h = all_links.nth(i).get_attribute("href")
                if t and h and not h.startswith("mailto:") and not h.startswith("tel:"):
                    print(f"       * {t} -> {h}")
                    count += 1
                    if count >= 15:
                        break

        # 8. HTML und Screenshot speichern
        out_html = "vertretungsplan_dump.html"
        out_png = "vertretungsplan_screenshot.png"
        
        Path(out_html).write_text(page.content(), encoding="utf-8")
        page.screenshot(path=out_png, full_page=True)

        print(f"\n[ERFOLG] Ergebnisse gespeichert:")
        print(f"  -> HTML:       {Path(out_html).resolve()}")
        print(f"  -> Screenshot: {Path(out_png).resolve()}")

        # Kurze Analyse der Seite
        tables = page.locator("table")
        print(f"\n[INFO] Gefundene HTML-Tabellen: {tables.count()}")
        iframes = page.locator("iframe")
        print(f"[INFO] Gefundene Iframes (z. B. eingebettetes Untis/DSB): {iframes.count()}")
        for i in range(iframes.count()):
            src = iframes.nth(i).get_attribute("src")
            print(f"       Iframe {i+1}: {src}")

        browser.close()
        print("\nFertig!")

if __name__ == "__main__":
    run()
