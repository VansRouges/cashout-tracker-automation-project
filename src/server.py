import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from data_processing import read_csv_to_df, df_to_values, compute_summary_table
from sheets_client import build_service, ensure_sheet_exists, append_values, update_values, clear_range, batch_update

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class CSVChangeHandler(FileSystemEventHandler):
    def __init__(self, csv_path, service, spreadsheet_id):
        self.csv_path = csv_path
        self.service = service
        self.spreadsheet_id = spreadsheet_id

    def on_modified(self, event):
        if event.src_path.endswith(self.csv_path):
            logging.info('Detected change in CSV; syncing to Google Sheets...')
            df = read_csv_to_df(self.csv_path)
            values = df_to_values(df)
            append_values(self.service, self.spreadsheet_id, values)


def run_watcher(csv_path, credentials_file, spreadsheet_id):
    service = build_service(credentials_file)
    ensure_sheet_exists(service, spreadsheet_id, 'Sheet1')
    ensure_sheet_exists(service, spreadsheet_id, 'Summary')

    event_handler = CSVChangeHandler(csv_path, service, spreadsheet_id)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    logging.info('Watching %s for changes. Press Ctrl+C to stop.', csv_path)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
