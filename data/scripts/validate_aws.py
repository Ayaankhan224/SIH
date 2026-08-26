from pathlib import Path
import csv
from datetime import datetime

INPUT_FILE = Path("data/processed/aws_clean_2012.csv")

def validate_aws_data():
  """to validate the cleaned file for any errors, any typo, any stuff not required"""

  print(f"Reading: {INPUT_FILE}\n")

  with INPUT_FILE.open("r",encoding="utf-8") as file:

    reader = csv.DictReader(file) #reads the csv file
    rows = list(reader) #stores rows

  print("-"*50)
  print("AWS DATA VISUALIZATION")
  print("-"*50)


  #NUMBER OF RECORDS
  print(f"\nTotal Rows: {len(rows)}")

  #REQUIRED COLUMNS
  required_columns = [
    "obstime",
    "tempr",
    "rh",
    "ws",
    "wd",
    "ap"
  ]
  print(f"Checking columns:")

  #checks if any columns that humko chahiye are not present
  missing_columns = [
    column 
    for column in required_columns
    if column not in reader.fieldnames
  ]

  if missing_columns:
    print(f"ERROR: Missing Columns: {missing_columns}")
  else:
    print("Ok: All required columns are present")

  #MISSING VALUES
  print(f"\nChecking missing values:")

  for column in required_columns:
    missing = sum(
      1
      for row in rows
      if not row[column].strip()
    ) #shorthand for counter, if koi value nahi milegi ("not strip" wali line) then counter +1 krega

    print(f"{column}: {missing} missing")

  

if __name__ == '__main__':
  validate_aws_data()