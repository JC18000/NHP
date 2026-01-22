import json
import re
import pathlib


'''
What we want to do:
Split by \n
Remove the first 5 columns to prevent confusion with TIER 1, 2, and 3, and last column to make sure everything works nice
Remove first and last "|" pipe and split by pipe
Strip everything but the numbers (and negatives) to leave a list of 3 numbers (special case for 1/2, or mechs that are 1/2 OR 1)
Match each list with corresponding line item (Hull, Agility, Systems, etc.)
Convert to JSON and return
'''


def JSONifyTable(Mech, Table):
    # Handle special Size Cases (Size 1/2; Size 1/2 or 1)
    # Remeber, size is always the same between Tiers, so we can just detect if one or the other is there and then drop the row\
    SpecialSize = 0 # 0 for none
    if "1/2 or 1" in Table:
        SpecialSize = "1/2 or 1"
    elif "1/2" in Table:
        SpecialSize = "1/2"


    Table = Table.split("\n")

    Table = Table[6:19] # All stat tables are the same so we don't have to worry about it
    del Table[4] # Get rid of the row that says CORE STATS

    for x, Row in enumerate(Table):
        Table[x] = Row.split("|")

    for x, Row in enumerate(Table):
        Table[x] = [x for x in Row if x]

    # Table = [x for x in Table if x]
    for Row in Table:
        for x, Tier in enumerate(Row):
            if not "E-Defense" in Tier:
                Match = re.sub(r"[A-z :+]", "", Tier)
            else:
                Match = re.sub(r"[A-z :+-]", "", Tier)
            if SpecialSize != 0 and "Size" in Tier:
                Match = SpecialSize
            if Match:
                Row[x] = Match #.group(0)
    
    
    Categories = ["Hull", "Agility", "Systems", "Engineering", "HP", "Evasion", "Speed", "HeatCap", "Sensors", "Armor", "EDefense", "Size", "SaveTarget"]
    Schema = {
    Mech: {
        Category: [0, 0, 0] for Category in Categories
    }
    }
    for i, Row in enumerate(Table):
        for j, Value in enumerate(Row):
            Schema[Mech][Categories[i]][j] = int(Table[i][j].replace('–', '-')) # Betcha AI couldn't figure that one out

    '''
    for i, Row in enumerate(Table):
        for j, Category in enumerate(Categories):
            print(Category)
            print(j)
            print(Row)
            Schema[Mech][Category][j] = int(Table[i][j].replace('–', '-'))
    '''
    
    # .replace('–', '-')
    
    return Schema


Table = """+-----------------+-----------------+-----------------+
| TIER 1          |                 |                 |
| TIER 2          |                 |                 |
| TIER 3          |                 |                 |
+-----------------+-----------------+-----------------+
| MECH SKILLS     | MECH SKILLS     | MECH SKILLS     |
| Hull: –2        | Hull: –2        | Hull: –2        |
| Agility: +3     | Agility: +4     | Agility: +6     |
| Systems: +1     | Systems: +2     | Systems: +3     |
| Engineering: +0 | Engineering: +1 | Engineering: +1 |
| CORE STATS      | CORE STATS      | CORE STATS      |
| HP: 10          | HP: 12          | HP: 14          |
| Evasion: 12     | Evasion: 15     | Evasion: 18     |
| Speed: 5        | Speed: 6        | Speed: 7        |
| Heat Cap: 8     | Heat Cap: 8     | Heat Cap: 8     |
| Sensors: 10     | Sensors: 10     | Sensors: 10     |
| Armor: 0        | Armor: 0        | Armor: 0        |
| E-Defense: 8    | E-Defense: 8    | E-Defense: 10   |
| Size: 1         | Size: 1         | Size: 1         |
| Save Target: 10 | Save Target: 12 | Save Target: 14 |
+-----------------+-----------------+-----------------+
"""

Table = JSONifyTable("Ace", Table)
print(Table)


with open("Table.json", "w") as json_file:
    json.dump(Table, json_file, indent=4)

# Text = str(Table)
# pathlib.Path("TableOutput.txt").write_bytes(Text.encode()) # type: ignore