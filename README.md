# MGM Vertretungsplan Notifier (Michaeli-Gymnasium München) INOFFIZIELL

> ⚠️ **Inoffizielles Schüler-Projekt:** Dies ist kein offizielles Angebot der Schulleitung des Michaeli-Gymnasiums München, sondern ein privates Open-Source-Projekt von und für Schüler.

Automatischer Vertretungsplan-Checker für Schülerinnen und Schüler des Michaeli-Gymnasiums München.  
Ruft den Vertretungsplan regelmäßig via **GitHub Actions** ab und sendet dir **persönliche Push-Benachrichtigungen aufs Handy (via Telegram)** – du wirst nur informiert, wenn deine eigene Klasse bzw. deine Oberstufen-Kurse betroffen sind!

---

## 📋 Was du brauchst

Bevor du startest, stelle sicher, dass du folgende 3 Dinge bereit hast:
1. **Deinen MS Teams / Microsoft Schul-Login** (E-Mail und Passwort)
2. **Die Telegram-App** auf deinem Smartphone
3. **Einen kostenlosen GitHub-Account**

---

## Schritt 1: Deinen persönlichen Telegram-Bot erstellen (ca. 1 Minute)

Damit dir dein Bot Benachrichtigungen aufs Smartphone senden darf, brauchst du ein Bot-Token und deine persönliche Chat-ID:

### 1. Bot erstellen & Token kopieren
1. Öffne in Telegram den Link: **[t.me/BotFather](https://t.me/BotFather)**
2. Sende den Befehl `/newbot`.
3. Gib deinem Bot einen beliebigen Anzeigenamen (z. B. `Mein MGM Plan`).
4. Gib deinem Bot einen Benutzernamen, der zwingend auf `bot` enden muss (z. B. `max_mgm_vplan_bot`).
5. BotFather sendet dir eine Nachricht mit deinem **HTTP API Token** (sieht so aus: `7123456789:AAH...`).  
   👉 **Kopiere diesen Token** (das ist dein `TELEGRAM_BOT_TOKEN`).

### 2. Deine Telegram Chat-ID herausfinden
1. Öffne in Telegram den Link: **[t.me/userinfobot](https://t.me/userinfobot)**
2. Klicke unten auf **Starten** (bzw. sende `/start`).
3. Der Bot antwortet mit deiner Profil-Info. Kopiere die reine Zahl hinter **`Id:`** (z. B. `123456789`).  
   👉 **Kopiere diese Zahl** (das ist deine `TELEGRAM_CHAT_ID` – *Wichtig: Es muss die Nummer sein, nicht dein @username!*).

### 3. ⚠️ GANZ WICHTIG: Deinen eigenen Bot freischalten!
Telegram verbietet Bots aus Spamschutzgründen, Nutzer unaufgefordert anzuschreiben.
* Suche in Telegram nach deinem **eigenen neu erstellten Bot** (z. B. `@max_mgm_vplan_bot`).
* Tippe unten auf **„Starten“** (bzw. schicke ihm eine kurze Nachricht wie `/start` oder `Hallo`).  
👉 **Erst jetzt darf der Bot dir Nachrichten senden!**

---

## Schritt 2: Auf GitHub einrichten (Mit 1-Klick-Buttons)

[![1. Repository forken](https://img.shields.io/badge/Schritt_1-Repository_jetzt_Forken-blue?style=for-the-badge&logo=github)](https://github.com/zfgf11/mgm-vertretungsbot-inoffiziell/fork)

### 1. Fork erstellen
Klicke auf den blauen Button oben (oder rechts oben auf GitHub auf **Fork**), um dieses Projekt in deinen eigenen GitHub-Account zu kopieren.

---

### 2. Deine Zugangsdaten eintragen (Secrets)
Gehe in deinem geforkten Repository auf:  
👉 **Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ Klicke auf **New repository secret**

Erstelle dort folgende 4 Secrets:

| Secret Name | Wert |
| :--- | :--- |
| `MGM_EMAIL` | Deine MS Teams / Microsoft Schul-E-Mail (`... @onmicrosoft.michaeli-gymnasium.de`) |
| `MGM_PASSWORD` | Dein persönliches Microsoft Teams Schul-Passwort |
| `TELEGRAM_BOT_TOKEN` | Dein Token von BotFather |
| `TELEGRAM_CHAT_ID` | Deine numerische Chat-ID von userinfobot |

---

### 3. Deine Klasse & Kurse festlegen (Variables)
Klicke direkt neben *Secrets* auf den Reiter **Variables** ➔ Klicke auf **New repository variable**:

* **Für ALLE Schüler (Klasse 5 bis 11 und Q12/Q13):**
  * **Name:** `KLASSE`  
  * **Value:** Deine Klasse oder Stufe, z. B. `7B` oder `Q13`

* **Zusätzlich NUR für die Oberstufe (Q12 / Q13):**  
  *(Schüler der Klassen 5–11 überspringen diesen Schritt!)*
  * **Name:** `KURSE`  
  * **Value:** Deine persönlichen Kurskürzel kommagetrennt, z. B.:  
    `2D5, 2ku4, 2b2, 2WR1, 2pha1, 2smw4_Volleyb.1, 2e2`

---

### 4. Automatischen Ablauf starten

1. Klicke in deinem Repository ganz oben in der **Haupt-Navigationsleiste** auf den Reiter **Actions**  
   *(⚠️ **Wichtig:** Gemeint ist der Menüpunkt ganz oben auf der GitHub-Seite neben „Code“, „Issues“, „Pull requests“ usw. – **NICHT** der Unterpunkt „Actions“ in der linken Seitenleiste der Settings, in denen du gerade warst!)*
2. Klicke auf die blaue Schaltfläche **"I understand my workflows, go ahead and enable them"** (falls GitHub danach fragt).
3. Klicke links auf **Check Vertretungsplan**.
4. Klicke rechts auf **Run workflow** ➔ grüner Button **Run workflow**, um den ersten Testlauf sofort manuell zu starten.

🎉 **Fertig!** Ab sofort prüft GitHub Actions den Vertretungsplan montags bis freitags alle 15 Minuten zwischen 06:00 und 17:00 Uhr und sendet dir automatisch eine Push-Mitteilung aufs Handy, sobald sich etwas für dich ändert!

---

## 🛠️ Für Entwickler: Lokales Testen

```bash
# 1. Virtuelle Umgebung erstellen und Abhängigkeiten installieren
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install firefox

# 2. .env Datei anlegen
cp .env.example .env
# Trage deine Zugangsdaten und Telegram-Keys in .env ein

# 3. Skript ausführen
python main.py
```

---
Der Code ist KI-Generiert
