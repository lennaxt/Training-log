# Trainingslog

Trainings-App, entwickelt von Lennart als Hobby-Projekt zum Lernen.

**Nutzerkreis:** Lennart plus ein kleiner Kreis von Freunden (5–10 Personen). Kein
öffentliches Produkt, aber auch keine reine Einzelplatz-App mehr: Bedienbarkeit für
Leute, die die App **nicht gebaut haben**, zählt ab jetzt als Anforderung.

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
- **Nutzerdaten sind unantastbar.** Jede Änderung an Abläufen, Texten oder Ansichten muss
  alle gespeicherten Werte (Einheiten, Pläne, Farben, Einstellungen) unangetastet lassen.
  Neue Felder im Store sind optional, bestehende Werte dürfen nie wegfallen oder ihre
  Bedeutung wechseln. Fehlzustände und „alt trifft neu" (Cloud, `_delSess`) bleiben
  bedacht, sonst verliert ein bestehender Nutzer seine Historie.
- Mobile-Tauglichkeit prüfen: 375 px Viewport, Touch-Ziele ≥ 44 px, `font-size: 16px` bei Inputs (verhindert iOS-Zoom).
- Auf Deutsch antworten.
- Für Fremde bedienbar bauen: sinnvolle Standardwerte statt leerer Auswahl, keine
  versteckte Geste als **einzigen** Weg zu einer Funktion, leere und Fehlzustände
  sagen, was zu tun ist. Gleich aussehende Elemente dürfen sich nicht ungleich
  verhalten — sonst ein sichtbares Zeichen dran (z. B. ↗ für „führt aus der App").
- Fremde Inhalte nur einbauen, wenn die Lizenz es hergibt, und die Quelle dann
  sichtbar nennen. Wikipedia (CC BY-SA) ja, Verlagstexte nein.
- Fertige Arbeit committen **und pushen** — ohne Rückfrage. Lennart arbeitet meist vom Handy und kann nichts lokal prüfen; ein ungepushter Commit ist für ihn unsichtbar.

### Niemals
- Keine externen Dependencies hinzufügen ohne explizite Rückfrage — die App soll Single-File bleiben.
- Keine Firebase-Konfiguration oder API-Keys aus `index.html` entfernen oder umschreiben ohne Rückfrage.
- Keine Kommentare in den Code schreiben, die nur beschreiben *was* der Code macht (Naming reicht). Nur *warum* wenn nicht offensichtlich.

## App-Konventionen (UI-Muster)

- **Bereiche:** Vier Trainingsarten — Kraft, Rad, Laufen, Kurse. Rad/Laufen/Kurse laufen über die gemeinsame `ACT`-Config + `renderAct*`-Funktionen.
- **Rahmen trennt die Ebenen:** Bereichsbezogene Einstellungen stehen in umrandeten
  Kästen (`.sec`), allgemeine stehen frei darüber. Ein allgemeiner Punkt bekommt
  nie einen Rahmen, sonst liest er sich wie eine Bereichs-Einstellung.
- **Zwei Einstellungs-Ebenen:** „Einstellungen" (Tippen aufs Logo) = Bereiche ein/aus + global. **Long-Press auf eine Bereichs-Zeile** dort öffnet das bereichsspezifische Menü. „Stile" (Zahnrad) bleibt separat für Farben + Kartenstil.
- **Hero-Name antippen wechselt schnell:** Kraft-Buchstabe → nächstes Training (`toggleDay`), Kursname → nächste Kursart (`cycleKursType`). Dezenter Hinweistext, kein prominentes Label.
- **Aktivitäten speichern in einem Schritt:** Rad/Laufen/Kurse haben einen „… speichern"-Button (`quickSaveAct`), kein Start/Stopp. (Aktive Session + „Verwerfen" existiert nur noch als Alt-Pfad.)
- **Kurse:** optionaler YouTube-Link mit Live-Vorschau; Thumbnail `maxresdefault` → Fallback `hqdefault` → ausblenden bei ungültig.
- **Kraft-Verlauf:** je Übung schwarze Satz-Punkte (ein Punkt = ein Satz) + Max-Gewicht.
- **Vorbelegung:** Eingabe schlägt pro Satz den entsprechenden Satz von letztem Mal vor (`lastSetsFor`, Draft springt beim Abhaken weiter).
- **Anzeigeschrift ist wählbar, Fließtext nicht.** Alles, was in der Fraunces-Rolle
  steht, nimmt `font-family:var(--display)` — nie wieder eine feste Familie. Gewählt
  wird in „Einstellungen → Schriftarten" (`fontOverlay`, Liste `FONTS`, gespeichert als
  `store.font`); die Schriftdatei wird erst beim Anwählen nachgeladen. Inter trägt
  weiterhin Beschriftungen und Fließtext und bleibt unveränderlich.
- **Hilfe wohnt in den Einstellungen:** „GPX-Routen" in den Bereichs-Einstellungen von
  Rad/Laufen und „App Guide" ganz unten in den Einstellungen sind statische Overlays
  (`gpxOverlay`, `guideOverlay`) mit `.info-body`-Text — kein gespeicherter Zustand,
  kein Bereichs-spezifisches Verhalten außer dem Titel. Neue Hilfe gehört in dieses
  Muster, nicht in den Store.
- **Strava-Import bleibt manuell:** Eine Strava-API-Anbindung ist bewusst nicht umgesetzt
  (kostenpflichtig). GPX kommt per Export aus der Strava-Web-App + Upload in der
  Trainingsapp; genau das erklärt der GPX-Reiter.

## Fallstricke

### Mehrbenutzer und Cloud-Sync
- **Zugriffsregeln liegen als `firestore.rules` im Repo, wirken aber erst nach dem
  Veröffentlichen in der Firebase-Konsole.** Die Datei allein schützt nichts.
- **Nie über Zeitstempel entscheiden, welcher Stand gewinnt.** Zwei Geräte messen an
  ihren eigenen Uhren; eines mit falscher Uhr wird unüberschreibbar. Maßgeblich ist
  `rev`, ein Zähler aus der Cloud (`trainingslog_sync_<uid>` im localStorage).
- **Einheiten werden vereinigt, nicht ersetzt** (`mergeStores`, Schlüssel ist `ts`).
  Wer Einheiten löscht, **muss** `tombstone(ts)` aufrufen — sonst holt der Merge sie
  vom anderen Gerät zurück. Betrifft `delSession`, `wipe` und beide Plan-Löschpfade.
- **`cloudSave` schreibt erst, wenn `cloudLoad` einmal geklappt hat.** Sonst ersetzt
  ein Fehlversuch beim Laden die ganze Historie durch den leeren Startspeicher.
  Ein Dokument ohne `rev` (Alt-Bestand) gilt als Erstkontakt und wird verschmolzen.
- **Erst auffrischen, dann hochladen.** Wer nach einem `cloudLoad` zuerst schreibt,
  lädt den un-vereinigten Arbeitsspeicher hoch und löscht die fremden Einheiten.
- **`_reloadStore` beim Nutzerwechsel, `_refreshStore` beim Auffrischen.** Ersteres
  setzt Bereich, Reiter und Entwürfe zurück (richtig bei Anmeldung), letzteres behält
  die Ansicht. Während einer laufenden Einheit oder offener Eingabe (`_hasActive`)
  wird gar nicht aufgefrischt.
- **Nichts, was nur einem Nutzer gehört, gehört in den Code.** Kursarten, Radarten
  und Trainingspläne liegen im Speicher des Nutzers; `PLAN` A/B ist Alt-Bestand und
  für neue Nutzer über `deleted` abgeschaltet.
- **Buchstaben für Krafteinheiten schließen die Bereichs-Kürzel aus** (`planLetters`
  filtert die `day`-Werte aus `ACT`). Ein Tag „L" fiele sonst aus `kraftDays()`.

### Sonstiges

- **`draft` beim Store-Wechsel zurücksetzen:** `_reloadStore` (Cloud-Load nach Login) muss `draft={}` setzen, sonst bleibt die Vorbelegung auf Standardwerten hängen.
- **Destruktive Aktionen erhalten Appearance/Prefs:** `wipe()` muss Farben (`accent*`), `mapStyle`, `bike`, `kursType`, `hiddenCats` bewahren und ein **vollständiges** Store-Objekt liefern (inkl. `schemes`, `plans`, `deleted`), sonst Crash in `dayLabel`.
- **Statusleiste am Home-Bildschirm:** `apple-mobile-web-app-status-bar-style`
  liest iOS **beim Hinzufügen** — Änderungen greifen erst, wenn man die App vom
  Home-Bildschirm entfernt und neu ablegt. Steht auf `black-translucent`, die
  Zeichen sind dort immer weiß; den Grund malt `.statusbar` selbst.
- **Darstellung:** Hell / Dunkel / System, gespeichert als `store.theme`. „System" hört
  per `matchMedia` live mit. Neben `theme-color` muss auch `color-scheme` am
  `<html>` mitziehen — sonst lässt Safari seine Leiste weiß, obwohl die App dunkel ist.
- **Dunkler Modus:** Flächen und Schriften laufen über Tokens (`--paper`, `--paper-2`,
  `--ink`, `--ink-soft`, `--ink-mute`, `--ink-faint`, `--line`, `--press`). `body.dark`
  definiert sie neu, der Grund ist `#252423` wie bei der dunklen Kreatur. **Nie Farben
  fest verdrahten** — `color:#fff` auf `var(--ink)` wird im Dunkeln unsichtbar, dafür
  gibt es `--on-ink`. Bereichsfarben (Kraft, Rad, …) bleiben in beiden Fassungen gleich.
- **Fokus-Umrandung** wird pro aktivem Bereich eingefärbt (`body.cat*`); Ausnahmen bei Bedarf per ID überschreiben (z. B. `#setOverlay` immer schwarz).
- **Google-Login: Popup-First ist der funktionierende Stand.** `signInWithPopup`
  läuft zuverlässig; `signInWithRedirect` bleibt nur außerhalb der installierten
  App (PWA) als Fallback. In der PWA bricht der Redirect in Safari mit
  „missing initial state" ab — dort zeigt die App stattdessen die Anleitung,
  in Safari anzumelden. Diese Popup-First-Reihenfolge nicht ändern, sonst bricht
  der Login ab.
- **`.nojekyll` ist Pflicht:** Ohne die Datei führt GitHub Pages Jekyll aus; der
  Build schlägt dann fehl und die **alte Version bleibt deployt** — man testet
  unbemerkt einen veralteten Stand. Nach einem Push im Browser checken, ob die
  deployte Seite den neuen Stand enthält.

## App-Icon (Stand der Entwürfe)

Entwürfe liegen als eigene Seiten in `entwuerfe/` (je eine pro Runde, alle mit
Artifact-Link in der Sitzung). Entschieden ist:

- **Motiv:** Mount Fuji. Profil wird **gerechnet, nicht gezeichnet** — konkave
  Potenzkurve mit weicher Kraterdelle (`entwuerfe/`-Bauskripte). Gekappte Gipfel
  mit aufgesetzter Beule geben harte Ecken, Bézier-Flanken fransen unten aus.
- **Form:** „Steiler" (Exponent 1.35, leichte Delle). Exponent > 1 = konkav wie
  der Fuji, = 1 gerade, < 1 wird zum Matterhorn.
- **Grund:** „Grat" — weißgrauer Verlauf, tiefblaue Wolke unten, Zeichen `#1F3A5C`.
- **Glas:** Liquid-Glass-Linse (eingerückt, harter Lichtsaum), nur fürs Icon.
  Die App selbst bleibt farblich schlicht — ein Glas-Umbau der ganzen App wäre
  wegen `backdrop-filter`-Last auf dem iPhone und der Lesbarkeit nicht ohne Risiko.
- **Gewählt: „Schnee als Umriss"** — Grat als Linie, die Schneegrenze als
  **offene** gezackte Linie darunter. Eine geschlossene Kappe legt ihre Oberkante
  ein zweites Mal auf den Grat (Doppellinie) und wirkt darunter gedrängt.
  Wenige, lange Zungen; viele kurze lesen sich als Gekritzel.
- **Dateien:** `apple-touch-icon.png` (180 px) und `apple-touch-icon-1024.png`,
  in `index.html` per `<link rel="apple-touch-icon">` eingehängt. Beide **ohne**
  runde Ecken — iOS rundet selbst. Gerendert wird mit Chromium/Playwright
  (`entwuerfe/`-Skript), weil `backdrop-filter` sich nicht in SVG rechnen lässt.
- **Verworfen, aber aufgehoben:** „Grundform", „Kontur mit Schnee", „Balkenberg"
  (sieben Balken, deren Höhe den Gipfel bildet) — alle in `entwuerfe/icon-auswahl.html`.
- **App-Name ist „Peak".** Auf dem Home-Bildschirm über `apple-mobile-web-app-title`
  (iOS liest es **beim Ablegen**), in der App als `.brand-title` und `.auth-title`.
- **Die Marke (`.mark`) ist eine Glaskachel, kein Buchstabe mehr.** Sie zeigt das
  Bergzeichen des Icons; die Initiale des Nutzers ist dort **entfallen** (wer angemeldet
  ist, steht in den Einstellungen). Der Grund bleibt in jedem Bereich hell — die
  Bereichsfarbe wird nur **beigemischt** (`--markc` + `color-mix` auf `--glass`),
  wie das Blau im App-Icon. Neue Bereichsfarbe heißt also: `--markc` setzen, nie
  `background` an `.mark` überschreiben. Die Ecken sind mit `border-radius:22.4%`
  gerundet — derselbe Anteil, den iOS den Icons auf dem Home-Bildschirm gibt.
- **`background-clip:text` schneidet Unterlängen ab.** Der Verlauf wird nur bis zur
  Kastenkante gemalt; ein „g" oder „y" verschwindet, wenn die Zeilenhöhe knapp ist.
  Gegenmittel: `padding-bottom` in em plus gleich großer negativer `margin-bottom`,
  damit die Anordnung gleich bleibt (`.hero-letter`, `.sess-badge`, `.sess-vol b`).
- **Farbige Flächen tragen den Lichtverlauf des Icons** (`--sheen`, als
  `background-image` **über** der Farbe, damit gewählte Akzentfarben durchschlagen).
  Wer eine farbige Fläche später umfärbt, nimmt `background-color`, nicht die
  Kurzform `background` — die löscht den Verlauf mit.

## User

Lennart lernt beim Bauen. Erklärungen dürfen kurz sein, aber Fachbegriffe kurz erläutern wenn sie zum ersten Mal auftauchen. Keine „junior-Warnungen" — direkte Kommunikation bevorzugt.

## CLAUDE.md pflegen

Alle 10 User-Anfragen einmal kurz nachfragen: „Soll ich etwas Neues in die CLAUDE.md aufnehmen — neue Konventionen, wiederkehrende Wünsche, oder Dinge, die diese Session gelernt hat?"

Zählen: Ab dem ersten Prompt der Session mitzählen; nach der Nachfrage Zähler zurücksetzen. Wenn Lennart nichts hinzufügen möchte, keine weiteren Vorschläge machen — einfach weiterarbeiten und in 10 Anfragen erneut fragen.
