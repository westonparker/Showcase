import pandas as pd

# Load CSV file
csv_file = 'input.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Save to Excel file
excel_file = 'output.xlsx'  # Replace with your desired output path
df.to_excel(excel_file, index=False)

print(f"Converted '{csv_file}' to '{excel_file}'")
