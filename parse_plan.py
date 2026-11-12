#!/usr/bin/env python3
import json
import re
from bs4 import BeautifulSoup

def parse_html(html_content, config):
    soup = BeautifulSoup(html_content, "html.parser")
    target_grade = config.get("grade", "").upper().strip()
    my_courses = [c.upper().strip() for c in config.get("my_courses", [])]
    include_grade_wide = config.get("include_grade_wide_announcements", True)

    results = []

    # Suche Abschnitte für die Tage (h2 oder Datum-Divs)
    # Typo3 Container suchen
    # Die Tabellen 2 und 4 sind die Haupttabellen
    tables = soup.find_all("table", class_="contenttable")
    
    # Finde Datums-Header
    date_divs = []
    for div in soup.find_all(["div", "p"]):
        txt = div.get_text(strip=True)
        m = re.match(r"(\d{1,2}\.\d{1,2}\.\d{4}\s+[A-Za-zäöüÄÖÜ]+)", txt)
        if m and m.group(1) not in date_divs:
            date_divs.append(m.group(1))

    # Zuordnung: Für jeden Tag gibt es meist 2 Tabellen (Nachrichten + Vertretungen)
    # Vertretungs-Tabellen haben den Header 'Klasse(n)'
    vplan_tables = []
    for t in tables:
        th_texts = [th.get_text(strip=True) for th in t.find_all("th")]
        if any("Klasse" in th for th in th_texts):
            vplan_tables.append(t)

    for idx, table in enumerate(vplan_tables):
        day_date = date_divs[idx] if idx < len(date_divs) else f"Tag {idx+1}"
        
        rows = table.find_all("tr")
        if not rows:
            continue
            
        # Headers ermitteln
        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cols) < len(headers):
                # Padding falls Zellen fehlen
                cols += [""] * (len(headers) - len(cols))
            
            row_data = dict(zip(headers, cols))
            
            klasse = row_data.get("Klasse(n)", "").strip()
            stunde = row_data.get("Stunde", "").strip()
            fach = row_data.get("Fach", "").strip()
            orig_fach = row_data.get("(Fach)", "").strip()
            vertreter = row_data.get("Vertreter", "").strip()
            orig_lehrer = row_data.get("(Lehrer)", "").strip()
            raum = row_data.get("Raum", "").strip()
            info_text = row_data.get("Text", "").strip()

            # Filterung:
            # 1. Passt die Klasse / Stufe?
            klasse_upper = klasse.upper()
            
            matches_grade = False
            if target_grade:
                # z.B. "Q13" in "Q13" oder "10C" in "10C_FL"
                if target_grade in klasse_upper:
                    matches_grade = True
            else:
                matches_grade = True # wenn keine Stufe gewählt, alles nehmen

            if not matches_grade:
                continue

            # 2. Oberstufe / Kurskürzel-Filter
            is_relevant = False
            matched_course = None

            if my_courses:
                # Prüfen, ob eines der Kürzel in Fach, (Fach) oder Text vorkommt
                search_pool = f"{fach.upper()} {orig_fach.upper()} {info_text.upper()}"
                for course in my_courses:
                    # Wortgrenzen oder direkter Match (z.B. 2F2 in 2F2)
                    if re.search(r'\b' + re.escape(course) + r'\b', search_pool) or course in orig_fach.upper() or course in fach.upper():
                        is_relevant = True
                        matched_course = course
                        break
                
                # Wenn kein spezieller Kurs matcht, aber es eine stufenweite Ankündigung ist
                if not is_relevant and include_grade_wide:
                    if not orig_fach and not fach:
                        is_relevant = True
                        matched_course = "Stufe"
            else:
                # Wenn keine Kurse definiert sind (Unter-/Mittelstufe), gilt alles für die Klasse
                is_relevant = True

            if is_relevant:
                is_entfall = (vertreter == "---" or raum == "---" or "entfall" in info_text.lower())
                results.append({
                    "date": day_date,
                    "stunde": stunde,
                    "klasse": klasse,
                    "kurs": matched_course or orig_fach or fach,
                    "fach": fach,
                    "orig_fach": orig_fach,
                    "vertreter": vertreter,
                    "orig_lehrer": orig_lehrer,
                    "raum": raum,
                    "text": info_text,
                    "entfall": is_entfall,
                    "id": f"{day_date}_{stunde}_{klasse}_{orig_fach}_{fach}_{vertreter}_{raum}"
                })

    return results

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    
    # Zum Testen fügen wir 2f2 und 2M1 hinzu, die in den Testdaten vorhanden sind
    test_config = dict(config)
    test_config["grade"] = "Q13"
    test_config["my_courses"] = ["2F2", "2M1", "2B3"]

    with open("vertretungsplan_dump.html") as f:
        html = f.read()

    entries = parse_html(html, test_config)
    print(f"Gefundene relevante Einträge: {len(entries)}")
    for e in entries:
        status = "❌ ENTFALL" if e["entfall"] else "🔄 VERTRETUNG"
        print(f"[{status}] {e['date']} | Std: {e['stunde']}")
        print(f"   Kurs/Fach: {e['orig_fach']} -> {e['fach'] or e['orig_fach']}")
        print(f"   Lehrer: {e['orig_lehrer']} -> Vertreter: {e['vertreter']} | Raum: {e['raum']}")
        if e['text']:
            print(f"   Hinweis: {e['text']}")
        print()
