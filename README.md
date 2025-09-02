# Cashout Tracker

A small Python project that reads mock financial account data and uploads it to Google Sheets, with summary analytics.

Requirements
- Python 3.8+
- A Google Cloud service account with Sheets API enabled

Setup
1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a service account in Google Cloud, enable the Google Sheets API, and download the JSON key. Save it as `credentials.json` in the project root.

4. Create a Google Sheet and share it with the service account email (found inside `credentials.json`).

5. Copy the Sheet ID (the part between `/d/` and `/edit` in the sheet URL) and add it to the `.env` file as `GOOGLE_SHEET_ID`.

Usage

```powershell
C:/Users/evans/Coding/python-projects/cashout-tracker/venv/Scripts/python.exe gsheets_upload.py
```

What the script does
- Reads `data.csv` in the project root
- Appends rows to `Sheet1` in the configured Google Sheet
- Computes summary analytics and writes them to a `Summary` tab
- Applies simple formatting to the `Summary` sheet

Notes
- Keep `credentials.json` out of version control (it's in `.gitignore`).
- Use `.env.example` as a template for environment variables.
