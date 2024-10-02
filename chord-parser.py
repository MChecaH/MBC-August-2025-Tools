from reamber.osu.OsuMap import OsuMap
from zipfile import ZipFile
from datetime import timedelta
import os
import pandas as pd
import math

class Columna:
    def __init__(self) -> None:
        self.status = 0
        self.endhold = 0
    
    def ends_at(self, offset):
        self.status = 1
        self.endhold = offset
    
    def update_status(self, offset):
        if self.endhold < offset:
            self.status = 0
    
    def __repr__(self):
        return str(self.status)

def notes_held(cols, offset):
    held = 0
    for col in cols:
        col.update_status(offset)
        held += col.status
    return held

def validate(notes, max_holds):
    status = True
    cols = [Columna(), Columna(), Columna(), Columna(), Columna(), Columna(), Columna()]
    for _, note in notes.iterrows():
        # print(cols, getTimestamp(note['offset']))
        if math.isnan(note['length']):
            cols[note['column']].ends_at(note['offset'])
        else:
            cols[note['column']].ends_at(note['offset'] + note['length'] - 1)
        if notes_held(cols, note['offset']) > max_holds:
            print(f"BIG CHORD @ osu://edit/{getTimestamp(note['offset'])} ({int(note['offset'])}|0)")
            status = False
    return status

def getTimestamp(ms):
    milliseconds = str(int(ms % 1000))
    seconds = str(int((ms / 1000) % 60000) % 60) 
    minutes = str(int(((ms / 1000) % 60000) / 60))

    return f"{minutes.rjust(2, "0")}:{seconds.rjust(2, "0")}:{milliseconds.rjust(3, "0")}"

INPUT_DIRECTORY = os.path.dirname(__file__) + "/input"
os.chdir(INPUT_DIRECTORY)

for beatMapSet in os.listdir(INPUT_DIRECTORY):
    print(beatMapSet)
    with ZipFile(beatMapSet, 'r') as zip:
        for file in zip.namelist():
            if file.endswith(".osu"):
                print("Now checking:      " + file)
                zip.extract(file)

                map = OsuMap.read_file(file)

                notes = pd.concat([map.holds.df, map.hits.df]).sort_values(by="offset")
                print("HOLD COUNT:      ", map.holds.offset.size, " | HITS COUNT:        ", map.hits.offset.size)
                if not validate(notes, 2 if map.circle_size == 4.0 else 3):
                    print(f"Map is invalid: {file}")
                os.remove(file)