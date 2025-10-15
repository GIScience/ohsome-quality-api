# README

## Usage
```
python generate_hurl_files.py
hurl --jobs=1 --repeat 1 indicator-building-count-rhineland-palatinate-ohsomedb.hurl
```

## Results

| Indicator   | Topic             | Region               | Requests | ohsome API [s] | ohsome DB [s] |
| --          | ---               | ---                  | ---      | ---            | ---           |
| Currentness | Buildings (count) | Heidelberg           | 1        | 12             | 0.9           |
| Currentness | Buildings (count) | Heidelberg           | 10       | 29             | 2.8           |
| Currentness | Buildings (count) | Heidelberg           | 100      | 240            | 25            |
| Currentness | Buildings (count) | Frankfurt            | 1        | 49             | 1.3           |
| Currentness | Buildings (count) | Frankfurt            | 10       | 96             | 4             |
| Currentness | Buildings (count) | Frankfurt            | 100      | 693            | 31            |
| Currentness | Buildings (count) | Rhineland-Palatinate | 1        | 37             | 3.5           |
| Currentness | Buildings (count) | Rhineland-Palatinate | 10       | 83             | 19            |
| Currentness | Buildings (count) | Rhineland-Palatinate | 100      | 656            | 149           |
| Currentness | Roads (length)    | Heidelberg           | 1        | 6              | 0.8           |
| Currentness | Roads (length)    | Heidelberg           | 10       | 10             | 3             |
| Currentness | Roads (length)    | Heidelberg           | 100      | 50             | 22            |
| Currentness | Roads (length)    | Frankfurt            | 1        | 16             | 0.9           |
| Currentness | Roads (length)    | Frankfurt            | 10       | 22             | 3             |
| Currentness | Roads (length)    | Frankfurt            | 100      | 160            | 26            |
| Currentness | Roads (length)    | Rhineland-Palatinate | 1        | 71             | 3             |
| Currentness | Roads (length)    | Rhineland-Palatinate | 10       | 113            | 17            |
| Currentness | Roads (length)    | Rhineland-Palatinate | 100      | 761            | 124           |
