import pandas as pd

# Load the Excel file
file_path = '31.01.24 Wed.xlsx'
df = pd.read_excel(file_path, engine='openpyxl', skiprows=4, usecols="A,C")

# Step 1: Remove rows where both columns (A and C here represented as 0 and 1) are NaN
df.dropna(how='all', inplace=True)

# Step 22 Fill NaN values in the first column (A) with the value from the previous row, for cases where A is NaN but C is not
df = df.fillna(method='ffill')

df = df.drop_duplicates(subset=df.columns[1])

df = df.dropna(subset=[df.columns[1]])

df = df.reset_index(drop=True)