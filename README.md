# PDF Upload & Download Flask App

A simple Flask application for uploading and downloading PDF files with local storage.

## Features

- Upload PDF files via web interface (click or drag-and-drop)
- Download PDF files by filename
- Modern UI with Tailwind CSS
- Docker support for easy deployment

## Local Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

### Web Interface

- **Upload**: 
  - Click to select a PDF file, or drag and drop a PDF file into the upload area
  - Click "Upload PDF" button
  - Files are stored locally in the `uploads` folder
- **Download**: Enter the filename (as returned after upload) and click "Download" to retrieve the file.

### Testing the API

You can test the API directly using curl:

```bash
# Upload
curl -X POST -F "file=@path/to/your/file.pdf" http://localhost:5000/upload

# Download (replace FILENAME with the filename returned from upload)
curl -O -J http://localhost:5000/download/FILENAME
```

## Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t pdf-manager .

# Run the container
docker run -p 3000:3000 -e PORT=3000 pdf-manager
```

### Deploy to Coolify

1. Push your code to a Git repository (GitHub, GitLab, etc.)

2. In Coolify:
   - Create a new application
   - Connect your Git repository
   - Coolify will automatically detect the Dockerfile
   - Set the port to `3000` (or use the PORT environment variable)
   - Deploy!

3. Environment Variables (optional):
   - `PORT`: Port to run the application (default: 3000)
   - `FLASK_DEBUG`: Set to `true` for debug mode (default: false)

**Note**: Files uploaded in Coolify will be stored in the container's `uploads` folder. For persistent storage, consider mounting a volume or using a database/file storage service.

## File Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .dockerignore      # Files to exclude from Docker build
├── templates/
│   └── index.html     # Web interface
└── uploads/           # Local storage folder (created automatically)
```

## Storage

Files are stored locally in the `uploads` folder. Each uploaded file gets a unique random 5-character filename to prevent conflicts.
