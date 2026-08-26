# Additive Creature

Zwei Fassungen der Animation von Julian Garnier
([CodePen](https://codepen.io/juliangarnier/pen/JojxjwB)), aufgehoben zum
späteren Einbau in den Trainingslog.

`creature.html` — eine einzige Datei, kein Netz nötig. Knöpfe unten schalten
zwischen den Fassungen; „Standbild" friert die Kreatur mittig ein. Die
Bedienelemente blenden nach 2,5 s Ruhe aus.

## Die beiden Fassungen

**Schwarz** — das Original unverändert.
Hintergrund `#252423`, `mix-blend-mode: plus-lighter`, Helligkeit 80 % (Mitte)
bis 20 % (Rand). Additives Mischen: überlappende Punkte addieren sich, der Kern
brennt zu Weiß aus.

**Weiß + Wolke** — Übersetzung auf hellen Grund.
Hintergrund `#ffffff`, `mix-blend-mode: multiply`, Helligkeit 38 % (Mitte) bis
86 % (Rand) — also umgekehrt. Statt nach außen zu glühen, verdichtet sie sich
nach innen zu Farbe.

Zwei Dinge waren dabei nötig, die das Original nicht braucht:

- **Weiche Verlaufspunkte** statt Vollkreise (`radial-gradient`, ab 58 %
  ausfadend). Die großen blassen Außenpunkte blieben sonst als Scheiben mit
  harter Kante stehen — auf Schwarz verschwinden sie, auf Weiß nicht.
- **Zurückgenommene Wolkenschichten** (.30/.38/.52 statt .42/.55/.75).
  `multiply` multipliziert sich bei Überlappung auf; zu satte Schichten klumpen
  dort zu harten dunklen Flecken.

## Aufbau der Datei

1. anime.js 4.5.0 vollständig eingebettet (`dist/bundles/anime.esm.min.js`).
   Einzige Änderung am Bündel: die `export{...}`-Anweisung am Ende wurde in ein
   Objekt `__ANIME__` umgeschrieben, weil `export` in einem Inline-Modul ins
   Leere läuft.
2. Der Original-Code des CodePen, wörtlich. Einzige Abweichung ist die erste
   Zeile — statt `import ... from 'https://esm.sh/animejs'` kommen die
   Funktionen aus `__ANIME__`.
3. Darunter die Zutaten dieser Seite: Farbfassungen, Standbild, fps-Anzeige.
   Die Bewegung ist davon unberührt.

Der angehängte Code liegt in einer eigenen Funktion — das minifizierte Bündel
belegt im selben Modul kurze Namen wie `f`, sonst kollidiert es.

## Größe

128 KB roh, 44 KB gzip. Davon ist praktisch alles die Bibliothek.
Zum Vergleich: `index.html` der App liegt bei 152 KB roh / 37 KB gzip.
