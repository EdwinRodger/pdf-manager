import os
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import random
import string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = "/app/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Create uploads directory if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_file_locally(file, filename):
    """Save file to local storage"""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    return file_path


def get_pdf_files():
    """Get all PDF files from uploads directory, sorted alphabetically"""
    pdf_files = []
    upload_folder = app.config["UPLOAD_FOLDER"]

    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path) and allowed_file(filename):
                pdf_files.append(filename)

    return sorted(pdf_files)


@app.route("/")
def index():
    """Render the main page"""
    pdf_files = get_pdf_files()
    return render_template("index.html", pdf_files=pdf_files)


@app.route("/api/pdfs", methods=["GET"])
def get_pdfs():
    """API endpoint to get list of PDF files"""
    pdf_files = get_pdf_files()
    return jsonify({"pdfs": pdf_files})


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit(".", 1)[1].lower()
    # Generate a random 5-letter filename (using lowercase letters and digits)
    random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    unique_filename = f"{random_part}.{file_extension}"

    try:
        # Save file to local storage
        file.seek(0)
        save_file_locally(file, unique_filename)

        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "filename": unique_filename,
                    "download_url": f"/download/{unique_filename}",
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500


@app.route("/download/<filename>")
def download_file(filename):
    """Handle file download"""
    # Sanitize filename
    filename = secure_filename(filename)

    # Download from local storage
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        return send_file(
            file_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
