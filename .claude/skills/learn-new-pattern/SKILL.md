---
name: learn-new-pattern
description: Analyze a reference image of an Islamic geometric pattern, iteratively replicate it using the sacred-patterns library, and produce D3.js, GeoGebra, and declarative pattern outputs.
user_invocable: true
argument: image_path - Path to a reference image (jpg/png) of a geometric pattern
---

# learn-new-pattern

Analyze a reference image of an Islamic geometric pattern, iteratively replicate it, extend the library as needed, and generate multiple output formats — with user feedback at each step.

## Invocation

```
/learn-new-pattern /path/to/image.jpg
```

The user provides just an image path. The skill handles everything else.

## Workflow

### Step 1: Initialize Session

1. Read the reference image at the provided path
2. Auto-generate a session name from initial visual impression (e.g., `8-fold-rosette`, `12-fold-medallion`) — or ask the user if ambiguous
3. Create session folder at `/Users/omareid/Dropbox/Data/sacred-patterns/session-{name}/`
4. Create the full directory structure:
   ```
   session-{name}/
     input/
       reference.{ext}
     analysis.md
     construction.md
     pattern.json
     iterations/
     final/
     dashboard.html
     session.json
     learnings.md
   ```
5. Copy the reference image to `input/reference.{ext}`
6. Initialize `session.json` with status `in-progress`
7. Load cross-session learnings from `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/`

### Step 2: Analyze Pattern

Follow the instructions in `analysis-guide.md` to analyze the reference image.

1. Examine the image carefully for all geometric, chromatic, and structural features
2. Write `analysis.md` covering:
   - Symmetry type and group
   - Base polygon and star pattern ({n/k} notation)
   - Tiling method
   - Construction geometry with normalized radii
   - Tile shapes and angles
   - Interlace/strapwork details
   - Color palette with hex codes
   - Programmatic construction steps
3. Write `construction.md` with normalized, algorithmic construction steps
4. Present the analysis to the user for review before proceeding
5. Consult `learnings/common-mistakes.md` to avoid known pitfalls

### Step 3: Generate Pattern Definition

1. Read `declarative-language-guide.md` for the pattern.json format
2. Translate the analysis into a `pattern.json` declarative definition
3. The definition should capture all layers of the pattern using available primitives
4. Save to the session root as `pattern.json`

### Step 4: Iteration Loop

Follow `iteration-guide.md` for the detailed iteration workflow.

For each iteration (max 5 before asking user):

**a) Compile** — Translate `pattern.json` to a self-contained D3.js v7 HTML file following `compile-d3.md`

**b) Render & Capture** — Open HTML in browser via `mcp__chrome-devtools__navigate_page` or `mcp__claude-in-chrome__navigate`, take screenshot

**c) Evaluate** — Compare screenshot to reference on structured criteria:
- Symmetry order match
- Element count (stars, polygons, rosettes)
- Radial proportions
- Interlace/strapwork
- Color palette accuracy
- Each scored: MISSING / PARTIAL / PRESENT / ACCURATE

**d) Retrospect** — When criteria score MISSING or PARTIAL:
- Re-examine the reference image focusing on the failing area
- Compare what `analysis.md` says vs what was rendered
- Identify misinterpretations
- Update `analysis.md` and `construction.md` with corrections
- Record in `iterations/{nn}/retrospective.md`

**e) Update** — Apply corrections to `pattern.json`

**f) Library Check** — If a primitive is missing, follow `library-extension-guide.md` to auto-create it, run `make compile`, and document in `iterations/{nn}/library-changes.md`

**g) Decide**:
- Confidence >= 0.85 with no MISSING → complete
- Confidence >= 0.70 → ask user
- Otherwise → iterate with corrections
- Max 5 iterations → ask user

### Step 5: Finalize

1. Copy best iteration to `final/`:
   - `pattern.json` — final declarative definition
   - `output.html` — self-contained D3.js HTML
   - `output.svg` — extracted SVG
2. Generate GeoGebra outputs following `geogebra-guide.md`:
   - `pattern.ggb` — GeoGebra archive
   - `geogebra-script.txt` — paste-in script
3. Generate `dashboard.html` following `dashboard-guide.md`
4. Update `session.json` with final status, confidence, etc.
5. Update `learnings.md` with session-specific insights

### Step 6: Deploy

1. Update cross-session learnings in `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/`:
   - Add to `patterns-catalog.md`
   - Log any library extensions in `library-extensions-log.md`
   - Add discovered palettes to `color-palettes-learned.md`
   - Add reusable techniques to `construction-techniques.md`
   - Add mistakes to `common-mistakes.md`
2. If user approves, run gallery build and `make deploy`

### Step 7: Present Results

1. Show the final output alongside the reference image
2. Provide file paths to all outputs
3. Show iteration journey (how many iterations, what was corrected)
4. Collect user feedback
5. If feedback requires changes, return to Step 4

## Session Isolation Rules

- Each session is fully self-contained — it NEVER reads from other session folders
- The only shared state is `learnings/` which is read at startup
- The skill does NOT compare against other sessions' outputs unless explicitly asked
- Combining patterns from multiple sessions requires explicit user request

## Session Folder Structure

```
session-{name}/
  input/                        # User-provided reference material
    reference.{jpg,png}         # Primary reference image
    notes.md                    # Optional user notes
  analysis.md                   # Pattern analysis (updated by retrospective loop)
  construction.md               # Normalized construction steps
  pattern.json                  # Declarative pattern definition (canonical)
  iterations/
    01/
      pattern.json              # Pattern definition for this iteration
      output.html               # Self-contained D3.js v7 HTML
      screenshot.png            # Browser screenshot of output
      evaluation.md             # Structured comparison vs reference
      retrospective.md          # WHY did analysis lead to wrong output?
      guidance.md               # What to change next
      library-changes.md        # Any TS library changes
    02/ ...
  final/
    pattern.json                # Final declarative definition
    output.html                 # Best iteration's HTML (self-contained)
    output.svg                  # Exported SVG
    pattern.ggb                 # GeoGebra archive
    geogebra-script.txt         # GeoGebra Classic paste-in script
  dashboard.html                # Self-contained session journey visualization
  session.json                  # Machine-readable session metadata
  learnings.md                  # Session-specific learnings
```

## session.json Schema

```json
{
  "name": "session-name",
  "status": "in-progress | completed | paused",
  "created": "ISO-8601 timestamp",
  "updated": "ISO-8601 timestamp",
  "pattern_type": "rosette | medallion | tessellation | ...",
  "symmetry_group": "D8 | D12 | ...",
  "symmetry_order": 8,
  "current_iteration": 1,
  "best_iteration": 1,
  "confidence_score": 0.0,
  "library_extensions": [],
  "color_palette": {
    "name": "palette name",
    "colors": {}
  },
  "tags": [],
  "reference_image": "input/reference.jpg"
}
```

## Guide Files

All guide files are in this skill directory:

| File | Purpose |
|------|---------|
| `analysis-guide.md` | How to analyze a reference image |
| `color-palettes.md` | Traditional Islamic art color palettes |
| `declarative-language-guide.md` | Pattern.json format and layer types |
| `compile-d3.md` | How to compile pattern.json to D3.js HTML |
| `compile-geogebra.md` | How to compile pattern.json to GeoGebra |
| `iteration-guide.md` | Core iteration workflow with retrospective loop |
| `library-extension-guide.md` | When/how to extend src/ts/ |
| `geogebra-guide.md` | GeoGebra script + .ggb generation |
| `dashboard-guide.md` | Per-session dashboard and gallery generation |

## Related Skills

- `/analyze-geometric-patterns` — Standalone image analysis (no iteration)
- `/generate-drawing` — Creative pattern composition from learned primitives
