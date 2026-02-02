#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using OpenRouter with Nano Banana Pro (Gemini 3 Pro Image Preview).

Usage:
    uv run generate_image.py --prompt "your image description" [--filename "output.png" | --filename auto] [--resolution 1K|2K|4K] [--api-key KEY]
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from io import BytesIO
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def get_base_url() -> str | None:
    value = os.environ.get("OPENROUTER_BASE_URL")
    if value:
        return value.strip()
    return None


def load_env_files(paths: list[Path]) -> None:
    for env_path in paths:
        if not env_path.is_file():
            continue
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        except Exception:
            # Ignore .env read errors and fall back to existing env
            continue


def slugify(text: str, fallback: str = "image") -> str:
    cleaned: list[str] = []
    last_was_dash = False
    for ch in text.lower():
        if ch.isascii() and ch.isalnum():
            cleaned.append(ch)
            last_was_dash = False
        elif ch in {" ", "-", "_"}:
            if not last_was_dash:
                cleaned.append("-")
                last_was_dash = True
    slug = "".join(cleaned).strip("-")
    if not slug:
        slug = fallback
    return slug[:40]


def build_user_message(prompt: str, input_image_data_url: str | None) -> list[dict]:
    if input_image_data_url:
        content = [
            {"type": "image_url", "image_url": {"url": input_image_data_url}},
            {"type": "text", "text": prompt},
        ]
    else:
        content = prompt
    return [{"role": "user", "content": content}]


def image_to_data_url(input_image) -> str:
    buffer = BytesIO()
    input_image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def extract_image_url(image_entry: dict) -> str | None:
    if isinstance(image_entry, dict):
        if "image_url" in image_entry:
            return image_entry["image_url"].get("url")
        if "imageUrl" in image_entry:
            return image_entry["imageUrl"].get("url")
    return None


def save_image_from_url(image_url: str, output_path: Path) -> None:
    if image_url.startswith("data:"):
        header, encoded = image_url.split(",", 1)
        if ";base64" in header:
            image_bytes = base64.b64decode(encoded)
        else:
            image_bytes = urllib.parse.unquote_to_bytes(encoded)
    else:
        with urllib.request.urlopen(image_url) as response:
            image_bytes = response.read()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(image_bytes)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using OpenRouter Nano Banana Pro (Gemini 3 Pro Image Preview)"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        help="Output filename (e.g., sunset-mountains.png). Use 'auto' to generate one."
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Optional input image path for editing/modification"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="OpenRouter API key (overrides OPENROUTER_API_KEY env var)"
    )

    args = parser.parse_args()

    # Load .env from current working dir and skill dir (if present)
    script_dir = Path(__file__).resolve().parent
    load_env_files([Path.cwd() / ".env", script_dir / ".env"])

    # Auto-generate filename if missing or set to "auto"
    if not args.filename or str(args.filename).lower() in {"auto", "timestamp", "now"}:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        slug = slugify(args.prompt)
        args.filename = f"{timestamp}-{slug}.png"
        print(f"Auto filename: {args.filename}")

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    openrouter_url = get_base_url()
    if not openrouter_url:
        print("Error: No API base URL provided.", file=sys.stderr)
        print("Please set OPENROUTER_BASE_URL environment variable", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key to avoid slow import on error
    from PIL import Image as PILImage

    model_name = "google/gemini-3-pro-image-preview"

    # Set up output path (always under workspace outputs folder)
    output_base_dir = (
        Path.home()
        / ".openclaw"
        / "workspace"
        / "outputs"
        / "nano-banana-pro-openrouter"
    )
    output_base_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_base_dir / Path(args.filename).name

    # Load input image if provided
    input_image = None
    input_image_data_url = None
    output_resolution = args.resolution
    if args.input_image:
        try:
            input_image = PILImage.open(args.input_image)
            print(f"Loaded input image: {args.input_image}")

            # Auto-detect resolution if not explicitly set by user
            if args.resolution == "1K":  # Default value
                # Map input image size to resolution
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                else:
                    output_resolution = "1K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")

            input_image_data_url = image_to_data_url(input_image)
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)

    # Build request (image first if editing, prompt only if generating)
    if input_image:
        messages = build_user_message(args.prompt, input_image_data_url)
        print(f"Editing image with resolution {output_resolution}...")
    else:
        messages = build_user_message(args.prompt, None)
        print(f"Generating image with resolution {output_resolution}...")

    try:
        payload = {
            "model": model_name,
            "messages": messages,
            "modalities": ["image", "text"],
            "image_config": {"image_size": output_resolution},
            "stream": False,
        }
        request = urllib.request.Request(
            openrouter_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
        result = json.loads(response_body)

        if "error" in result:
            raise RuntimeError(result["error"].get("message", "Unknown API error"))

        # Process response and convert to PNG
        if not result.get("choices"):
            print("Error: No choices returned in response.", file=sys.stderr)
            sys.exit(1)

        message = result["choices"][0].get("message", {})
        if message.get("content"):
            print(f"Model response: {message['content']}")

        images = message.get("images")
        if not images:
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

        saved_paths = []
        for index, image_entry in enumerate(images, start=1):
            image_url = extract_image_url(image_entry)
            if not image_url:
                continue

            if index == 1:
                target_path = output_path
            else:
                target_path = output_path.with_name(
                    f"{output_path.stem}-{index}{output_path.suffix}"
                )

            save_image_from_url(image_url, target_path)
            saved_paths.append(target_path.resolve())

        if saved_paths:
            for saved_path in saved_paths:
                print(f"\nImage saved: {saved_path}")
                print(f"MEDIA_URL=file://{saved_path}")
        else:
            print("Error: No valid image URLs found in response.", file=sys.stderr)
            sys.exit(1)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        print(f"Error generating image: {e.code} {e.reason}", file=sys.stderr)
        if error_body:
            print(error_body, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
