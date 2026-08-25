# Trainingslog

Persönliche Trainings-App, entwickelt von Lennart als Hobby-Projekt zum Lernen.

## Projekt-Setup

- **Struktur:** Single-File-Web-App — alles liegt in `index.html` (HTML, CSS, JavaScript inline)
- **Backend:** Firebase (Auth + Firestore)
- **Hosting:** GitHub Pages
- **Zielgerät:** iPhone Safari (mobile-first). Desktop ist zweitrangig.
- **Offline:** zweitrangig — einzelne Features dürfen netzpflichtig sein (z. B. Kartenkacheln), solange die Kernfunktionen ohne Netz weiterlaufen.

## Arbeitsweise

### Immer
- Bei UI-Änderungen: lokal starten (`python3 -m http.server 8000` o. ä.) und im Browser prüfen, bevor als „fertig" gemeldet wird.
- Änderungen so klein wie möglich halten. Keine Refactorings, die nicht Teil der Aufgabe sind.
- Mobile-Tauglichkeit prüfen: 375 px Viewport, Touch-Ziele ≥ 44 px, `font-size: 16px` bei Inputs (verhindert iOS-Zoom).
- Auf Deutsch antworten.

### Niemals
- Nicht automatisch `git push` ausführen. Erst zeigen, was gepusht würde, dann Bestätigung abwarten.
- Keine externen Dependencies hinzufügen ohne explizite Rückfrage — die App soll Single-File bleiben.
- Keine Firebase-Konfiguration oder API-Keys aus `index.html` entfernen oder umschreiben ohne Rückfrage.
- Keine Kommentare in den Code schreiben, die nur beschreiben *was* der Code macht (Naming reicht). Nur *warum* wenn nicht offensichtlich.

## App-Konventionen (UI-Muster)

- **Bereiche:** Vier Trainingsarten — Kraft, Rad, Laufen, Kurse. Rad/Laufen/Kurse laufen über die gemeinsame `ACT`-Config + `renderAct*`-Funktionen.
- **Zwei Einstellungs-Ebenen:** „Einstellungen" (Tippen aufs Logo) = Bereiche ein/aus + global. **Long-Press auf eine Bereichs-Zeile** dort öffnet das bereichsspezifische Menü. „Stile" (Zahnrad) bleibt separat für Farben + Kartenstil.
- **Hero-Name antippen wechselt schnell:** Kraft-Buchstabe → nächstes Training (`toggleDay`), Kursname → nächste Kursart (`cycleKursType`). Dezenter Hinweistext, kein prominentes Label.
- **Aktivitäten speichern in einem Schritt:** Rad/Laufen/Kurse haben einen „… speichern"-Button (`quickSaveAct`), kein Start/Stopp. (Aktive Session + „Verwerfen" existiert nur noch als Alt-Pfad.)
- **Kurse:** optionaler YouTube-Link mit Live-Vorschau; Thumbnail `maxresdefault` → Fallback `hqdefault` → ausblenden bei ungültig.
- **Kraft-Verlauf:** je Übung schwarze Satz-Punkte (ein Punkt = ein Satz) + Max-Gewicht.
- **Vorbelegung:** Eingabe schlägt pro Satz den entsprechenden Satz von letztem Mal vor (`lastSetsFor`, Draft springt beim Abhaken weiter).

## Fallstricke

- **`draft` beim Store-Wechsel zurücksetzen:** `_reloadStore` (Cloud-Load nach Login) muss `draft={}` setzen, sonst bleibt die Vorbelegung auf Standardwerten hängen.
- **Destruktive Aktionen erhalten Appearance/Prefs:** `wipe()` muss Farben (`accent*`), `mapStyle`, `bike`, `kursType`, `hiddenCats` bewahren und ein **vollständiges** Store-Objekt liefern (inkl. `schemes`, `plans`, `deleted`), sonst Crash in `dayLabel`.
- **Fokus-Umrandung** wird pro aktivem Bereich eingefärbt (`body.cat*`); Ausnahmen bei Bedarf per ID überschreiben (z. B. `#setOverlay` immer schwarz).

## User

Lennart lernt beim Bauen. Erklärungen dürfen kurz sein, aber Fachbegriffe kurz erläutern wenn sie zum ersten Mal auftauchen. Keine „junior-Warnungen" — direkte Kommunikation bevorzugt.

## CLAUDE.md pflegen

Alle 10 User-Anfragen einmal kurz nachfragen: „Soll ich etwas Neues in die CLAUDE.md aufnehmen — neue Konventionen, wiederkehrende Wünsche, oder Dinge, die diese Session gelernt hat?"

Zählen: Ab dem ersten Prompt der Session mitzählen; nach der Nachfrage Zähler zurücksetzen. Wenn Lennart nichts hinzufügen möchte, keine weiteren Vorschläge machen — einfach weiterarbeiten und in 10 Anfragen erneut fragen.
