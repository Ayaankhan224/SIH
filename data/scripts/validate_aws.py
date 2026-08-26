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

  #MISSING TIMESTAMPS
  print("\nChecking timestamps:")

  timestamps = []
  invalid_timestamps = 0

  for row in rows:
    try:
      timestamp = datetime.strptime(
          row["obstime"],
          "%Y-%m-%d %H:%M:%S"
      ) #stores all timestamps

      timestamps.append(timestamp)

    #invalid timesramps
    except ValueError:
      invalid_timestamps += 1

  print(f"Valid timestamps: {len(timestamps)}")
  print(f"Invalid timestamps: {invalid_timestamps}")
    
  
  #DUPLICATE TIMESTAMPS
  print("\nChecking duplicate timestamps:")

  duplicates = len(timestamps) - len(set(timestamps)) #supposedly ye equation duplicates deta but i've no idea how this works YET

  print(f"Duplicate timestamps: {duplicates}")

  
  #NUMERIC VALIDATION
  print("\nChecking numeric values...")

  numeric_columns = [
    "tempr",
    "rh",
    "ws",
    "wd",
    "ap"
  ]

  for column in numeric_columns:
    invalid = 0

    for row in rows:
      try:
        float(row[column]) #tries converting every value to float, if ho gaya then it means wo valid hai if it cannot i.e. error dega toh iska mtlb it isnt a number 
      except (ValueError, TypeError):#rather than exiting with a error message ye code ko chalta rkhega
        invalid += 1

    print(f"{column}: {invalid} invalid values")

  
  #RELATIVE HUMIDITY RANGE
  print("\nChecking humidity range:")

  invalid_humidity = 0

  for row in rows:
    try:
      humidity = float(row["rh"]) #converts to float taaki checking easier ho

      if humidity < 0 or humidity > 100: #invalid range (if humidity < 0 toh obv invalid)
        invalid_humidity += 1

    except ValueError:
      pass

  print(f"Humidity outside 0-100%: {invalid_humidity}")

  
  #TIMESTAMP CONTINUITY i.e. koi gaps toh nahi timestamps me
  print("\nChecking hourly continuity:")

  timestamps.sort()
  gaps = 0

  for previous, current in zip(
      timestamps,
      timestamps[1:]
  ):

    difference = current - previous 

    if difference.total_seconds() != 3600:
      gaps += 1

  print(f"Non-hourly gaps: {gaps}")

  
  #DATE RANGE
  if timestamps:
    print("\nDataset range:")

    print(
      f"First observation: {timestamps[0]}"
    )

    print(
      f"Last observation:  {timestamps[-1]}"
    )

  print("VALIDATION COMPLETE")

if __name__ == "__main__":
    validate_aws_data()
