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

# local helpers
from src.data_processing import read_csv_to_df, df_to_values, compute_summary_table
from src.sheets_client import build_service, ensure_sheet_exists, append_values, update_values, clear_range, batch_update, update_values as upload_values

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load environment
load_dotenv()
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data.csv')


def validate():
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID not set in environment (.env)")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")


if __name__ == '__main__':
    try:
        logging.info('Validating configuration...')
        validate()

        logging.info('Building Sheets service...')
        service = build_service(GOOGLE_CREDENTIALS_FILE)

        logging.info(f'Reading CSV from {CSV_PATH}...')
        df = read_csv_to_df(CSV_PATH)
        values = df_to_values(df)

        logging.info('Appending data to Google Sheet (Sheet1)...')
        resp = append_values(service, GOOGLE_SHEET_ID, values)
        logging.info('Append complete: %s', resp)

        logging.info('Compute summary analytics...')
        summary_table = compute_summary_table(df)

        # Ensure Summary exists and write
        summary_sheet = 'Summary'
        summary_range = f"{summary_sheet}!A1"
        try:
            ensure_sheet_exists(service, GOOGLE_SHEET_ID, summary_sheet)
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
