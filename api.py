import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from image_describer import describe_image
from video_describer import describe_video


app = FastAPI(title="Image Describer API", version="1.0.0")


class DescribeResponse(BaseModel):
    description: str


class VideoDescribeResponse(BaseModel):
    description: str
    frame_descriptions: list[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/describe", response_model=DescribeResponse)
def describe(
    image: UploadFile = File(..., description="Image file to describe"),
    model: str = Form(default="auto"),
) -> DescribeResponse:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY")

    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    suffix = Path(image.filename or "upload.jpg").suffix or ".jpg"
    tmp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image.file.read())
            tmp_path = Path(tmp.name)

        text = describe_image(image_path=tmp_path, api_key=api_key, model=model or "auto")
        return DescribeResponse(description=text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to describe image: {exc}") from exc
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


@app.post("/describe-video", response_model=VideoDescribeResponse)
def describe_video_file(
    video: UploadFile = File(..., description="Video file to describe"),
    model: str = Form(default="auto"),
    max_frames: int = Form(default=4),
    summary_model: str = Form(default="llama-3.3-70b-versatile"),
) -> VideoDescribeResponse:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY")

    if video.content_type and not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video")

    suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"
    tmp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(video.file.read())
            tmp_path = Path(tmp.name)

        result = describe_video(
            video_path=tmp_path,
            api_key=api_key,
            model=model or "auto",
            max_frames=max_frames,
            summary_model=summary_model,
        )
        return VideoDescribeResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to describe video: {exc}") from exc
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
