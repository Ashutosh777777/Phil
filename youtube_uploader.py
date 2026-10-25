"""
YouTube upload + scheduling for Phil.

First run (interactive, once):
    python3 youtube_uploader.py --auth
This opens a browser sign-in and saves token.json. After that, uploads run
unattended and the token refreshes itself.

Videos are uploaded as private with a `publishAt` time; YouTube itself flips
them to public at that moment, so your PC does not need to be on then.
"""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"
UPLOAD_LOG = "upload_log.jsonl"


def get_service():
    # Imported here so the rest of the pipeline works without the Google libs installed.
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"{CLIENT_SECRET_FILE} not found. Create a Desktop-app OAuth client "
                    "in Google Cloud Console and save it here."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            # In WSL the browser may not open automatically; the URL is printed.
            creds = flow.run_local_server(port=0, open_browser=False)
        Path(TOKEN_FILE).write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def file_fingerprint(path):
    """Hash of the file contents, used to avoid uploading the same video twice."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def already_uploaded(fingerprint):
    if not os.path.exists(UPLOAD_LOG):
        return None
    with open(UPLOAD_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("sha1") == fingerprint:
                return entry
    return None


def log_upload(path, fingerprint, video_id, title, publish_at):
    entry = {
        "file": str(path),
        "sha1": fingerprint,
        "video_id": video_id,
        "title": title,
        "publish_at": publish_at.isoformat() if publish_at else None,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(UPLOAD_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def upload_video(path, title, description, publish_at=None, tags=None, force=False):
    """
    Upload one video. If `publish_at` (timezone-aware datetime) is given the
    video is uploaded private and goes public at that time.
    Returns the YouTube video id, or the existing id if this exact file was
    already uploaded (unless force=True).
    """
    from googleapiclient.http import MediaFileUpload

    fingerprint = file_fingerprint(path)
    previous = None if force else already_uploaded(fingerprint)
    if previous:
        print(f"Skipping {path}: already uploaded as https://youtu.be/{previous['video_id']} "
              "(use --force to upload again)")
        return previous["video_id"]

    status = {"selfDeclaredMadeForKids": False}
    if publish_at is not None:
        if publish_at.tzinfo is None:
            raise ValueError("publish_at must be timezone-aware")
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    else:
        status["privacyStatus"] = "public"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": "27",  # Education
        },
        "status": status,
    }

    request = get_service().videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(path), chunksize=-1, resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    log_upload(path, fingerprint, video_id, title, publish_at)
    return video_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube uploader for Phil")
    parser.add_argument("--auth", action="store_true",
                        help="Run the one-time sign-in and save token.json")
    args = parser.parse_args()
    if args.auth:
        get_service()
        print(f"Signed in. Credentials saved to {TOKEN_FILE}")
    else:
        parser.print_help()
