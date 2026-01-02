# PDF Upload & Download Flask App

A simple Flask application for uploading and downloading PDF files with support for both local storage and Amazon S3.

## Features

- Upload PDF files via web interface
- Download PDF files by filename
- Automatic S3 integration when AWS credentials are provided
- Falls back to local storage when S3 credentials are not available
- Modern UI with Tailwind CSS

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up AWS S3 credentials as environment variables:
```bash
# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_REGION=us-east-1
set S3_BUCKET_NAME=your_bucket_name

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_REGION="us-east-1"
$env:S3_BUCKET_NAME="your_bucket_name"

# Linux/Mac
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
export S3_BUCKET_NAME=your_bucket_name
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Web Interface

- **Upload**: 
  - Click to select a PDF file, or drag and drop a PDF file into the upload area
  - Click "Upload PDF" button
  - The file will be stored either in S3 (if credentials are provided) or locally in the `uploads` folder
- **Download**: Enter the filename (as returned after upload) and click "Download" to retrieve the file.

### Testing the API

You can test the API directly using one of these methods:

#### Using Python (test_api.py)
```bash
python test_api.py path/to/your/file.pdf
```

#### Using curl (Linux/Mac/Git Bash)
```bash
# Upload
curl -X POST -F "file=@path/to/your/file.pdf" http://localhost:5000/upload

# Download (replace FILENAME with the filename returned from upload)
curl -O -J http://localhost:5000/download/FILENAME
```

#### Using PowerShell (Windows)
```powershell
# Upload
$form = @{file = Get-Item "path\to\your\file.pdf"}
Invoke-RestMethod -Uri "http://localhost:5000/upload" -Method Post -Form $form

# Download
Invoke-WebRequest -Uri "http://localhost:5000/download/FILENAME" -OutFile "downloaded_file.pdf"
```

#### Using test_api.ps1 (Windows PowerShell)
```powershell
.\test_api.ps1 path\to\your\file.pdf
```

## Storage Behavior

- If AWS credentials are provided: Files are uploaded to and downloaded from Amazon S3
- If AWS credentials are not provided: Files are stored locally in the `uploads` folder

## File Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Web interface
├── uploads/           # Local storage folder (created automatically)
├── test_api.py        # Python test script for API
├── test_api.sh        # Bash test script for API (Linux/Mac)
└── test_api.ps1       # PowerShell test script for API (Windows)
```

