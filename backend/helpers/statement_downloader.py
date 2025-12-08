# save as download_gmail_pdfs_gmail_api.py
import os
import base64
import re
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes

# 1) Config
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  # readonly is enough to download attachments
CREDENTIALS_FILE = 'credentials.json'  # from Google Cloud Console
TOKEN_FILE = 'token.json'
OUTPUT_DIR = Path('downloaded_pdfs')
QUERY = 'has:attachment filename:pdf "Statement"'  # tweak as needed

OUTPUT_DIR.mkdir(exist_ok=True)

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=58497)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def download_attachments():
    service = get_gmail_service()
    resp = service.users().messages().list(userId='me', q=QUERY, maxResults=500).execute()
    messages = resp.get('messages', [])
    print(f'Found {len(messages)} message(s) matching query.')
    for msg_meta in messages:
        msg = service.users().messages().get(userId='me', id=msg_meta['id'], format='raw').execute()
        raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        em = message_from_bytes(raw)
        subject = em.get('Subject','(no-subject)')
        date = em.get('Date','')
        # walk parts for attachments
        for part in em.walk():
            content_disposition = part.get('Content-Disposition','')
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if filename and filename.lower().endswith('.pdf'):
                data = part.get_payload(decode=True)
                safe_name = re.sub(r'[\\/:"*?<>|]+','_', filename)
                out_path = OUTPUT_DIR / f"{safe_name}"
                with open(out_path, 'wb') as f:
                    f.write(data)
                print(f"Saved: {out_path} (Subject: {subject})")

if __name__ == '__main__':
    download_attachments()
