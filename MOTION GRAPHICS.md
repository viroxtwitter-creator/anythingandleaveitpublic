# Motion graphics possibilities

The safest first layer is graphics driven by information the app already knows. Each item should be created on a separate, editable Resolve track and remain optional.

## What the supplied examples actually use

- Gameplay and desktop clips frequently use **ResolveFX Transform inside Fusion**, with animated Bezier splines rather than Edit-page sizing.
- The sampled MW4 push zoom uses three zoom values: **1.000 → 1.186 → 1.367**, with most of the movement easing through the latter part of the clip.
- Short **CameraShake** adjustment clips recur in all three examples. Rainbow Six/Fortnite commonly use roughly 22–26 frames; MW4 commonly uses roughly 27–41 frames.
- **Box Wipe** appears throughout all three projects. **Brightness Flash** appears at openings, and **Flip 3D** is used occasionally rather than as a default transition.
- Text treatments repeatedly combine Text+, SoftGlow, ResolveFX Transform and Waviness. Fortnite also commonly adds DropShadow.

The first automated motion feature now uses the measured MW4 Fusion zoom curve on transcript-confirmed emphasis and reaction clips. It is capped and spaced, and each generated composition is named **AUTO - Jordan punch zoom**.

## Good first features

- **Emphasis captions:** briefly enlarge or recolour one important caption word on strong spoken reactions.
- **Punch-in zooms:** a short 105–115% camera push on a reveal, surprise, or punchline, with a smooth return.
- **Chapter cards:** simple title cards when a long source jump begins a clearly new section.
- **Callouts:** arrows, circles, or labels when speech contains cues such as “right there,” “look at this,” or “top left.” These should be suggestions until the object position can be verified.
- **Counters and stat cards:** animate a number or short label after phrases such as “three kills,” “level 20,” or “£50.” The extracted text should stay editable.
- **Freeze-frame emphasis:** a very short freeze with a border, caption, and impact sound for a confirmed punchline or reaction.

## Possible after visual understanding improves

- Track a player, enemy, UI item, or cursor and attach a label to it.
- Automatically crop horizontal footage into vertical video while following the important subject.
- Detect confirmed kills, wins, unlocks, purchases, and scoreboard changes before adding event-specific graphics.
- Build recurring branded lower thirds, scoreboards, progress bars, and end cards from reusable Fusion templates.

## Recommended order

1. Punch-in zooms and emphasis captions: useful, reversible, and based on existing timing.
2. Chapter cards and editable stat cards: require reliable phrase extraction but not object tracking.
3. Callout suggestions: only place automatically after screen-position validation exists.
4. Tracking and event-confirmed graphics: highest payoff, but needs stronger visual detection and more testing.

Avoid covering the crosshair, subtitles, minimap, health, or other game HUD. Limit simultaneous motion, reserve large animations for genuine highlights, and keep every generated element removable in Resolve.
