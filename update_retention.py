from pathlib import Path
p=Path('automatic_cut.py');s=p.read_text();a=s.index('def select_ranges(');b=s.index('\ndef plan(',a)
s=s[:a]+'''def select_ranges(transcript,events,duration):
    from dialogue_cut import clean_dialogue,subtract
    speech,exclusions,duplicates=clean_dialogue(transcript,duration)
    kept=join_near(speech+events,duration,.10)
    words=[w for seg in transcript for w in seg['words'] if 0<w['end']-w['start']<3]
    for r in kept:
        for w in words:
            if w['start']<r[0]<w['end']:r[0]=max(0,w['start']-.09)
            if w['start']<r[1]<w['end']:r[1]=min(duration,w['end']+.12)
    # Subtract last: combat cannot put an abandoned take back into the edit.
    return subtract(join_near(kept,duration,.10),exclusions),speech,duplicates
''' +s[b:]
a=s.index("    check();progress('Finding action");b=s.index('\nFUSCRIPT=',a)
s=s[:a]+'''    check();progress('Checking shooting and filtering menus/loading…')
    game=next((i for i,n in enumerate(names) if i!=mic and ('system' in n.lower() or 'game' in n.lower())),next((i for i in range(len(names)) if i!=mic),None))
    events=[];checks={'method':'No separate game track; commentary only'}
    if game is not None:
        from combat_detection import detect
        wav=ROOT/'analysis'/f'action-audio-{key}-{game}.wav'
        if not wav.is_file():extract(source,game,0,duration,wav)
        check()
        events,checks=detect(source,wav,f'{key}-{game}',duration,progress,cancel)
    check();progress('Tightening speech and removing repeated takes…')
    kept,speech,duplicates=select_ranges(transcript,events,duration)
    if not kept:raise ValueError('No clear commentary or shooting was found. Check the voice-track selection.')
    kept=[[round(a*fps)/fps,min(duration,round(b*fps)/fps)] for a,b in kept if round(b*fps)>round(a*fps)]
    return dict(source=str(source),duration=duration,fps=fps,kept=kept,
                speech=speech,action=events,microphone=mic,game_audio=game,
                duplicate_takes=len(duplicates),removed_duplicates=duplicates,combat_checks=checks,
                target_duration=None,
                selection_method='Tight microphone word timing, conservative nearby retake removal, classified gunfire with sampled visual menu/loading veto. No target duration; not full narrative understanding.')
''' +s[b:]
s=s.replace('Speech boundaries and game-audio transients generate editable selections. Reference\nshot durations calibrate action handles; this is not semantic gameplay recognition.','Tight speech, conservative retakes and classified gunfire with visual screen checks.')
s=s.replace('Automatically selected commentary and game-audio activity.','Tightened commentary, nearby retake removal and visually screened gunfire.')
p.write_text(s,encoding='utf-8')
p=Path('dialogue_cut.py');s=p.read_text().replace("w['start']-groups[-1][-1]['end']>.65 or", "w['start']-groups[-1][-1]['end']>.65 or (token(w)=='so' and len(groups[-1])>=5 and w['start']-groups[-1][-1]['end']>.3) or");p.write_text(s)
p=Path('automatic_review.py');s=p.read_text();a=s.index("self.details=QLabel(");b=s.index(';self.details.setWordWrap',a);s=s[:a]+"self.details=QLabel('Cuts close to your voice, removes nearby repeated takes, and checks shooting against the picture to filter silent menus/loading.\\n\\nVaried effects from Desktop/SFX follow cuts and spoken cues. All sounds stay editable on separate tracks.')"+s[b:];p.write_text(s,encoding='utf-8')
