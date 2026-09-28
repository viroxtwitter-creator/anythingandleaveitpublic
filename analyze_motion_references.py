"""Extract readable Fusion settings and motion summaries from DRP references."""
import collections,json,re,struct,zipfile,zlib
from pathlib import Path
import xml.etree.ElementTree as ET
from review_core import save_json

ROOT=Path(__file__).resolve().parent

def frame_value(value):
    if not value:return 0
    whole,_,fraction=value.partition('|')
    return int(whole)+(struct.unpack('<d',bytes.fromhex(fraction))[0] if fraction else 0)

def inflate_stream(blob):
    """Resolve wraps a textual Fusion comp in one or more zlib records."""
    pending=[blob];seen=set();texts=[]
    while pending:
        data=pending.pop()
        for match in re.finditer(b'\x78[\x01\x5e\x9c\xda]',data):
            try:expanded=zlib.decompress(data[match.start():])
            except zlib.error:continue
            key=hash(expanded)
            if key in seen:continue
            seen.add(key);pending.append(expanded)
            decoded=expanded.decode('utf-8','ignore')
            if ('Composition {' in decoded or 'Tools = ordered()' in decoded
                    or decoded.lstrip('\x00').startswith('{')):texts.append(decoded)
    # A saved composition contains separate compressed records for UI state and
    # the actual tool graph. Keep every readable record so the graph is not
    # accidentally discarded in favour of the larger UI-state block.
    return '\n'.join(texts)

def classify(name,text,kind):
    tools=collections.Counter(re.findall(r'\b(?:[A-Za-z][A-Za-z0-9_]*)\s*=\s*([A-Za-z][A-Za-z0-9_]*)\s*\{',text))
    lower=(name+' '+text).lower()
    if kind=='transition':category='transition'
    elif tools['Transform'] or 'size = input' in lower:category='zoom/transform'
    elif tools['TextPlus']:category='text'
    elif any(tools[x] for x in ('RectangleMask','EllipseMask','PolygonMask')):category='masked graphic'
    else:category='other fusion'
    keyframes=[]
    for spline,body in re.findall(r'(\w+)\s*=\s*BezierSpline\s*\{(.*?)\n\s*\},',text,re.S):
        points=[(float(t),float(v)) for t,v in re.findall(r'\[(-?[\d.]+)\]\s*=\s*\{\s*(-?[\d.]+)',body)]
        if points:keyframes.append(dict(spline=spline,points=points[:12]))
    return category,dict(tools),keyframes

def analyse(project):
    with zipfile.ZipFile(project) as archive:
        files=[n for n in archive.namelist() if n.endswith('.xml')]
        roots=[]
        for filename in files:
            raw=archive.read(filename)
            if b'<VideoTrackVec>' not in raw:continue
            roots.append((filename,ET.fromstring(re.sub(rb'(<\/?\w+)::',rb'\1__',raw))))
        # The main edit has the largest timeline item collection.
        filename,root=max(roots,key=lambda x:len(list(x[1].iter('Sm2TiVideoClip')))+len(list(x[1].iter('Sm2TiTransition'))))
        rows=[]
        for kind,tag in [('clip','Sm2TiVideoClip'),('transition','Sm2TiTransition')]:
            for item in root.iter(tag):
                name=item.findtext('Name') or ''
                for index,field in enumerate(item.iter('CompositionBA'),1):
                    if not field.text:continue
                    text=inflate_stream(bytes.fromhex(field.text))
                    category,tools,keyframes=classify(name,text,kind)
                    rows.append(dict(kind=kind,name=name,start_frame=frame_value(item.findtext('Start')),
                        duration_frames=frame_value(item.findtext('Duration')),composition=index,
                        category=category,tools=tools,keyframes=keyframes,
                        has_size_animation='Size = Input { SourceOp' in text,
                        has_center_animation='Center = Input { SourceOp' in text))
    return dict(project=project.name,sequence=filename,items=rows,
        categories=dict(collections.Counter(r['category'] for r in rows)),
        named_effects=collections.Counter(r['name'] for r in rows).most_common())

def main():
    reports=[analyse(p) for p in sorted(ROOT.glob('*.drp'))]
    out=ROOT/'analysis/editing-style/motion-reference-report.json';save_json(out,dict(references=reports))
    for report in reports:
        print(report['project'],report['categories'])
        print(' ',report['named_effects'][:12])
        zooms=[r for r in report['items'] if r['category']=='zoom/transform']
        print(' ',len(zooms),'zoom/transform comps;',sum(bool(r['keyframes']) for r in zooms),'with readable splines')

if __name__=='__main__':main()
