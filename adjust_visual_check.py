from pathlib import Path
p=Path('combat_detection.py');s=p.read_text().replace('gameplay=margin>.012','gameplay=margin>=0').replace("            if visual[label]['gameplay']:","            visual[label]['gameplay']=visual[label]['margin']>=0\n            if visual[label]['gameplay']:").replace('CLIP gameplay margin > 0.012','CLIP gameplay score >= menu/loading scores');p.write_text(s)
