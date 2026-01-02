import os
import uuid
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import random
import string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# S3 Configuration (optional)
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# Create uploads directory if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize S3 client if credentials are provided
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        print("S3 client initialized successfully")
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        s3_client = None
else:
    print("S3 credentials not provided. Using local storage.")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def upload_to_s3(file, filename):
    """Upload file to S3 bucket"""
    if not s3_client or not S3_BUCKET_NAME:
        return False

    try:
        s3_client.upload_fileobj(
            file, S3_BUCKET_NAME, filename, ExtraArgs={"ContentType": "application/pdf"}
        )
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error uploading to S3: {e}")
        return False


def download_from_s3(filename):
    """Download file from S3 bucket"""
    if not s3_client or not S3_BUCKET_NAME:
        return None

    try:
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        return file_obj["Body"]
    except ClientError as e:
        print(f"Error downloading from S3: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading from S3: {e}")
        return None


def save_file_locally(file, filename):
    """Save file to local storage"""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    return file_path


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")


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
        # Try to upload to S3 if available
        if s3_client and S3_BUCKET_NAME:
            # Reset file pointer to beginning
            file.seek(0)
            if upload_to_s3(file, unique_filename):
                return (
                    jsonify(
                        {
                            "message": "File uploaded successfully to S3",
                            "filename": unique_filename,
                            "download_url": f"/download/{unique_filename}",
                        }
                    ),
                    200,
                )

        # Fallback to local storage
        file.seek(0)
        save_file_locally(file, unique_filename)

        return (
            jsonify(
                {
                    "message": "File uploaded successfully to local storage",
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

    # Try to download from S3 first
    if s3_client and S3_BUCKET_NAME:
        file_obj = download_from_s3(filename)
        if file_obj:
            return send_file(
                file_obj,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=filename,
            )

    # Fallback to local storage
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
    app.run(debug=True)
