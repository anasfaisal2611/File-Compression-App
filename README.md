# RAMZ — Flask front-end for Huffman compression

This project contains a Huffman compression implementation and a modern Flask UI called RAMZ (previously "Huffman File Compressor"). The UI includes a splash screen, light/dark theme toggle, drag-and-drop file upload, and basic quick actions.

Files of interest:

- `app.py` — Flask application exposing `/` (index), `/compress`, `/decompress`, and `/download/<filename>` routes.
- `templates/index.html` — modern UI with splash screen, theme toggle, and upload forms.
- `templates/result.html` — shows operation results and download link.
- `static/style.css` — theme-aware styles (dark/light) and UI effects.
- `static/script.js` — handles splash, theme toggle, drag/drop, and file-info display.
- `requirements.txt` — minimal Python dependencies.

How to run

1. (Recommended) Create and activate a virtualenv.

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Start the app from the project folder:

```powershell
python app.py
```

4. Open http://127.0.0.1:5000 in your browser.

# RAMZ — Flask front-end for Huffman compression

RAMZ is a small Flask app that wraps an existing Huffman compression implementation and provides a modern browser UI for compressing and decompressing files.

Repository highlights
- `app.py` — Flask application exposing `/`, `/compress`, `/decompress`, `/download/<filename>` and `/log` routes.
- `ptII.py` / `DSA.py` — compression/decompression implementation (Huffman + file I/O).
- `templates/` — Jinja2 templates (`index.html`, `result.html`).
- `static/` — styles and client JS (`style.css`, `script.js`).
- `test_app.py` — a small smoke test that exercises the main routes via Flask's test client.

Prerequisites
- Python 3.8 or newer (3.10/3.11 recommended)
- Windows PowerShell (instructions below use PowerShell)

Install dependencies (PowerShell)
```powershell
# create a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the application
```powershell
# from the project root (ensure venv is active)
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

Uploads and outputs
- Uploaded files are saved to the `uploads/` folder in the project root.
- The compressor may write output files into the project root; the UI attempts to resolve and serve the produced files. If you'd like, I can force all outputs into `uploads/` for consistency.

Run the smoke test (optional)
```powershell
python test_app.py
```
This creates a small `sample.txt` if missing, exercises the compress/decompress routes, and prints simple pass/fail output.

Notes & troubleshooting
- If PowerShell blocks virtualenv activation, run as Administrator and execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
- If port 5000 is in use, edit `app.py` to change the host/port or run behind a WSGI server.
- If you see missing dependency errors, re-run `pip install -r requirements.txt` inside the activated venv.

Contact
- Syed Mehdi — GitHub: https://github.com/smmehdi23

If you want, I can add a small `run.ps1` helper to automate activation + start or add Docker support.
