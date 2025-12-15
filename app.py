from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# import compression functions from existing project
from ptII import compress_file, decompress_file

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "dev-secret-key"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route('/log')
def view_log():
    # Serve the project's log.csv file (if present) so the UI can open it reliably
    log_path = os.path.join(BASE_DIR, 'log.csv')
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=False)
    # fallback: try static folderc:\UNI DATA\CP\1) DSA(Data_Structure_Algorithm)\File Compressor
    static_log = os.path.join(BASE_DIR, 'static', 'log.csv')
    if os.path.exists(static_log):
        return send_file(static_log, as_attachment=False)
    flash('Log file not found')
    return redirect(url_for('index'))


@app.route("/compress", methods=["POST"])
def compress():
    if "file" not in request.files:
        flash("No file part in the request")
        return redirect(url_for("index"))

    f = request.files["file"]
    if f.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    filename = secure_filename(f.filename)
    saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(saved_path)

    # call existing compress function
    try:
        stats = compress_file(saved_path)
    except Exception as e:
        flash(f"Compression failed: {e}")
        return redirect(url_for("index"))

    compressed_path = stats.get("compressed_file") if isinstance(stats, dict) else None
    if compressed_path is None:
        flash("Compression completed but no output file was returned by the compressor.")
        return redirect(url_for("index"))

    # Ensure compressed file exists
    if not os.path.exists(compressed_path):
        # The compressor might have written to current working dir; try to resolve by name
        possible = os.path.join(BASE_DIR, os.path.basename(compressed_path))
        if os.path.exists(possible):
            compressed_path = possible
        else:
            flash("Compressed file not found on disk.")
            return redirect(url_for("index"))

    return render_template("result.html", action="compress", stats=stats, file_url=url_for("download", filename=os.path.basename(compressed_path)))


@app.route("/decompress", methods=["POST"])
def decompress():
    if "file" not in request.files:
        flash("No file part in the request")
        return redirect(url_for("index"))

    f = request.files["file"]
    if f.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    filename = secure_filename(f.filename)
    saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(saved_path)

    try:
        result = decompress_file(saved_path)
    except Exception as e:
        flash(f"Decompression failed: {e}")
        return redirect(url_for("index"))

    if not result:
        flash("Decompression did not produce an output file.")
        return redirect(url_for("index"))

    output_file = result.get("output_file")
    if not output_file or not os.path.exists(output_file):
        # try to locate in project dir
        possible = os.path.join(BASE_DIR, os.path.basename(output_file) if output_file else "")
        if os.path.exists(possible):
            output_file = possible
        else:
            flash("Decompressed output not found on disk.")
            return redirect(url_for("index"))

    return render_template("result.html", action="decompress", stats=result, file_url=url_for("download", filename=os.path.basename(output_file)))


@app.route("/download/<path:filename>")
def download(filename):
    # Allow downloading from base project dir and uploads folder
    candidates = [app.config["UPLOAD_FOLDER"], BASE_DIR]
    for base in candidates:
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return send_file(candidate, as_attachment=True)
    flash("File not found")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
