from pathlib import Path
p=Path(r"c:\Users\User\OneDrive\Documents\GitHub\Sweatbox-Creator\modules\ui\viewers\sweatbox_map.py")
lines=p.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines, start=1):
    if 1240 <= i <= 1300:
        print(f"{i:5d}: {line}")
