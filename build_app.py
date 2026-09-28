import sys
from pathlib import Path
root=Path(__file__).resolve().parent
dist_dir=sys.argv[1] if len(sys.argv)>1 else '.app'
sys.path.insert(0,str(root/'.runtime-deps'))
from PyInstaller.__main__ import run
run([str(root/'packaged_entry.py'),'--hidden-import','automatic_review','--name','CutReview','--onedir','--windowed','--noconfirm',
     '--distpath',str(root/dist_dir),'--workpath',str(root/'.build-user'),'--specpath',str(root/'.build-user'),
     '--paths',str(root/'.runtime-deps'),'--hidden-import','configparser','--exclude-module','faster_whisper',
     '--exclude-module','matplotlib','--exclude-module','scipy','--exclude-module','pandas',
     '--exclude-module','tkinter','--exclude-module','IPython','--exclude-module','pytest',
     '--exclude-module','automatic_sfx','--exclude-module','automatic_motion','--exclude-module','automatic_captions'])
