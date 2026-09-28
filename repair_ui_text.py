from pathlib import Path
for name in ['automatic_review.py','automatic_cut.py','automatic_sfx.py']:
 p=Path(name);s=p.read_text(encoding='utf-8')
 for char in ['—','…','→','·','’']:
  bad=char
  variants=[]
  for i in range(3):
   try:bad=bad.encode('utf-8').decode('cp1252');variants.append(bad)
   except UnicodeError:break
  for bad in reversed(variants):s=s.replace(bad,char)
 p.write_text(s,encoding='utf-8')
