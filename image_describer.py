import argparse
import base64
import mimetypes
import os
import sys
from pathlib import Path
from typing import Optional

from groq import Groq
from dotenv import load_dotenv

DEFAULT_MODEL = os.getenv("GROQ_VISION_MODEL", "auto")

PREFERRED_VISION_MODELS = [
    "qwen/qwen2.5-vl-72b-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.2-90b-vision-preview",
    "llama-3.2-11b-vision-preview",
]

load_dotenv()


def resolve_vision_model(client: Groq, requested_model: Optional[str]) -> str:
    if requested_model and requested_model.lower() != "auto":
        return requested_model

    models = client.models.list()
    available = [
        model.id
        for model in getattr(models, "data", [])
        if getattr(model, "id", None)
    ]

    for model_name in PREFERRED_VISION_MODELS:
        if model_name in available:
            return model_name

    for model_name in available:
        lowered = model_name.lower()
        if "vision" in lowered or "vl" in lowered:
            return model_name

    raise RuntimeError(
        "No vision-capable model found in your Groq account. "
        "Pass one explicitly with --model."
    )


def image_to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "image/png"

    with image_path.open("rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def describe_image(image_path: Path, api_key: str, model: str = DEFAULT_MODEL) -> str:
    client = Groq(api_key=api_key)
    selected_model = resolve_vision_model(client, model)
    data_url = image_to_data_url(image_path)

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe this image clearly and accurately in plain English. "
                            "Mention key objects, people, actions, setting, and any visible text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe an image using Groq vision model")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=(
            "Groq model to use. Use 'auto' to pick an available vision model "
            f"(default: {DEFAULT_MODEL})"
        ),
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("GROQ_API_KEY"),
        help="Groq API key (or set GROQ_API_KEY environment variable)",
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: missing API key. Use --api-key or set GROQ_API_KEY.", file=sys.stderr)
        return 1

    image_path = Path(args.image)
    if not image_path.exists() or not image_path.is_file():
        print(f"Error: image not found: {image_path}", file=sys.stderr)
        return 1

    try:
        description = describe_image(image_path=image_path, api_key=args.api_key, model=args.model)
        print(description)
        return 0
    except Exception as exc:
        print(f"Error while describing image: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
