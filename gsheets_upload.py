"""Upload data.csv to a Google Sheet using a service account.

Usage:
  - Ensure .env contains GOOGLE_CREDENTIALS_FILE and GOOGLE_SHEET_ID
  - Share the Google Sheet with the service account email from credentials.json
  - Run:
    C:/Users/evans/Coding/python-projects/cashout-tracker/venv/Scripts/python.exe gsheets_upload.py
"""
import os
import logging
from dotenv import load_dotenv
import pandas as pd

from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment
load_dotenv()
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data.csv')


def validate():
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID not set in environment (.env)")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")


def build_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    return service


def read_csv_values(csv_path):
    # Allow spaces after commas and normalize column names
    df = pd.read_csv(csv_path, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    # Convert all values to strings so Google Sheets accepts them
    values = [df.columns.tolist()] + df.fillna('').astype(str).values.tolist()
    return values


def compute_summary(csv_path):
    """Compute summary statistics from the CSV and return as a list of lists for Sheets."""
    df = pd.read_csv(csv_path, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Ensure numeric balance
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)

    total_balance = df['balance'].sum()
    payment_counts = df['payment_status'].value_counts().to_dict()
    account_type_counts = df['account_type'].value_counts().to_dict()
    avg_balance_by_type = df.groupby('account_type')['balance'].mean().round(2).to_dict()

    # Build a simple human-readable table for Google Sheets
    table = []
    table.append(['Metric', 'Value'])
    table.append(['Total balance', f"{total_balance:.2f}"])

    table.append(['', ''])
    table.append(['Payment status', 'Count'])
    for k, v in payment_counts.items():
        table.append([k, str(v)])

    table.append(['', ''])
    table.append(['Account type', 'Count'])
    for k, v in account_type_counts.items():
        table.append([k, str(v)])

    table.append(['', ''])
    table.append(['Account type', 'Average balance'])
    for k, v in avg_balance_by_type.items():
        table.append([k, f"{v:.2f}"])

    return table


def upload_values(service, spreadsheet_id, values, range_name='Sheet1!A1'):
    body = {'values': values}
    result = (
        service.spreadsheets()
        .values()
        .update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW', body=body)
        .execute()
    )
    return result


def clear_range(service, spreadsheet_id, range_name):
    body = {}
    result = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name, body=body).execute()
    return result


def ensure_sheet_exists(service, spreadsheet_id, sheet_title):
    """Create a sheet/tab with sheet_title if it does not already exist."""
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = meta.get('sheets', [])
    titles = [s.get('properties', {}).get('title') for s in sheets]
    if sheet_title in titles:
        return
    requests = [{
        'addSheet': {
            'properties': {'title': sheet_title}
        }
    }]
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


if __name__ == '__main__':
    try:
        logging.info('Validating configuration...')
        validate()

        logging.info('Building Sheets service...')
        service = build_sheets_service()

        logging.info(f'Reading CSV from {CSV_PATH}...')
        values = read_csv_values(CSV_PATH)

        logging.info('Uploading data to Google Sheet...')
        resp = upload_values(service, GOOGLE_SHEET_ID, values)
        logging.info('Upload complete: %s', resp)
        logging.info('Compute summary analytics...')
        summary_table = compute_summary(CSV_PATH)

        # Write summary to a separate sheet named 'Summary'
        summary_sheet = 'Summary'
        summary_range = f"{summary_sheet}!A1"
        try:
            logging.info('Ensuring Summary sheet exists...')
            ensure_sheet_exists(service, GOOGLE_SHEET_ID, summary_sheet)
            logging.info('Clearing existing Summary sheet range...')
            clear_range(service, GOOGLE_SHEET_ID, summary_sheet)
        except Exception:
            logging.debug('Could not clear or create Summary sheet; proceeding to write.')

        logging.info('Writing summary to sheet...')
        summary_resp = upload_values(service, GOOGLE_SHEET_ID, summary_table, range_name=summary_range)
        logging.info('Summary write complete: %s', summary_resp)

        logging.info('Verify the Google Sheet to confirm rows and summary were written.')

    except Exception as e:
        logging.exception('Unexpected error during upload:')
        raise
