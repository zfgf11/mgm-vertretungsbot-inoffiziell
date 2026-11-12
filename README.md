# MGM Vertretungsplan Notifier (Michaeli-Gymnasium München)

> ⚠️ **Inoffizielles Schüler-Projekt:** Dies ist kein offizielles Angebot der Schulleitung des Michaeli-Gymnasiums München, sondern ein privates Open-Source-Projekt von und für Schüler.

Automatischer Vertretungsplan-Checker für Schülerinnen und Schüler des Michaeli-Gymnasiums München.  
Ruft den Vertretungsplan regelmäßig via **GitHub Actions** ab und sendet dir **persönliche Push-Benachrichtigungen aufs Handy (via Telegram)** – du wirst nur informiert, wenn deine eigene Klasse bzw. deine Oberstufen-Kurse betroffen sind!

---

## Features

- 🔒 **Sicher:** Deine Microsoft Teams Zugangsdaten werden verschlüsselt in GitHub Secrets gespeichert und niemals öffentlich im Code sichtbar.
- 🎯 **Persönliche Benachrichtigung:** Filtert gezielt nach deiner Klasse (z. B. `7B`, `Q12`, `Q13`) und deinen individuellen Oberstufen-Kurskürzeln (z. B. `2M1`, `2f2`, `ph1`).
- 🖥️ **Einfache Bedienung:** Die Klasse und Kurse können direkt im Browser über GitHub-Variablen eingetragen werden.
- 🔄 **Nur bei echten Änderungen:** Bereits gesehene Vertretungen werden zwischengespeichert – keine doppelten Pings.
- ⚡ **100% Kostenlos:** Läuft komplett über GitHub Actions (Cronjob alle 15 Minuten während der Schulzeit). Kein eigener Server nötig.
- 🦊 **Headless Firefox & Playwright:** Schneller und zuverlässiger Microsoft Teams SSO-Login.

---

## Schritt-für-Schritt-Anleitung (Für jeden Schüler)

### Schritt 1: Repository forken
Klicke oben rechts auf GitHub auf den Button **Fork**, um dieses Projekt als eigene Kopie in deinen persönlichen GitHub-Account zu übernehmen.

---

### Schritt 2: Eigene Klasse & Kurse einstellen

Gehe in deinem geforkten Repository auf **Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ Reiter **Variables** (neben Secrets).  
Klicke auf **New repository variable**:

#### 1. Für ALLE Schüler (Klasse 5 bis 11 und Q12 / Q13):
Erstelle die Variable für deine Klasse:
* **Name:** `KLASSE`  
* **Value:** Deine Klasse oder Stufe, z. B. `7B` oder `Q13`

#### 2. NUR für die Oberstufe (Q12 / Q13 relevant):
*Falls du in Klasse 5 bis 11 bist, überspringe diesen Punkt einfach! In der Unter- und Mittelstufe hat die ganze Klasse denselben Stundenplan.*

Für Schüler der Q12 und Q13: Erstelle eine zweite Variable mit deinen persönlichen Kurskürzeln:
* **Name:** `KURSE`  
* **Value:** Deine Kurse kommagetrennt (Groß-/Kleinschreibung egal), z. B.:  
  `2D5, 2ku4, 2b2, 2WR1, 2pha1, 2smw4_Volleyb.1, 2e2`

*(Alternativ kannst du die Fächer auch direkt in der Datei `config.json` über das Stift-Symbol ✏️ im Browser bearbeiten).*

---

### Schritt 3: Telegram-Bot einrichten (Dauert ca. 1 Minute)

Damit dir dein persönlicher Bot Push-Nachrichten aufs Handy schicken darf, brauchst du einen eigenen Bot und deine Chat-ID:

#### 1. Bot erstellen & Token holen
* Öffne den Link: **[t.me/BotFather](https://t.me/BotFather)** in Telegram.
* Sende den Befehl `/newbot`.
* Gib deinem Bot einen beliebigen Anzeigenamen (z. B. `Mein MGM Plan`).
* Gib deinem Bot einen Benutzernamen, der zwingend auf `bot` enden muss (z. B. `max_mgm_vplan_bot`).
* BotFather schickt dir nun deinen **HTTP API Token** (sieht so aus: `7123456789:AAH...`).
  👉 Das ist dein **`TELEGRAM_BOT_TOKEN`**.

#### 2. Deine persönliche Telegram Chat-ID herausfinden
* Öffne den Link: **[t.me/userinfobot](https://t.me/userinfobot)** in Telegram.
* Klicke unten auf **Starten** (bzw. sende `/start`).
* Der Bot antwortet dir mit deinem Profil. Kopiere die reine Zahl hinter **`Id:`** (z. B. `123456789`).
  👉 Das ist deine **`TELEGRAM_CHAT_ID`** *(Wichtig: Es muss die reine Zahl sein, nicht dein @username!)*.

#### 3. ⚠️ WICHTIG: Deinen eigenen Bot freischalten!
Telegram verbietet Bots aus Spamschutzgründen, Nutzer unaufgefordert anzuschreiben.
* Suche in Telegram nach deinem **eigenen Bot** aus Schritt 1 (z. B. nach `@max_mgm_vplan_bot`).
* Drücke unten auf **„Starten“** (bzw. schicke ihm `/start` oder `Hallo`).
* **Erst jetzt darf der Bot dir Nachrichten senden!**

---

### Schritt 4: GitHub Secrets anlegen

Gehe in deinem geforkten GitHub-Repository auf:  
**Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ Klicke auf **New repository secret**

Erstelle dort folgende 4 Secrets (jeweils auf **Add secret** klicken):

| Secret Name | Wert |
| :--- | :--- |
| `MGM_EMAIL` | Deine MS Teams / Microsoft Schul-E-Mail (`... @onmicrosoft.michaeli-gymnasium.de`) |
| `MGM_PASSWORD` | Dein persönliches Microsoft Teams Schul-Passwort |
| `TELEGRAM_BOT_TOKEN` | Dein Token von BotFather |
| `TELEGRAM_CHAT_ID` | Deine numerische Chat-ID von userinfobot |

---

### Schritt 5: Automatischen Ablauf (GitHub Actions) aktivieren

1. Klicke in deinem Repository oben auf den Reiter **Actions**.
2. Klicke auf **"I understand my workflows, go ahead and enable them"** (falls GitHub nach einer Bestätigung fragt).
3. Klicke in der linken Seitenleiste auf **Check Vertretungsplan**.
4. Klicke rechts auf **Run workflow** ➔ grüner Button **Run workflow**, um den ersten Testlauf manuell zu starten.
5. **Fertig!** Ab sofort läuft das Skript montags bis freitags alle 15 Minuten zwischen 06:00 und 17:00 Uhr vollautomatisch im Hintergrund und meldet sich nur bei dir, wenn etwas für dich ansteht.

---

## Lokales Testen (Optional für Entwickler)

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
