import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List

from groq import Groq
from image_describer import describe_image
import os

DEFAULT_TEXT_MODEL = "llama-3.3-70b-versatile"

if os.name == "nt":  # Windows
    FFMPEG_PATH = "ffmpeg"
else:  # Linux / Streamlit Cloud (mount is read-only — copy binary to writable /tmp)
    _src = Path(__file__).parent / "ffmpeg"
    _dst = Path(tempfile.gettempdir()) / "ffmpeg_exec"

    if not _dst.exists():
        shutil.copy2(_src, _dst)

    try:
        os.chmod(_dst, 0o755)
    except Exception:
        pass

    FFMPEG_PATH = str(_dst)


def summarize_frame_descriptions(
    frame_descriptions: List[str],
    api_key: str,
    model: str = DEFAULT_TEXT_MODEL,
) -> str:
    if not frame_descriptions:
        return "No visual details were extracted from the video."

    client = Groq(api_key=api_key)
    merged = "\n\n".join(frame_descriptions)

    prompt = (
        "You are summarizing a short video from frame-by-frame descriptions. "
        "Write one accurate, coherent total summary in plain English. "
        "Keep it concise (3-5 sentences), avoid bullets, and avoid repeating details. "
        "If visible text appears in multiple frames, include only the most important points.\n\n"
        f"Frame descriptions:\n{merged}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def extract_video_frames(video_path: Path, max_frames: int = 4, interval_seconds: int = 2) -> List[Path]:
    frames_dir = Path(tempfile.mkdtemp(prefix="video_frames_"))
    frame_pattern = frames_dir / "frame_%03d.jpg"

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"fps=1/{max(1, interval_seconds)}",
        "-frames:v",
        str(max(1, max_frames)),
        str(frame_pattern),
        "-hide_banner",
        "-loglevel",
        "error",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("ffmpeg is not installed or not available in PATH") from exc

    if result.returncode != 0:
        detail = (result.stderr or "").strip() or "Unknown ffmpeg error"
        raise RuntimeError(f"Frame extraction failed: {detail}")

    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not frames:
        raise RuntimeError("No frames were extracted from the video")

    return frames


def describe_video(
    video_path: Path,
    api_key: str,
    model: str = "auto",
    max_frames: int = 4,
    interval_seconds: int = 2,
    summary_model: str = DEFAULT_TEXT_MODEL,
) -> dict:
    frames = extract_video_frames(
        video_path=video_path,
        max_frames=max_frames,
        interval_seconds=interval_seconds,
    )

    frame_descriptions: List[str] = []
    for index, frame in enumerate(frames, start=1):
        frame_text = describe_image(image_path=frame, api_key=api_key, model=model)
        frame_descriptions.append(f"Frame {index}: {frame_text}")

    summary = summarize_frame_descriptions(
        frame_descriptions=frame_descriptions,
        api_key=api_key,
        model=summary_model,
    )

    for frame in frames:
        frame.unlink(missing_ok=True)

    try:
        frames[0].parent.rmdir()
    except OSError:
        pass

    return {
        "description": summary,
        "frame_descriptions": frame_descriptions,
    }