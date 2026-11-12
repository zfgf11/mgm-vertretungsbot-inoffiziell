# MGM Vertretungsplan Notifier (Michaeli-Gymnasium München)

Automatischer Vertretungsplan-Checker für Schülerinnen und Schüler des Michaeli-Gymnasiums München.  
Ruft den Microsoft-geschützten Vertretungsplan regelmäßig via **GitHub Actions** ab und sendet dir **persönliche Push-Benachrichtigungen aufs Handy (via Telegram)** – du wirst nur informiert, wenn deine eigene Klasse bzw. deine Oberstufen-Kurse betroffen sind!

---

## Features

- 🔒 **Sicher:** Deine Microsoft-Schul-Zugangsdaten werden verschlüsselt in GitHub Secrets gespeichert und niemals im Code committet.
- 🎯 **Persönliche Benachrichtigung:** Filtert gezielt nach deiner Stufe (z. B. `Q13`, `Q12`, `10C`) und deinen individuellen Kurskürzeln (z. B. `2M1`, `2f2`, `ph1`).
- 🖥️ **Einfache GUI-Bedienung:** Kurse können wahlweise direkt im Browser über GitHub Variables oder per Klick auf die Datei geändert werden.
- 🔄 **Nur bei Änderungen:** Bereits gesehene Vertretungen werden zwischengespeichert – keine doppelten Pings.
- ⚡ **Kostenlos & serverlos:** Läuft komplett über GitHub Actions (Cronjob alle 15 Minuten während der Schulzeit). Kein eigener Server nötig.
- 🦊 **Headless Firefox & Playwright:** Schneller und stabiler SAML-Login.

---

## Schritt-für-Schritt-Anleitung (Für jeden Schüler)

### Schritt 1: Repository forken
Klicke oben rechts auf GitHub auf den Button **Fork**, um dieses Projekt als eigene Kopie in deinen persönlichen GitHub-Account zu übernehmen.

---

### Schritt 2: Eigene Kurse eintragen (2 einfache Wege)

Wähle die Methode, die dir am leichtesten fällt:

#### Option A: Direkt über die GitHub-Web-GUI (Sehr einfach!)
1. Gehe in deinem geforkten Repository auf **Settings** ➔ **Secrets and variables** ➔ **Actions**.
2. Klicke auf den Reiter **Variables** (neben Secrets).
3. Klicke auf **New repository variable** und erstelle zwei Variablen:
   * **Name:** `MGM_GRADE`  
     **Value:** Deine Stufe, z. B. `Q13` (oder `10C`)
   * **Name:** `MGM_COURSES`  
     **Value:** Deine Kurse kommagetrennt, z. B.:  
     `2D5, 2ku4, 2b2, 2WR1, 2pha1, 2smw4_Volleyb.1, 2e2`  
     *(Wenn du in der Mittel-/Unterstufe bist, lass `MGM_COURSES` einfach weg)*.

#### Option B: Über die Datei `config.json`
1. Klicke auf der Startseite deines Repos auf die Datei **`config.json`**.
2. Klicke rechts oben auf das **Stift-Symbol ✏️ (Edit this file)**.
3. Trage deine Fächer ein und klicke oben rechts auf den grünen Button **Commit changes...**.

---

### Schritt 3: Telegram-Bot einrichten (Dauert ca. 1 Minute)

Damit dir der Bot Push-Nachrichten aufs Handy schicken darf, brauchst du einen eigenen Bot und deine Chat-ID:

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
| `MGM_EMAIL` | Deine Schul-E-Mail (z. B. `vorname.nachname@onmicrosoft.michaeli-gymnasium.de`) |
| `MGM_PASSWORD` | Dein persönliches Microsoft-Schul-Passwort |
| `TELEGRAM_BOT_TOKEN` | Dein Token von BotFather |
| `TELEGRAM_CHAT_ID` | Deine numerische Chat-ID von userinfobot |

---

### Schritt 5: Automatischen Ablauf (GitHub Actions) aktivieren

1. Klicke in deinem Repository oben auf den Reiter **Actions**.
2. Klicke auf **"I understand my workflows, go ahead and enable them"** (falls GitHub nach einer Bestätigung fragt).
3. Klicke in der linken Seitenleiste auf **Check Vertretungsplan**.
4. Klicke rechts auf **Run workflow** ➔ grüner Button **Run workflow**, um den ersten Testlauf manuell zu starten.
5. **Fertig!** Ab sofort läuft das Skript montags bis freitags alle 15 Minuten zwischen 06:00 und 17:00 Uhr vollautomatisch im Hintergrund.

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
