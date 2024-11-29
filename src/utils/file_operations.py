#utils/file_operations.py

import pandas as pd

def read_csv(file_path):
    return pd.read_csv(file_path)

def save_to_csv(df, file_path):
    df.to_csv(file_path, index=False)

def read_categories(file_path):
    with open(file_path, 'r') as file:
        categories = [line.strip() for line in file.readlines() if line.strip() != '']
    return categories

def read_postcodes(file_path):
    extension = file_path.split('.')[-1].lower()
    if extension == 'txt':
        df = pd.read_csv(file_path, delimiter="\r\n", header=None, names=['postcode'])
    elif extension == 'csv':
        df = pd.read_csv(file_path)
    elif extension == 'xlsx':
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Not supported")
    return df
