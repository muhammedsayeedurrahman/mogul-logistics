import os

FILE_PATH = "c:/code/openenv/server/training_viz.py"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('_GREEN = "#00e676"', '_GREEN = "#2B7D6D"')
content = content.replace('_BLUE = "#40c4ff"', '_BLUE = "#0668E1"')
content = content.replace('_ORANGE = "#ff9100"', '_ORANGE = "#EE4C2C"')
content = content.replace('#1e3a5f', '#404040')
content = content.replace('#7a8ea0', '#666666')
content = content.replace('linear-gradient(135deg,#0d2137,#162332)', 'linear-gradient(135deg,#1c1c1c,#262626)')

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
