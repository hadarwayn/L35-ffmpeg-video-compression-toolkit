# Product Requirements Document (PRD)

## L35 — Advanced Video Compression Analysis & Visualization Toolkit

**Version:** 1.0
**Date:** February 2026
**Course:** AI Developer Expert — Dr. Yoram Segal
**Author:** Hadar

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Educational Background — Video Compression Theory](#2-educational-background)
3. [Target Users & Applications](#3-target-users--applications)
4. [Input & Output Specification](#4-input--output-specification)
5. [Task 1 — Video Statistics & Metadata Extraction](#5-task-1--video-statistics--metadata-extraction)
6. [Task 2 — Motion Vector & Macroblock Visualization](#6-task-2--motion-vector--macroblock-visualization)
7. [Task 3 — Moving & Rotating Rectangle Overlay](#7-task-3--moving--rotating-rectangle-overlay)
8. [Technical Requirements](#8-technical-requirements)
9. [Directory Structure](#9-directory-structure)
10. [Performance Requirements](#10-performance-requirements)
11. [Security & Configuration](#11-security--configuration)
12. [README & Documentation Strategy](#12-readme--documentation-strategy)
13. [Learning Objectives Matrix](#13-learning-objectives-matrix)
14. [Success Criteria & Acceptance Tests](#14-success-criteria--acceptance-tests)
15. [Assumptions & Constraints](#15-assumptions--constraints)
16. [Future Extensions](#16-future-extensions)
17. [References](#17-references)
18. [Phase Gate](#18-phase-gate)

---

## 1. Project Overview

### Project Name
**L35 — Advanced Video Compression Analysis & Visualization Toolkit**

### One-Line Description
A professional-grade, FFmpeg-centric video analysis and manipulation toolkit that exposes the inner workings of H.264/AVC compression through metadata extraction, motion vector visualization, and controlled pixel-level editing of compressed video streams.

### Problem Statement
Modern video codecs (H.264/AVC) achieve remarkable compression ratios through a combination of spatial transforms (DCT), temporal prediction (motion vectors), and structured frame dependencies (GOPs). For most people, these mechanisms remain a "black box" — you can compress a video, but you cannot *see* how the codec makes its decisions.

**Real-world analogy (for a 15-year-old):**
Imagine you're watching a soccer game on TV. The camera barely moves for 10 seconds, and only the ball and a few players shift position. A smart video codec says: *"Why store the entire stadium image 300 times? I'll store it once (I-frame), then only record where the ball and players moved (motion vectors)."* This project lets you actually *see* those decisions the codec makes — the movement arrows, the block grid, and what happens when you add something new to the video.

### Why This Matters
- **Video engineers & streaming developers** need to understand bitrate spikes and quality drops
- **Computer vision practitioners** work with decoded frames and must understand compression artifacts
- **Surveillance & media pipeline engineers** need to tune GOP size, B-frame depth, and CRF for their use cases
- **Students** gain hands-on understanding of concepts usually taught only in theory

---

## 2. Educational Background — Video Compression Theory

### 2.1 What Is a GOP (Group of Pictures)?

A **GOP** is a sequence of frames that starts with an **I-frame** (a complete image) and continues with dependent **P-frames** and/or **B-frames**. Think of it like a chapter in a book:

- The **I-frame** is the full chapter — everything is spelled out
- **P-frames** are like saying "same as before, but change paragraph 3"
- **B-frames** are like saying "blend paragraph 3 from the previous AND next chapter"

**Key trade-offs:**

| GOP Property | Short GOP (30 frames) | Long GOP (250 frames) |
|---|---|---|
| Compression efficiency | Lower | Higher |
| Random seek speed | Fast | Slow |
| Error recovery | Quick | Slow |
| Typical use case | Live streaming, surveillance | Movies, VOD |

### 2.2 Frame Types Explained

| Frame Type | Full Name | How It Works | Typical Size |
|---|---|---|---|
| **I-frame** | Intra-coded | Complete image — no dependencies. Like a JPEG snapshot. | Large (100–300 KB) |
| **P-frame** | Predicted | References **previous** frames only. Contains motion vectors + residual data. | Medium (30–80 KB) |
| **B-frame** | Bi-directional | References **both past and future** frames. Highest compression. | Small (5–30 KB) |

**Why does this matter?** When you seek in a video player, the player must find the nearest I-frame and decode forward from there. More I-frames = faster seeking but larger files.

### 2.3 Motion Vectors — The Core of Temporal Compression

A **motion vector** (MV) tells the decoder: *"This 16×16 block of pixels in the current frame? Don't store it from scratch — it's the same block from 2 frames ago, just shifted 5 pixels to the right and 3 pixels down."*

**Types of motion vectors:**

| MV Type | Direction | Used By | Color in Our Visualization |
|---|---|---|---|
| Forward MV | Current → Previous frame | P-frames, B-frames | 🟢 Green |
| Backward MV | Current → Future frame | B-frames only | 🔴 Red |
| Bi-directional MV | Both directions blended | B-frames only | 🔵 Blue |

### 2.4 Macroblocks and DCT

In H.264, each frame is divided into **macroblocks** — typically 16×16 pixel blocks. Each macroblock is independently encoded:

1. **Prediction** — Use motion vectors to predict what this block looks like
2. **Residual** — Calculate the difference between prediction and reality
3. **DCT (Discrete Cosine Transform)** — Convert the residual into frequency components
4. **Quantization** — Throw away invisible details (this is where quality loss happens)
5. **Entropy coding** — Compress the result further with CABAC/CAVLC

**Real-world analogy:** Imagine describing someone's face over the phone. Instead of listing every pixel, you say "it's like yesterday's photo, but the mouth moved slightly left." The motion vector is "mouth moved left," and the residual is "and the shadow changed a tiny bit."

### 2.5 Rate–Distortion Trade-off

The encoder constantly balances two goals:
- **Low bitrate** (small file size) — achieved by aggressive quantization
- **Low distortion** (high quality) — requires keeping more detail

**CRF (Constant Rate Factor)** controls this balance:
- CRF 0 = lossless (huge file)
- CRF 18 = visually lossless (recommended high quality)
- CRF 23 = default (good balance)
- CRF 28 = noticeable quality loss
- CRF 51 = maximum compression (terrible quality)

---

## 3. Target Users & Applications

### Primary Users
- Image & Video Processing students in the AI Developer Expert course
- Computer Vision learners who need to understand how decoded frames differ from raw images
- Engineers learning video compression internals for streaming or surveillance pipelines

### Real-World Application Scenarios

**Scenario 1: Streaming Quality Optimization**
A video engineer notices buffering on a client's live stream. They use Task 1 to analyze the GOP structure and discover the encoder uses a GOP of 250 — too long for live streaming. Switching to GOP=30 reduces latency and eliminates buffering. Our tool teaches exactly *why* this works.

**Scenario 2: Surveillance Anomaly Detection**
A security engineer needs to understand why their motion detection algorithm produces false positives during scene changes. Task 2 reveals that I-frames create zero motion vectors while P-frames show massive spurious vectors during scene cuts. This insight leads them to filter out I-frame transitions.

**Scenario 3: Content-Aware Compression Tuning**
A content creator adds a watermark to their video and notices the file size doubled. Task 3 demonstrates exactly *why* — the moving overlay forces the encoder to create new motion vectors and larger residuals in every frame, dramatically reducing compression efficiency.

**Scenario 4: Educational Demonstration**
A professor needs to visually explain H.264 to students. They run all three tasks on a sample video and show: (a) the GOP structure as a table, (b) the motion arrows as an overlay video, and (c) how adding content affects compression. One toolkit replaces three separate lecture demos.

---

## 4. Input & Output Specification

### 4.1 Input

| Property | Specification |
|---|---|
| **Location** | `input/` folder in project root |
| **Format** | MP4 container |
| **Codec** | H.264/AVC (required) |
| **Duration** | ~1 minute recommended (any duration supported) |
| **Resolution** | Any (tested with 1080p and 720p) |
| **Audio** | Optional — preserved in Task 3 output if present |

**User responsibility:** Place one MP4 video file in the `input/` folder before running the project. The code auto-detects the first `.mp4` file found.

### 4.2 Output — Mandatory Structure

```
output/
├── task 1 - video information/
│   ├── metadata.json              # Full ffprobe JSON (container + streams)
│   ├── gop_analysis.json          # Structured GOP analysis with patterns
│   ├── frame_statistics.csv       # Per-frame data: type, size, pts, key_frame
│   ├── summary_report.txt         # Human-readable report (console-friendly)
│   ├── frame_type_distribution.png # Pie chart: I/P/B percentages
│   ├── frame_sizes_by_type.png    # Box plot: size distribution per type
│   └── bitrate_over_time.png      # Line chart: bitrate fluctuation
│
├── task 2 - motion vectors/
│   ├── motion_vectors_overlay.mp4 # Full video with MV + macroblock overlay
│   ├── sample_frames/             # 5–8 representative PNG frames
│   │   ├── frame_iframe_001.png   # I-frame (no motion vectors)
│   │   ├── frame_pframe_050.png   # P-frame with forward MVs
│   │   ├── frame_bframe_075.png   # B-frame with bi-directional MVs (if present)
│   │   ├── frame_high_motion.png  # Auto-detected high-motion frame
│   │   └── frame_low_motion.png   # Auto-detected low-motion frame
│   └── mv_analysis.json           # Motion vector statistics summary
│
└── task 3 - rotating rectangle/
    ├── overlay_video.mp4          # Final video with moving/rotating rectangle
    ├── rectangle_log.csv          # Per-frame: x, y, angle, frame_number
    ├── compression_comparison.json # Before vs. after file size, bitrate, quality
    └── compression_impact.png     # Bar chart: original vs. modified bitrate
```

---

## 5. Task 1 — Video Statistics & Metadata Extraction

### 5.1 Purpose
Extract comprehensive technical metadata from an input video using `ffprobe`, analyze the GOP structure, and generate both machine-readable and human-readable reports with visualizations.

### 5.2 What the 15-year-old should understand
*"We're opening the video's 'ID card' — finding out its resolution, frame rate, how it's compressed, and how the frames are organized. It's like reading the nutrition label on a food package, but for video."*

### 5.3 Functional Requirements

#### A. Full Metadata Extraction
Using `ffprobe`, extract and organize:

| Category | Fields |
|---|---|
| **Container** | Format name, duration, total bitrate, file size, number of streams |
| **Video stream** | Resolution (width × height), aspect ratio, frame rate (real & average), codec name, profile, level, pixel format, color space, color primaries, color transfer, bit depth |
| **Audio stream** (if present) | Codec, sample rate, channels, layout, bitrate |
| **GOP** | GOP size (keyframe interval), B-frame depth, reference frame count |

**FFmpeg command reference:**
```bash
# Full metadata as JSON
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Frame-by-frame analysis
ffprobe -v error -select_streams v:0 \
  -show_entries frame=key_frame,pict_type,pts_time,pkt_size,coded_picture_number \
  -of csv=p=0 input.mp4
```

#### B. GOP Structure Analysis
- Detect GOP pattern (e.g., `IBBBPBBBPBBBP...`)
- Calculate GOP length (number of frames between I-frames)
- Identify if GOPs are fixed-length or variable
- Count total I/P/B frames and calculate percentage distribution

#### C. I-Frame Statistics
- Average I-frame size (bytes)
- Min/Max I-frame size
- Standard deviation of I-frame sizes
- Average temporal distance between I-frames (in frames and seconds)

#### D. Bitrate Analysis
- Average bitrate over time
- Peak bitrate moment (which frame/second)
- Bitrate per frame type (average I, P, B frame sizes)

#### E. Visualization Requirements (3 graphs minimum)

**Graph 1: Frame Type Distribution** (pie chart)
- Slices for I, P, B frames with percentages and counts
- Color scheme: Blue = I-frame, Green = P-frame, Orange = B-frame

**Graph 2: Frame Size Distribution by Type** (box plot or violin plot)
- One box per frame type showing min, Q1, median, Q3, max
- Clearly demonstrates why I-frames are larger than P and B frames

**Graph 3: Bitrate Over Time** (line chart)
- X-axis: time in seconds
- Y-axis: bitrate (kbps), windowed average (e.g., 1-second window)
- Annotate I-frame positions with vertical markers

#### F. Output Files
- `metadata.json` — Full ffprobe JSON output
- `gop_analysis.json` — Structured GOP analysis (pattern, length, I/P/B counts)
- `frame_statistics.csv` — One row per frame: `frame_number, pict_type, key_frame, pkt_size, pts_time`
- `summary_report.txt` — Human-readable summary with key findings
- Three PNG graph files as described above

### 5.4 Acceptance Criteria
- [ ] All metadata fields extracted without errors
- [ ] GOP pattern correctly identified and displayed
- [ ] Frame type counts match total frame count
- [ ] I-frame statistics are mathematically correct (verified manually on 3 frames)
- [ ] All 3 graphs generated and saved as PNG (300 DPI)
- [ ] Summary report is readable by a non-technical person
- [ ] Runs in under 30 seconds for a 1-minute 1080p video

---

## 6. Task 2 — Motion Vector & Macroblock Visualization

### 6.1 Purpose
Generate a video that visually overlays motion vectors and macroblock boundaries on top of the original video, making the encoder's temporal prediction decisions visible to the human eye.

### 6.2 What the 15-year-old should understand
*"We're making the invisible visible. Normally, motion vectors are hidden data inside the compressed file. We're going to draw them as arrows on top of the video — so you can literally see the encoder saying 'this block moved from HERE to THERE between frames.'"*

### 6.3 Functional Requirements

#### A. Motion Vector Overlay Video
Generate a full video with FFmpeg's `codecview` filter showing:
- **Macroblock grid** — 16×16 pixel boundaries visible on all frames
- **Forward P-frame MVs** — Green arrows showing prediction from previous frame
- **Forward B-frame MVs** — Blue arrows showing forward prediction
- **Backward B-frame MVs** — Red arrows showing backward prediction

**Primary FFmpeg command:**
```bash
ffmpeg -flags2 +export_mvs -i input.mp4 \
  -vf "codecview=mv=pf+bf+bb:block=1" \
  -c:v libx264 -crf 18 -preset medium \
  output/task\ 2\ -\ motion\ vectors/motion_vectors_overlay.mp4
```

**Command breakdown:**

| Flag / Filter | Purpose |
|---|---|
| `-flags2 +export_mvs` | Instructs the decoder to export motion vector data during decoding |
| `codecview=mv=pf+bf+bb` | Draws motion vectors: `pf` = P-frame forward, `bf` = B-frame forward, `bb` = B-frame backward |
| `:block=1` | Draws macroblock boundaries (16×16 grid) |
| `-crf 18` | High-quality output encoding |

#### B. Sample Frame Extraction
Automatically extract 5–8 representative frames as PNGs:
1. **One I-frame** — Shows macroblock grid but NO motion vectors (I-frames don't reference other frames)
2. **Two P-frames** — Show green forward motion vectors
3. **One B-frame** (if present) — Shows blue + red bi-directional vectors
4. **One high-motion frame** — Auto-detected (largest average MV magnitude)
5. **One low-motion frame** — Auto-detected (smallest average MV magnitude)

**Frame extraction command:**
```bash
# Extract specific frame types
ffmpeg -flags2 +export_mvs -i input.mp4 \
  -vf "codecview=mv=pf+bf+bb:block=1,select='eq(pict_type\,I)'" \
  -vsync vfr -frames:v 1 output/frame_iframe_001.png
```

#### C. Motion Vector Statistics
Generate `mv_analysis.json` containing:
- Total frames analyzed
- Frames with motion vectors vs. without (I-frames)
- If B-frames are present (boolean + count)
- Video characteristics that affect MV density (resolution, frame rate, motion level)

#### D. Color Legend Documentation
The README must include a clear color legend table:

| Color | Arrow Type | Source Frame | Meaning |
|---|---|---|---|
| 🟢 Green | Forward MV | P-frame | "This block came from a previous frame" |
| 🔵 Blue | Forward MV | B-frame | "This block came from a previous frame (in a B-frame)" |
| 🔴 Red | Backward MV | B-frame | "This block came from a future frame" |
| ⬜ Grid | Macroblock borders | All frames | 16×16 pixel block boundaries |

### 6.4 Acceptance Criteria
- [ ] Overlay video generated and playable in standard video players (VLC, mpv)
- [ ] Motion vectors clearly visible as directional arrows
- [ ] Macroblock grid visible on all frames
- [ ] 5+ sample frames extracted as PNG (300 DPI)
- [ ] I-frame shows grid but no motion arrows
- [ ] P-frame shows green forward arrows
- [ ] `mv_analysis.json` contains correct statistics
- [ ] Video has no dropped frames or audio sync issues
- [ ] Runs in under 60 seconds for a 1-minute 1080p video

---

## 7. Task 3 — Moving & Rotating Rectangle Overlay

### 7.1 Purpose
Demonstrate video decompression, pixel-level editing, and recompression by programmatically inserting a moving, rotating, semi-transparent rectangle into a compressed video — then measure the impact on compression efficiency.

### 7.2 What the 15-year-old should understand
*"We're going to 'open up' each frame of the video (decompress it), draw a spinning rectangle on top of it, and then save it back as a compressed video. The cool part? We'll measure how much BIGGER the file gets — because the encoder now has to deal with this new moving thing that wasn't there before. It's like sneaking a sticker onto every page of a flipbook and then asking how much thicker the book got."*

### 7.3 Functional Requirements

#### A. Rectangle Properties

| Property | Specification |
|---|---|
| **Size** | 200×100 pixels |
| **Color** | Semi-transparent — must remain visible on any background |
| **Opacity** | 70% (alpha = 0.7) — original video partially visible through rectangle |
| **Rotation** | Full 360° rotation every 5 seconds (continuous, smooth) |
| **Position** | Centered on the video frame |
| **Movement** | Center-based, edge-bouncing diagonal movement |
| **Adaptivity** | Color should contrast with underlying content (e.g., inverted or bright overlay) |

#### B. Implementation Approach — Two Options

**Option 1: Pure FFmpeg (filter_complex)**
```bash
ffmpeg -i input.mp4 -filter_complex "
  color=c=red@0.7:s=200x100:d=85:r=60[rect];
  [rect]format=rgba[rect_alpha];
  [rect_alpha]rotate=a=2*PI*t/5:c=none:ow=300:oh=300[rotated];
  [0:v][rotated]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1[out]
" -map "[out]" -map 0:a? -c:v libx264 -crf 18 -c:a copy output.mp4
```

**Option 2: Python + OpenCV (frame-by-frame)**
```python
# Pseudo-code for the Python approach
for frame in video_frames:
    raw_frame = decompress(frame)         # Step 1: Decompress
    edited_frame = draw_rectangle(         # Step 2: Edit pixels
        raw_frame, x, y, angle, opacity=0.7
    )
    compress_and_write(edited_frame)       # Step 3: Recompress
```

**Recommended approach:** Python + OpenCV for maximum control and educational value (shows the decompress → edit → recompress pipeline explicitly). FFmpeg for audio track handling.

#### C. Movement Logic
- Initial position: center of frame
- Velocity: configurable (default: 5 px/frame horizontal, 3 px/frame vertical)
- Direction: diagonal movement
- Bouncing: reverse velocity component when rectangle edge hits frame edge
- Rotation: angle = `(2 * π * frame_number) / (fps * 5)` radians (360° every 5 seconds)

#### D. Semi-Transparency Implementation
```python
# Blend rectangle with background
alpha = 0.7  # Rectangle opacity
blended = cv2.addWeighted(rectangle_region, alpha, background_region, 1 - alpha, 0)
```

**Why semi-transparent?** The assignment specifically notes that on a colorful video, a solid rectangle might "disappear" against similarly-colored backgrounds. Semi-transparency ensures the rectangle is always visible while demonstrating the additive pixel editing concept.

#### E. Re-Encoding Parameters

| Parameter | Value | Reason |
|---|---|---|
| Codec | H.264 (libx264) | Match original format |
| CRF | 18 | High quality, allows fair compression comparison |
| Preset | medium | Balance between speed and compression |
| GOP size | Same as original (or configurable) | Fair comparison |
| B-frames | Same as original (or configurable) | Fair comparison |

#### F. Compression Impact Analysis
After generating the overlay video, compare:

| Metric | Original | With Overlay | Delta |
|---|---|---|---|
| File size (bytes) | Measured | Measured | % increase |
| Average bitrate (kbps) | Measured | Measured | % increase |
| Average frame size (bytes) | Measured | Measured | % increase |

**Generate a bar chart** (`compression_impact.png`) showing original vs. modified for each metric.

#### G. Position Logging
Write `rectangle_log.csv` with columns:
```
frame_number, timestamp_sec, center_x, center_y, angle_degrees, velocity_x, velocity_y
```

#### H. Output Files
- `overlay_video.mp4` — Final video with animated rectangle (audio preserved if present)
- `rectangle_log.csv` — Per-frame position/angle log
- `compression_comparison.json` — Before/after compression metrics
- `compression_impact.png` — Bar chart visualization of compression impact

### 7.4 Acceptance Criteria
- [ ] Rectangle rotates smoothly at specified speed (360° every 5 seconds)
- [ ] Rectangle bounces off frame edges without going out of bounds
- [ ] Rectangle is semi-transparent (background video visible through it)
- [ ] Rectangle visible on both light and dark backgrounds
- [ ] Output video plays without errors in standard players
- [ ] Audio track preserved (if original has audio)
- [ ] Position log has one entry per frame
- [ ] Compression comparison shows measurable difference
- [ ] Bar chart clearly shows bitrate impact
- [ ] Runs in under 120 seconds for a 1-minute 1080p video

---

## 8. Technical Requirements

### 8.1 Environment

| Component | Specification |
|---|---|
| **Python** | 3.10+ |
| **Virtual Environment** | UV (MANDATORY) |
| **OS** | Windows 11 + WSL (primary), Linux, macOS |
| **FFmpeg** | 7.0+ with `libx264` and `codecview` support |
| **FFprobe** | Bundled with FFmpeg |

### 8.2 Core Dependencies

| Package | Purpose | Required? |
|---|---|---|
| `numpy` | Array operations (frame manipulation, statistics) | MANDATORY |
| `opencv-python` (cv2) | Video frame reading/writing, rectangle drawing | MANDATORY |
| `matplotlib` | All graph/chart generation | MANDATORY |
| `pandas` | CSV generation and frame statistics | MANDATORY |
| `pathlib` | Cross-platform path handling | MANDATORY (stdlib) |

### 8.3 Code Standards

| Rule | Specification |
|---|---|
| **Max lines per file** | 150 lines (split into modules if exceeded) |
| **Array operations** | NumPy vectorization — no basic Python loops for array math |
| **Path handling** | `pathlib.Path` — all relative paths, no absolute paths |
| **Type hints** | All functions must have parameter and return type hints |
| **Docstrings** | All functions must explain WHAT, WHY, and HOW |
| **Comments** | Must pass the "15-year-old test" |
| **Error handling** | Try/except with informative messages; validate FFmpeg availability |
| **Logging** | Ring buffer logging system (see project guidelines) |
| **Package structure** | `__init__.py` in every Python package directory |

### 8.4 FFmpeg Dependency Validation
The project **must** check that FFmpeg and FFprobe are installed and accessible before running any task:

```python
def validate_ffmpeg() -> bool:
    """Check FFmpeg and FFprobe are installed and support required features."""
    # Check ffmpeg exists
    # Check ffprobe exists
    # Check libx264 encoder available
    # Check codecview filter available
    # Return True or raise informative error
```

---

## 9. Directory Structure

```
L35-ffmpeg-video-toolkit/
├── README.md                      # Project showcase document
├── main.py                        # Single entry point — runs all 3 tasks
├── requirements.txt               # Exact dependency versions
├── .gitignore                     # Secrets, cache, large videos
│
├── venv/                          # Virtual environment indicator
│   └── .gitkeep                   # UV setup instructions
│
├── src/                           # ALL source code
│   ├── __init__.py                # Package marker
│   ├── config.py                  # All constants, paths, parameters
│   ├── ffmpeg_utils.py            # FFmpeg/FFprobe wrapper functions
│   │
│   ├── task1/                     # Task 1: Video Information
│   │   ├── __init__.py
│   │   ├── metadata_extractor.py  # Extract full metadata via ffprobe
│   │   ├── gop_analyzer.py        # GOP structure analysis
│   │   ├── frame_statistics.py    # Per-frame stats and CSV generation
│   │   ├── visualizer.py          # Graphs: pie chart, box plot, bitrate line
│   │   └── report_generator.py    # Human-readable summary report
│   │
│   ├── task2/                     # Task 2: Motion Vectors
│   │   ├── __init__.py
│   │   ├── mv_visualizer.py       # Generate overlay video via FFmpeg
│   │   ├── frame_extractor.py     # Extract sample frames (I/P/B/high/low motion)
│   │   └── mv_analyzer.py         # Motion vector statistics
│   │
│   ├── task3/                     # Task 3: Rotating Rectangle
│   │   ├── __init__.py
│   │   ├── rectangle_overlay.py   # Frame-by-frame rectangle rendering
│   │   ├── motion_logic.py        # Bouncing + rotation math
│   │   ├── compression_analyzer.py# Before/after comparison
│   │   └── visualizer.py          # Compression impact bar chart
│   │
│   └── utils/                     # Shared utilities
│       ├── __init__.py
│       ├── paths.py               # Relative path resolution
│       ├── logger.py              # Ring buffer logging
│       └── validators.py          # Input validation (file exists, format check)
│
├── docs/                          # Documentation
│   ├── PRD.md                     # This document
│   └── tasks.json                 # Implementation task breakdown
│
├── input/                         # Input MP4 video (committed to repo)
│   └── *.mp4                     # H.264 video for analysis
│
├── output/                        # All generated results
│   ├── task 1 - video information/
│   ├── task 2 - motion vectors/
│   │   └── sample_frames/
│   └── task 3 - rotating rectangle/
│
├── results/                       # Graphs and visual results for README
│   ├── graphs/                    # All visualization PNGs
│   └── previews/                  # GIF previews for README auto-play
│
└── logs/                          # Ring buffer logs
    ├── config/
    │   └── log_config.json
    └── .gitkeep
```

### Code Files Estimate

| File | Purpose | Est. Lines |
|---|---|---|
| `main.py` | Entry point, argument parsing, task orchestration | ~60 |
| `src/config.py` | Constants, default parameters, color schemes | ~50 |
| `src/ffmpeg_utils.py` | FFmpeg/FFprobe wrappers (run command, parse JSON) | ~80 |
| `src/task1/metadata_extractor.py` | Full metadata extraction | ~80 |
| `src/task1/gop_analyzer.py` | GOP pattern detection and stats | ~100 |
| `src/task1/frame_statistics.py` | Per-frame CSV generation | ~70 |
| `src/task1/visualizer.py` | 3 graphs for Task 1 | ~120 |
| `src/task1/report_generator.py` | Human-readable summary | ~80 |
| `src/task2/mv_visualizer.py` | FFmpeg codecview overlay generation | ~70 |
| `src/task2/frame_extractor.py` | Sample frame extraction logic | ~90 |
| `src/task2/mv_analyzer.py` | MV statistics | ~60 |
| `src/task3/rectangle_overlay.py` | Main overlay pipeline | ~130 |
| `src/task3/motion_logic.py` | Bouncing + rotation calculations | ~60 |
| `src/task3/compression_analyzer.py` | Before/after comparison | ~80 |
| `src/task3/visualizer.py` | Compression impact chart | ~70 |
| `src/utils/paths.py` | Path resolution helpers | ~40 |
| `src/utils/logger.py` | Ring buffer logging | ~130 |
| `src/utils/validators.py` | Input validation | ~50 |
| **Total** | | **~1,500** |
| **Average per file** | | **~83** |
| **Max per file** | | **≤150 ✅** |

---

## 10. Performance Requirements

| Metric | Target | Measured On |
|---|---|---|
| Task 1 total runtime | < 30 seconds | 1-minute 1080p H.264 video |
| Task 2 overlay generation | < 60 seconds | 1-minute 1080p H.264 video |
| Task 2 frame extraction | < 15 seconds | 5–8 frames |
| Task 3 overlay rendering | < 120 seconds | 1-minute 1080p H.264 video |
| Peak memory usage | < 500 MB | Any task |
| Output video quality | Visually lossless | CRF 18 |
| Output video compatibility | Plays in VLC, mpv, Windows Media Player | All output MP4 files |

---

## 11. Security & Configuration

### 11.1 Security Checklist
- [ ] No hardcoded file paths — all relative via `pathlib.Path`
- [ ] Input validation: check file exists, check file is MP4, check FFmpeg installed
- [ ] No API keys or secrets in this project (FFmpeg is local)
- [ ] Safe subprocess calls: use `subprocess.run()` with list arguments (no shell=True)
- [ ] No arbitrary code execution from user input

### 11.2 Configuration via `src/config.py`
All "magic numbers" centralized with explanations:

```python
# Task 3: Rectangle overlay parameters
RECT_WIDTH = 200       # Rectangle width in pixels
RECT_HEIGHT = 100      # Rectangle height in pixels
RECT_OPACITY = 0.7     # 70% opaque (30% transparent)
ROTATION_PERIOD = 5.0  # Seconds for one full 360° rotation
VELOCITY_X = 5         # Horizontal speed: pixels per frame
VELOCITY_Y = 3         # Vertical speed: pixels per frame

# Encoding parameters
CRF_VALUE = 18         # Constant Rate Factor (18 = visually lossless)
PRESET = "medium"      # Encoding speed/compression trade-off
```

---

## 12. README & Documentation Strategy

The README is the **face of the project** — most visitors will only look at the README. It must include:

### 12.1 Visual Results (embedded in README)
- **Input Video:** GIF preview auto-playing in README, linking to the committed MP4
- **Task 1:** Tables with metadata, GOP analysis, frame statistics + 3 embedded graph images
- **Task 2:** GIF preview of MV overlay video (auto-plays) + link to full MP4 + sample frame images in a table grid + color legend
- **Task 3:** GIF preview of rotating rectangle overlay (auto-plays) + link to full MP4 + compression comparison table + impact chart

### 12.2 Educational Content
- Each task section explains the theory BEFORE showing results
- "What you're looking at" descriptions for every image/graph
- Real-world analogies for compression concepts
- The README itself should teach video compression to someone with no background

### 12.3 FFmpeg Commands Reference
- Document every FFmpeg command used in the project
- Include a breakdown table for each command (flag → purpose)
- Users should be able to run the commands manually from terminal

### 12.4 Auto-Generated Content
- The last 3 test runs should be captured and reflected in the README
- Performance benchmarks included with actual measured times

---

## 13. Learning Objectives Matrix

| Concept | Where Demonstrated | How the Student Sees It |
|---|---|---|
| GOP structure | Task 1: `gop_analysis.json` + report | Pattern like `IBBBPBBBP...` with length and I-frame intervals |
| I/P/B frame roles | Task 1: frame statistics + pie chart | Size differences visible in box plot; distribution in pie chart |
| Bitrate distribution | Task 1: bitrate over time chart | Spikes at I-frames, valleys at B-frames |
| Motion compensation | Task 2: overlay video + sample frames | Green/blue/red arrows showing block movement |
| Macroblock structure | Task 2: grid overlay | Visible 16×16 grid on every frame |
| DCT behavior | Task 2: macroblock observation | Blocks with high detail have more complex residuals |
| Pixel-level editing | Task 3: rectangle overlay pipeline | Decompress → edit → recompress workflow |
| Rate–distortion trade-off | Task 3: compression comparison | File size increase measured and visualized |
| Content-dependent compression | Task 3: impact analysis | Moving rectangle forces encoder to work harder |
| Encoder sensitivity to motion | Task 3: position log + bitrate analysis | More rectangle movement = more bits needed |

---

## 14. Success Criteria & Acceptance Tests

### 14.1 Functional Success
- [ ] All three tasks execute successfully via `python main.py`
- [ ] Individual tasks runnable via `python main.py --task 1` (or 2 or 3)
- [ ] Output folder structure matches specification exactly
- [ ] All output files generated without errors
- [ ] Output videos playable in standard video players

### 14.2 Educational Success
- [ ] GOP behavior clearly observable in Task 1 output
- [ ] Motion vectors are interpretable and correctly colored in Task 2
- [ ] Compression impact of overlay is measurable and visualized in Task 3
- [ ] README teaches video compression concepts with real-world analogies

### 14.3 Code Quality Success
- [ ] Every source file ≤ 150 lines
- [ ] NumPy used for all array operations (no basic Python loops)
- [ ] All functions have type hints and docstrings
- [ ] Ring buffer logging implemented
- [ ] All paths are relative (pathlib.Path)
- [ ] `__init__.py` in every package directory
- [ ] FFmpeg availability validated before task execution

### 14.4 Documentation Success
- [ ] README includes visual results (images embedded)
- [ ] README includes FFmpeg commands with breakdowns
- [ ] Installation instructions tested on clean WSL environment
- [ ] Code files summary table with line counts
- [ ] Minimum 3 example runs documented

### 14.5 Performance Success
- [ ] Task 1 completes in < 30 seconds
- [ ] Task 2 completes in < 60 seconds
- [ ] Task 3 completes in < 120 seconds
- [ ] Peak memory < 500 MB

---

## 15. Assumptions & Constraints

### Assumptions
- Input video uses H.264/AVC codec (not H.265/HEVC or VP9)
- FFmpeg build includes `codecview` filter and `libx264` encoder
- Student has prior exposure to image processing basics (L32–L33 projects)
- WSL has sufficient disk space for temporary decoded frames (~500 MB for 1080p × 60 sec)
- Input video is not DRM-protected

### Constraints
- **150-line file limit** enforces modular design
- **No GUI** — command-line only with file outputs
- **Single input video** — one MP4 at a time
- **H.264 only** — other codecs may produce different results with codecview
- **Audio handling** — OpenCV cannot write audio; FFmpeg used for audio track remuxing

---

## 16. Future Extensions

### Phase 1: Quick Wins
- Support for multiple input videos (batch processing)
- HTML report generation with embedded graphs
- Configurable CRF sweep for rate–distortion curves

### Phase 2: Advanced Analysis
- Scene change detection and annotation
- Compare two encodings side-by-side (different CRF values)
- Macroblock-level heatmap (color intensity = block size)

### Phase 3: Visionary
- Real-time preview of motion vectors using OpenCV window
- H.265/HEVC support with CTU visualization
- Web dashboard for interactive video analysis

---

## 17. References

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [FFmpeg Filters — codecview](https://ffmpeg.org/ffmpeg-filters.html#codecview)
- [FFprobe Documentation](https://ffmpeg.org/ffprobe.html)
- [H.264/AVC Specification (ITU-T Rec. H.264)](https://www.itu.int/rec/T-REC-H.264)
- [H.264 Is Magic — Sid Bala](https://sidbala.com/h-264-is-magic/) — Excellent visual explanation
- [Video Compression Fundamentals — Ottverse](https://ottverse.com/video-compression-basics/)

---

## 18. Phase Gate

### ⚠️ STOP HERE

Implementation (Phase 2) may only begin **after explicit approval** of:
1. ✅ This PRD document (`docs/PRD.md`)
2. ✅ Task breakdown (`docs/tasks.json`)

**Next step:** Create `tasks.json` with detailed task breakdown, dependencies, time estimates, and file assignments — then wait for approval before writing any code.
