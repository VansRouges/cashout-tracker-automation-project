from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def build_service(credentials_file):
    creds = service_account.Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service


def ensure_sheet_exists(service, spreadsheet_id, sheet_title):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = meta.get('sheets', [])
    titles = [s.get('properties', {}).get('title') for s in sheets]
    if sheet_title in titles:
        return
    requests = [{'addSheet': {'properties': {'title': sheet_title}}}]
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def append_values(service, spreadsheet_id, values, range_name='Sheet1'):
    body = {'values': values}
    return service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()


def update_values(service, spreadsheet_id, values, range_name='Sheet1!A1'):
    body = {'values': values}
    return service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()


def clear_range(service, spreadsheet_id, range_name):
    body = {}
    return service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name, body=body).execute()


def get_sheet_values(service, spreadsheet_id, range_name):
    resp = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return resp.get('values', [])


def batch_update(service, spreadsheet_id, requests):
    body = {'requests': requests}
    return service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def format_summary_sheet(service, spreadsheet_id, sheet_title, num_rows):
    """Apply simple formatting to the Summary sheet: bold header and number format for the Value column."""
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = meta.get('sheets', [])
    sheet = next((s for s in sheets if s.get('properties', {}).get('title') == sheet_title), None)
    if not sheet:
        return
    sheet_id = sheet.get('properties', {}).get('sheetId')

    requests = []
    # Bold the first row (header)
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1,
                'startColumnIndex': 0,
                'endColumnIndex': 2,
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True}
                }
            },
            'fields': 'userEnteredFormat.textFormat.bold'
        }
    })

    # Apply number format to the Value column (column B, index 1)
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': num_rows,
                'startColumnIndex': 1,
                'endColumnIndex': 2,
            },
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {
                        'type': 'NUMBER',
                        'pattern': '#,##0.00'
                    }
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    })

    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
