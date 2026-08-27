"""One-shot Veo cinematic evidence generator.

Takes a storyboard prompt that already exists, sends exactly one Veo request to
Vertex AI using Application Default Credentials, saves the returned MP4, and
writes an adjacent JSON manifest that lets a reviewer verify the artifact
without trusting this script's stdout.

The manifest never stores the prompt itself, only its SHA-256, so a storyboard
can stay private while remaining verifiable.

Usage (each run is a billable Veo generation):

    export GOOGLE_CLOUD_PROJECT=your-gcp-project
    export GOOGLE_CLOUD_LOCATION=us-central1
    python -m scripts.generate_cinematic_scene \
        --prompt-file storyboard/scene_01.txt \
        --output evidence/scene_01.mp4

For continuity, pass the previous shot's final frame as the first frame of the
next one (image-to-video guidance, still exactly one generation):

    python -m scripts.generate_cinematic_scene         --prompt-file storyboard/scene_02.txt         --first-frame evidence/scene_01_last_frame.png         --output evidence/scene_02.mp4

Add --dry-run to validate every input and print the resolved plan without
contacting the API (no cost, no credentials required).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "veo-3.1-fast-generate-001"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "1080p"
DEFAULT_OUTPUT = "evidence/cinematic_scene.mp4"

# Veo is served from regional Vertex endpoints only; the "global" endpoint that
# the Gemini text models in this repo use will not route a video request.
DEFAULT_LOCATION = "us-central1"

# Client-side guard so an accidental paste of a whole script is rejected before
# it is charged as a generation. Veo's own prompt limit is smaller than this.
MAX_PROMPT_CHARS = 4000

# Veo accepts a single still as first-frame guidance; only these encodings.
FIRST_FRAME_SUFFIXES = (".png", ".jpg", ".jpeg")

DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_POLL_SECONDS = 10.0


class ScriptError(Exception):
    """Any operator-facing failure; reported on stderr and exits nonzero."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_prompt(prompt: str | None, prompt_file: str | None) -> str:
    """Resolve the prompt from exactly one source and validate it."""
    if (prompt is None) == (prompt_file is None):
        raise ScriptError("provide exactly one of --prompt or --prompt-file")

    if prompt_file is not None:
        path = Path(prompt_file)
        if not path.is_file():
            raise ScriptError(f"prompt file not found: {path}")
        prompt = path.read_text(encoding="utf-8")

    prompt = prompt.strip()
    if not prompt:
        raise ScriptError("prompt is empty")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ScriptError(
            f"prompt is {len(prompt)} characters, over the {MAX_PROMPT_CHARS} limit"
        )
    return prompt


def read_first_frame(first_frame: str | None) -> dict | None:
    """Validate the optional first-frame image and return its manifest entry."""
    if first_frame is None:
        return None

    path = Path(first_frame)
    if not path.exists():
        raise ScriptError(f"first frame not found: {path}")
    if not path.is_file():
        raise ScriptError(f"first frame is not a file: {path}")
    if path.suffix.lower() not in FIRST_FRAME_SUFFIXES:
        raise ScriptError(
            f"first frame must be one of {', '.join(FIRST_FRAME_SUFFIXES)}: {path}"
        )

    data = path.read_bytes()
    if not data:
        raise ScriptError(f"first frame is empty: {path}")

    return {"file": path.name, "size_bytes": len(data), "sha256": _sha256_bytes(data)}


def resolve_target(project: str | None, location: str | None) -> tuple[str, str]:
    """Resolve the Vertex project/location pair, rejecting unusable endpoints."""
    project = (project or os.getenv("GOOGLE_CLOUD_PROJECT") or "").strip()
    if not project:
        raise ScriptError(
            "GOOGLE_CLOUD_PROJECT is not set (or pass --project); "
            "this script uses Vertex AI ADC, not an API key"
        )

    location = (location or os.getenv("GOOGLE_CLOUD_LOCATION") or DEFAULT_LOCATION).strip()
    if location.lower() == "global":
        raise ScriptError(
            f"location 'global' does not serve Veo; use a region such as {DEFAULT_LOCATION}"
        )
    return project, location


def default_client_factory(project: str, location: str):
    """Build a real Vertex AI client. Imported lazily so --dry-run needs no SDK auth."""
    from google import genai

    return genai.Client(vertexai=True, project=project, location=location)


def _await_operation(client, operation, timeout: float, poll_interval: float, sleep):
    deadline = time.monotonic() + timeout
    while not operation.done:
        if time.monotonic() >= deadline:
            name = getattr(operation, "name", None) or "unknown"
            raise ScriptError(
                f"timed out after {timeout:.0f}s waiting for operation {name}; "
                "the generation may still complete server-side"
            )
        sleep(poll_interval)
        operation = client.operations.get(operation)
    return operation


def _extract_video_bytes(operation) -> bytes:
    if operation.error:
        message = operation.error
        if isinstance(message, dict):
            message = message.get("message", message)
        raise ScriptError(f"Veo operation failed: {message}")

    response = operation.response or operation.result
    videos = getattr(response, "generated_videos", None) if response else None
    if not videos:
        reasons = getattr(response, "rai_media_filtered_reasons", None) if response else None
        detail = f": {reasons}" if reasons else ""
        raise ScriptError(f"Veo returned no video (safety filter or empty response){detail}")

    data = videos[0].video.video_bytes
    if not data:
        raise ScriptError(
            "Veo returned a video reference instead of inline bytes; "
            "this script does not read from Cloud Storage"
        )
    return data


def write_artifacts(
    output: Path,
    data: bytes,
    prompt: str,
    model: str,
    operation_name: str | None,
    aspect_ratio: str,
    resolution: str,
    first_frame: dict | None = None,
) -> Path:
    """Write the MP4 plus its adjacent manifest and return the manifest path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)

    manifest_path = output.with_suffix(".json")
    manifest = {
        "model": model,
        "prompt_sha256": _sha256_bytes(prompt.encode("utf-8")),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operation_name": operation_name,
        "output_file": output.name,
        "size_bytes": len(data),
        "sha256": _sha256_bytes(data),
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if first_frame:
        manifest["first_frame"] = first_frame
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_cinematic_scene",
        description="Generate one Veo cinematic scene from an existing storyboard prompt.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="storyboard prompt text")
    source.add_argument("--prompt-file", help="file containing the storyboard prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"default: {DEFAULT_MODEL}")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO)
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT, help=f"MP4 path, default: {DEFAULT_OUTPUT}"
    )
    parser.add_argument(
        "--first-frame",
        help="local PNG/JPEG used as the first frame, for continuity between shots",
    )
    parser.add_argument("--project", help="overrides GOOGLE_CLOUD_PROJECT")
    parser.add_argument(
        "--location", help=f"overrides GOOGLE_CLOUD_LOCATION, default: {DEFAULT_LOCATION}"
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument(
        "--overwrite", action="store_true", help="allow replacing an existing output file"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="validate inputs and exit without calling the API"
    )
    return parser


def run(args, client_factory, sleep) -> None:
    """Validate everything cheap first, then make at most one generation call."""
    prompt = read_prompt(args.prompt, args.prompt_file)
    first_frame = read_first_frame(args.first_frame)
    project, location = resolve_target(args.project, args.location)

    output = Path(args.output)
    if output.exists() and not args.overwrite:
        raise ScriptError(f"{output} already exists; pass --overwrite to replace it")
    if args.timeout <= 0 or args.poll_interval <= 0:
        raise ScriptError("--timeout and --poll-interval must be positive")

    prompt_sha = _sha256_bytes(prompt.encode("utf-8"))
    print(
        f"model={args.model} project={project} location={location} "
        f"aspect_ratio={args.aspect_ratio} resolution={args.resolution} "
        f"prompt_sha256={prompt_sha} output={output}"
    )
    if first_frame:
        print(
            f"first_frame={first_frame['file']} "
            f"first_frame_sha256={first_frame['sha256']}"
        )
    if args.dry_run:
        print("dry run: no API call made")
        return

    from google.genai import types

    client = client_factory(project, location)
    operation = client.models.generate_videos(
        model=args.model,
        source=types.GenerateVideosSource(
            prompt=prompt,
            image=types.Image.from_file(location=args.first_frame)
            if args.first_frame
            else None,
        ),
        config=types.GenerateVideosConfig(
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            number_of_videos=1,
        ),
    )
    print(f"submitted operation {getattr(operation, 'name', None) or 'unknown'}; polling")

    operation = _await_operation(client, operation, args.timeout, args.poll_interval, sleep)
    data = _extract_video_bytes(operation)
    manifest_path = write_artifacts(
        output,
        data,
        prompt,
        args.model,
        getattr(operation, "name", None),
        args.aspect_ratio,
        args.resolution,
        first_frame,
    )
    print(f"wrote {output} ({len(data)} bytes) and {manifest_path}")


def main(argv=None, client_factory=default_client_factory, sleep=time.sleep) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args, client_factory, sleep)
    except ScriptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
