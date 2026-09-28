"""Automatic Resolve subtitles followed by the installed Snap Captions converter."""
from pathlib import Path
import unicodedata
from app_paths import ROOT
PLUGIN=Path.home()/'AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Comp/Snap Captions.lua'

def lua_for_captions(microphone):
    if not PLUGIN.is_file():raise ValueError('Snap Captions is missing. Install it or turn off automatic captions.')
    bridge=(ROOT/'caption_bridge.lua').read_text(encoding='utf-8-sig')
    ranges=[]
    for cp in range(0x110000):
        if unicodedata.category(chr(cp)).startswith('P'):
            if ranges and cp==ranges[-1][1]+1:ranges[-1][1]=cp
            else:ranges.append([cp,cp])
    bridge=bridge.replace('PUNCTUATION_RANGES',','.join('{'+str(a)+','+str(b)+'}' for a,b in ranges))
    return '\n'+bridge.replace('SNAP_PLUGIN_PATH',PLUGIN.as_posix()).replace('MICROPHONE_TRACK',str(microphone+1))+'\n'
