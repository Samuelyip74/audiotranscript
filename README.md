# Audio Transcript App

Simple Python app to transcribe `.mp3`, `.mp4`, `.m4v`, and `.m4a` files using OpenAI Whisper.

## Features
- Read audio/video files: `.mp3`, `.mp4`, `.m4v`, `.m4a`
- Transcribe file content to text
- Choose language (`auto` detect or specific language code like `en`, `es`)
- Choose input file
- Choose output transcript file

## Prerequisites
- Python 3.10+
- `ffmpeg` installed and available in your PATH

## Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
Interactive mode (file pickers for input/output):
```powershell
python .\app.py
```

With arguments:
```powershell
python .\app.py -i ".\meeting.mp3" -o ".\transcript.txt" -l en -m base
```

## CLI Options
- `-i, --input`: Input file path (`.mp3`, `.mp4`, `.m4v`, `.m4a`)
- `-o, --output`: Output text file path
- `-l, --language`: Language code (`auto`, `en`, `es`, etc.)
- `-m, --model`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`)
