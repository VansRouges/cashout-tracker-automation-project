import pandas as pd


def read_csv_to_df(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    return df


def df_to_values(df):
    return [df.columns.tolist()] + df.fillna('').astype(str).values.tolist()


def compute_summary_table(df):
    """Return a list-of-lists summary table suitable for writing to Sheets."""
    # Ensure numeric balance
    df = df.copy()
    if 'balance' in df.columns:
        df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
    else:
        df['balance'] = 0

    total_balance = df['balance'].sum()
    payment_counts = df['payment_status'].value_counts().to_dict() if 'payment_status' in df.columns else {}
    account_type_counts = df['account_type'].value_counts().to_dict() if 'account_type' in df.columns else {}
    avg_balance_by_type = df.groupby('account_type')['balance'].mean().round(2).to_dict() if 'account_type' in df.columns else {}

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
