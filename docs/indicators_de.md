# Indikatoren

## Kartierungssättigung

Berechnet die Sättigung der letzten 3 Jahre.
Der Zeitintervall beträgt einen Monat seit 2008.

Verschiedene statistische Modelle werden verwendet, um festzustellen, ob die Sättigung erreicht ist.

### Methoden und Daten

- Intrinsischer Ansatz

**Prämisse:**
Die Anzahl der hinzugefügten OSM-Objekte einer bestimmten Merkmalsklasse pro Zeitintervall nimmt ab, sobald die Anzahl der kartierten Objekte gegen die (unbekannte) tatsächliche Anzahl der Objekte konvergiert.

Jede Aggregation von Merkmalen (z. B. Länge von Straßen oder Anzahl von Gebäuden) hat ein Maximum. Nach erhöhter Kartierungsaktivität wird in der Nähe dieses Maximums die Sättigung erreicht.

### Limitationen
- Die Informativität variiert je nach Thema: Sie ist besser bei kleinen, diskreten Objekten (z. B. Häusern), aber schlechter bei großen 
Polygonen (z. B. Landnutzung), wo ein einziger abrupter Kartierungsschritt zu einer geringen Vollständigkeit führen kann.


### Referenzen

- Gröchenig S et al. (2014): *Digging into the history of VGI data-sets: results from a worldwide study on OpenStreetMap mapping activity*
  [DOI:10.1080/17489725.2014.978403](https://doi.org/10.1080/17489725.2014.978403)

- Barrington-Leigh C und Millard-Ball A (2017): *The world’s user-generated road map is more than 80% complete*
  [DOI:10.1371/journal.pone.0180698](https://doi.org/10.1371/journal.pone.0180698)

- Brückner J, Schott M, Zipf A, Lautenbach S (2021): *Assessing shop completeness in OpenStreetMap for two federal states in Germany*
  [DOI:10.5194/agile-giss-2-20-2021](https://doi.org/10.5194/agile-giss-2-20-2021)



## Vollständigkeit der Landbedeckung

Prozentualer Anteil der Gesamtfläche, der durch OpenStreetMap-Landbedeckungsdaten abgedeckt wird.

### Methoden und Daten

- **Intrinsischer Ansatz**

Das Verhältnis wird berechnet, indem die Gesamtfläche des Interessensgebiets durch die Summe der Flächen aller darin enthaltenen Landbedeckungspolygone geteilt wird.

### Limitationen

Überlappende OSM-Landbedeckungspolygone werden mehrfach gezählt und verbessern fälschlicherweise den Grad der 
Vollständigkeit der Landbedeckung.


## Thematische Genauigkeit der Landbedeckung

Thematische Genauigkeit der OpenStreetMap-Landbedeckungsdaten im Vergleich zum CORINE Land Cover (CLC)-Datensatz.
Dieser Indikator kann für mehrere oder eine einzelne CLC-Klasse(n) berechnet werden.

### Methoden und Daten
- **Extrinsischer Ansatz**

#### CORINE Land Cover
In seiner aktuellen Form bietet das [CORINE Land Cover (CLC)](https://land.copernicus.eu/en/products/corine-land-cover)-Produkt
ein paneuropäisches Landbedeckungs- und Flächennutzungsinventar mit 44 thematischen Klassen,
die von großen Waldgebieten bis hin zu einzelnen Weinbergen reichen.
CORINE verwendet eine 3-stufige Nomenklatur für Landbedeckungsklassen.
Hier verwenden wir das Produkt "CORINE Land Cover 5 ha, Stand 2021 (CLC5-2021)",
das vom Bundesamt für Kartographie und Geodäsie bereitgestellt wird und
nutzen die zweite Ebene der Nomenklatur (z.B. 1.1 Siedlungsflächen, 1.2 Industrie-, Gewerbe- und Verkehrsflächen).

### Vorverarbeitung:

OSM-Objekte werden basierend auf ihren Tags einer CLC-Klasse zugeordnet, wie unten spezifiziert.
Wir berechnen die Schnittmenge der OSM-Landbedeckungspolygone mit den CORINE-Landbedeckungspolygonen.
Die resultierenden Polygone enthalten sowohl die OSM-CLC-Klasse als auch die CORINE-Klasse.


| CLC (level 2)                                     | OSM tags                                                                                                                                                                                | 
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.1 Städtische geprägte Flächen                   | `landuse in (residential, retail)`                                                                                                                                                      |
| 1.2 	Industrie-, Gewerbe- und Verkehrsflächen     | `landuse in (industrial, commercial, port, railway, lock) or leisure in (marina)`                                                                                                       |
| 1.3 	Abbauflächen, Deponien und Baustellen        | `landuse in (quarry, construction, landfill, brownfield)`                                                                                                                               |
| 1.4 	Grünflächen                                  | `landuse in (recreation_ground, allotments, village_green, cemetery, grass) or leisure in (park, garden, pitch, golf_course, playground, stadium, recreation_ground, common, dog_park)` |
| 2.1 	Ackerland                                    | `landuse in (greenhouse_horticulture, greenhouse, farmland, farmyard)`                                                                                                                  |
| 2.2 	Dauerkulturen                                | `landuse in (vineyard, orchard)`                                                                                                                                                        |
| 2.3 	Grünland                                     | `landuse in (meadow)`                                                                                                                                                                   |
| 2.4 	Heterogene landwirtschaftliche Flächen       | *Für Klasse 2.4 gelten die meisten Tags, die für Klasse 2.1 genutzt werden. Daher wird Klasse 2.4 nicht zugewiesen.*                                                                    |
| 3.1 	Wälder                                       | `landuse in (forest) or natural in (wood)`                                                                                                                                              |
| 3.2 	Strauch- und Krautvegetation                 | `landuse in (greenfield) or natural in (grassland, scrub, heath, fell)`                                                                                                                 |
| 3.3 	Offene Flächen ohne/ mit geringer Vegetation | `natural in (beach, scree, shingle, bare_rock, sand, glacier, mud, glacier, rock, cliff, fill)`                                                                                         |
| 4.1 	Feuchtflächen im Landesinneren               | `natural in (wetland)`                                                                                                                                                                  |
| 4.2 	Feuchtflächen an der Küste                   | `landuse in (salt_pond)`                                                                                                                                                                |
| 5.1 	Wasserflächen im Landesinneren               | `natural in (water, pond) or landuse in (basin, reservoir)`                                                                                                                             |
| 5.2 	Meeresgewässer                                | *Meeresgewässer werden in OSM nicht kartiert. Daher wird Klasse 5.2 nicht zugewiesen.*                                                                                                  |

#### Indikatorberechnung:

Für das Interessensgebiet laden wir die Polygone aus dem Vorverarbeitungsschritt und schneiden sie zu.
Anschließend erstellen wir eine Konfusionsmatrix zwischen den OSM- und CORINE-Landbedeckungsklassen.
Diese Matrix dient als Grundlage für die Berechnung von Präzision, Recall und F1-Score.
Diese Berechnungen berücksichtigen die Fläche/Größe der Landbedeckungspolygone.

### Referenzen

- Schultz, Michael, Janek Voss, Michael Auer, Sarah Carter und Alexander Zipf. 2017.
  *„Open Land Cover from OpenStreetMap and Remote Sensing“*.
  International Journal of Applied Earth Observation and Geoinformation 63 (Mai): 206–13.
  [DOI:10.1016/j.jag.2017.07.014](https://doi.org/10.1016/j.jag.2017.07.014)

---

## Thematische Genauigkeit von Straßen

### Methoden und Daten
- **Extrinsischer Ansatz**

#### Basis-DLM

Das [Basis-DLM](https://mis.bkg.bund.de/trefferanzeige?docuuid=66656563-c818-4587-bde1-f4bed2787851) wird vom Bundesamt für Kartographie und Geodäsie (BKG) veröffentlicht und beschreibt die topographischen
Objekte der Landschaft und das Relief der Erdoberfläche in Vektorform. Die Objekte sind durch ihre räumliche Lage,
geometrischen Typ, beschreibende Attribute und Beziehungen zu anderen Objekten definiert.
Jedes Objekt besitzt eine bundesweit eindeutige Identifikationsnummer.
Die Straßen aus diesem Datensatz werden für diesen Indikator verwendet.

| Attribut            | OSM-Tag   | DLM-Attributspalte | Beschreibung                                             | 
|---------------------|-----------|--------------------|----------------------------------------------------------|
 | Name                | name, ref | NAM                | Der Name oder die Referenz der Straße.                   |
 | Oberflächenmaterial | surface   | OFM                | Das Material, aus dem die Oberfläche der Straße besteht. |
 | Fahrspuren          | lanes     | FSZ                | Die Anzahl der Fahrspuren einer Straße.                  |
 | Fahrbahnbreite      | width     | BRF                | Die Breite der Fahrbahn.                                 |
 | Fahrtrichtung       | oneway    | FAR                | Die Fahrtrichtung bei Einbahnstraßen.                    |

### Verarbeitung

OSM-Straßen und DLM-Straßen werden mit [map-matching-2](https://github.com/addy90/map-matching-2) unter Verwendung eines auf Markov-Entscheidungsprozessen basierenden Modells abgeglichen.
Für die abgeglichenen Straßen wird zunächst das Vorhandensein jedes Attributes in beiden Datensätzen überprüft. Falls die Attribute in beiden Datensätzen vorhanden sind, werden die Werte verglichen. Standardmäßig werden die Werte direkt verglichen, es gibt jedoch einige Ausnahmen:

#### Name

Für den Namen wurde die [Levenshtein-Distanz](https://de.wikipedia.org/wiki/Levenshtein-Distanz) berechnet. Die Namen wurden als übereinstimmend gewertet, wenn ihr Levenshtein-Ähnlichkeitswert über 0,85 lag.

#### Oberfläche

Für die Oberfläche werden OSM-Tags und DLM-Tags abgeglichen. Alle OSM-Tags, die nicht in der folgenden Tabelle aufgeführt sind, wurden als nicht übereinstimmend gewertet.

| DLM-Wert             | OSM-Tags                                                    |
|----------------------|-------------------------------------------------------------|
| Beton                | concrete                                                    |
| Bitumen, Asphalt     | asphalt                                                     |
| Pflaster             | paving_stones, sett, brick, cobblestone, unhewn_cobblestone |
| Gestein, zerkleinert | fine_gravel, gravel, sand, compacted, pebblestone           |

#### Fahrbahnbreite

For the width, a tolerance of 1 m was applied.
Für die Fahrbahnbreite wurde eine Toleranz von 1 m angewandt.

#### Fahrtrichtung

Um die Richtung der Straße zu überprüfen, wird der Vektor beider Geometrien berechnet. Wenn beide Vektoren das gleiche 
Vorzeichen aufweisen, wird dies als Übereinstimmung gewertet.

### Referenz

- A. Wöltche, *"Open source map matching with Markov decision processes: A new method and a detailed benchmark with existing approaches"*, Transactions in GIS, vol. 27, no. 7, pp. 1959–1991, Oct. 2023, doi: [10.1111/tgis.13107](https://onlinelibrary.wiley.com/doi/full/10.1111/tgis.13107).

## Attributvollständigkeit
Ermitteln Sie den Anteil der OSM-Features mit vorhandenen Attributen.

### Methoden und Daten

- Intrinsischer Ansatz

Berechnet den Prozentsatz der Features, die einen bestimmten Attributfilter enthalten. Es gibt vordefinierte
Attribute, Sie können jedoch auch eigene definieren.

### Limitationen
Es werden nur explizit gekennzeichnete Attribute berücksichtigt. Implizite Attribute wie die Geschwindigkeitsbegrenzung 
auf Wegen werden nicht berücksichtigt. Dieser Indikator hat für alle Attribute denselben Schwellenwert und erwartet ein
optimales Verhältnis von 100 % der Elemente, die über die angegebenen Attribute verfügen, was bei einigen Indikatoren
möglicherweise nicht der Fall ist.

## Gebäudevergleich
Vergleicht die Gesamtgebäudefläche von OSM mit der Gebäudefläche zweier Referenzdatensätze.

### Methoden und Daten
- Extrinsische Methode

Das Ergebnis ist das Verhältnis der Gesamtfläche der Gebäude in OSM geteilt durch die Gesamtfläche der Gebäude im Referenzdatensatz.

Referenzdatensätze:
- [EUBUCCO](https://docs.eubucco.com/): Europaweite Gebäudeflächen, abgeleitet aus Verwaltungsdatensätzen
- [Microsoft Buildings](https://planetarycomputer.microsoft.com/dataset/ms-buildings): Weltweite Gebäudeflächen, abgeleitet aus Satellitenbildern unter Verwendung von maschinellem Lernen

### Limitationen
- Vergleicht nur die Gesamtquadratmeter der Gebäudepolygone von OSM und dem Referenzdatensatz, nicht die tatsächliche Überlappung
- Keine Qualitätsbewertung des Referenzdatensatzes. OSM spiegelt die reale Welt möglicherweise genauer wider als die Referenzdaten.


## Aktualitätsindikator

Der Aktualitätsindikator misst, wie aktuell OSM-Elemente sind, indem er die Verteilung 
ihrer jüngsten Beiträge analysiert. Er bewertet die Aktualität von Geometrie- und Tag-Bearbeitungen (ohne Löschungen) und klassifiziert
Features anhand der Zeit seit ihrer letzten Aktualisierung in Qualitätsstufen.
Alle Beiträge seit 2008 werden berücksichtigt und in monatlichen Intervallen aggregiert. Jedes Objekt wird einer Qualitätsklasse zugeordnet,
 je nachdem, wann es zuletzt bearbeitet wurde. Die Schwellenwerte werden in Monaten relativ zum aktuellen Datum definiert und 
dienen dazu, zwischen hochaktuellen, mittelmäßig aktuellen und veralteten Objekten zu unterscheiden.
Für jede Objektklasse wird der relative Anteil der Beiträge berechnet, die in diese Aktualitätsklassen fallen. Basierend auf 
diesen Anteilen wird eine Gesamtaktualitätsklasse zugewiesen.

### Methoden und Daten
– intrinsischer Ansatz.


**Prämisse**:
Der Zeitstempel der letzten Bearbeitung spiegelt wider, wie gut ein Feature die aktuellen realen Bedingungen 
repräsentiert. Kürzlich aktualisierte Merkmale sind mit größerer Wahrscheinlichkeit korrekt und aktuell, während 
Merkmale, die über einen längeren Zeitraum nicht bearbeitet wurden, mit höherer Wahrscheinlichkeit veraltet sind.

### Limitationen

- Die Aktualität der Bearbeitungen garantiert nicht unbedingt die Richtigkeit oder thematische Genauigkeit.
- Einige Merkmale sind möglicherweise korrekt, wurden jedoch über einen längeren Zeitraum nicht geändert und werden 
daher als veraltet eingestuft.
- Die Kartierungsaktivität variiert stark zwischen Merkmalsklassen und Regionen.
- Die Wahl der Schwellenwerte für die Zeitstempel beeinflusst die Klassenzuordnung und Vergleichbarkeit.


## Straßenvergleich
Vergleicht das Straßennetz von OSM mit dem eines Referenzdatensatzes.
Das Ergebnis ist das Verhältnis der Länge der Referenzstraßen, die von OSM-Straßen abgedeckt werden, zur Gesamtlänge der
Referenzstraßen.

### Methoden und Daten
- Extrinsische Methode

Identifiziert entsprechende Straßengeometrien in OSM und dem Referenzdatensatz, um das Verhältnis der übereinstimmenden 
Straßenlänge zu berechnen.


Referenzdatensatz: 
- [Microsoft Roads](https://github.com/microsoft/RoadDetections): Weltweiter Datensatz von Straßen, abgeleitet aus 
Satellitenbildern unter Verwendung von maschinellem Lernen

### Limitationen
– Keine Qualitätsbewertung des Referenzdatensatzes. OSM spiegelt die reale Welt möglicherweise genauer wider als die Referenzdaten.


## Nutzeraktivität
Berechnet, wie viele einzelne Benutzer zu einem bestimmten Thema beigetragen haben, gruppiert nach Monaten.


### Methoden und Daten
– intrinsische Methode

Die monatliche Anzahl der einzelnen Nutzer, die ein bestimmtes Thema im Interessengebiet bearbeitet haben, wird für den gesamten Zeitraum von OSM ermittelt.
Zusätzlich werden der Medianwert der letzten drei Jahre sowie eine Regressionsgerade berechnet, um die aktuelle Tendenz der Nutzeraktivität zu ermitteln.

### Limitationen
- Gibt keine Auskunft über die Datenqualität an sich, kann jedoch zusätzlich zu anderen Indikatoren verwendet werden.
