from __future__ import annotations

import argparse
import os
import shutil
import time
from glob import glob
from pathlib import Path
from tkinter import Tk, filedialog


SUPPORTED_INPUT_EXTENSIONS = {".mp3", ".mp4", ".m4v", ".m4a"}
COMMON_LANGUAGES = {
    "auto": "Auto-detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio/video files with Whisper.")
    parser.add_argument("-i", "--input", type=str, help="Input file path (.mp3, .mp4, .m4v, .m4a)")
    parser.add_argument("-o", "--output", type=str, help="Output transcript path (.txt)")
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="auto",
        help="Language code (e.g., en, es) or 'auto' for auto-detect",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="base",
        help="Whisper model size: tiny, base, small, medium, large",
    )
    return parser.parse_args()


def pick_input_file() -> Path:
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Choose audio/video file",
        filetypes=[
            ("Supported files", "*.mp3 *.mp4 *.m4v *.m4a"),
            ("MP3 files", "*.mp3"),
            ("MP4 files", "*.mp4"),
            ("M4V files", "*.m4v"),
            ("M4A files", "*.m4a"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    if not file_path:
        raise ValueError("No input file selected.")
    return Path(file_path)


def pick_output_file(default_stem: str) -> Path:
    root = Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Choose transcript output file",
        defaultextension=".txt",
        initialfile=f"{default_stem}_transcript.txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    root.destroy()
    if not file_path:
        raise ValueError("No output file selected.")
    return Path(file_path)


def choose_language(default: str = "auto") -> str:
    print("\nChoose transcript language:")
    for code, label in COMMON_LANGUAGES.items():
        print(f"  {code:>4} - {label}")
    print("  <any> - Enter another Whisper language code manually")

    selected = input(f"Language [{default}]: ").strip().lower()
    if not selected:
        selected = default
    return selected


def validate_input_file(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}. "
            f"Use one of: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))}"
        )


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg"):
        return

    candidates: list[Path] = []

    # Common Windows locations, including Winget FFmpeg install.
    if os.environ.get("LOCALAPPDATA"):
        winget_pattern = (
            Path(os.environ["LOCALAPPDATA"])
            / "Microsoft"
            / "WinGet"
            / "Packages"
            / "Gyan.FFmpeg*"
            / "ffmpeg-*"
            / "bin"
        )
        candidates.extend(Path(p) for p in glob(str(winget_pattern)))

    candidates.extend(
        [
            Path(r"C:\ffmpeg\bin"),
            Path(r"C:\Program Files\ffmpeg\bin"),
        ]
    )

    for candidate in candidates:
        ffmpeg_exe = candidate / "ffmpeg.exe"
        if ffmpeg_exe.exists():
            os.environ["PATH"] = f"{candidate}{os.pathsep}{os.environ.get('PATH', '')}"
            if shutil.which("ffmpeg"):
                return

    raise FileNotFoundError(
        "ffmpeg was not found. Install it and reopen your IDE terminal, or add ffmpeg/bin to PATH."
    )


def transcribe_file(input_path: Path, output_path: Path, language: str, model_name: str) -> None:
    import whisper

    ensure_ffmpeg_available()
    use_language = None if language == "auto" else language
    print(f"\nLoading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {input_path}")
    print("Transcription in progress... (CPU mode can take several minutes for long files)")
    started_at = time.time()
    result = model.transcribe(str(input_path), language=use_language, verbose=True)
    transcript = result.get("text", "").strip()
    output_path.write_text(transcript + "\n", encoding="utf-8")
    elapsed = time.time() - started_at
    print(f"Transcript saved to: {output_path}")
    print(f"Done in {elapsed:.1f} seconds.")


def main() -> None:
    args = parse_args()

    try:
        input_path = Path(args.input) if args.input else pick_input_file()
        validate_input_file(input_path)

        language = args.language.strip().lower() if args.language else "auto"
        if language == "auto" and not args.language:
            language = choose_language(default="auto")

        output_path = Path(args.output) if args.output else pick_output_file(input_path.stem)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        transcribe_file(
            input_path=input_path,
            output_path=output_path,
            language=language,
            model_name=args.model.strip().lower(),
        )
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
