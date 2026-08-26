from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/processed/aws_clean_2012.csv")
OUTPUT_FILE = Path("data/processed/aws_normalized_2012.csv")

"""ye script data transform karegi. currently data is stored under 'obstime','rh','wd', not understandable bekar. This scritp will convert it into readable usable headings"""
def normalize_aws_data():
  print(f"Reading: {INPUT_FILE}")

  #is baar we are reading the csv using pandas because pandas has some functionns like rename function or converting to datetime format wala function, very useful n easy
  df = pd.read_csv(INPUT_FILE)

  #renaming
  df = df.rename(columns={
    "obstime": "timestamp",
    "tempr": "temperature",
    "rh": "humidity",
    "ws": "wind_speed",
    "wd": "wind_direction",
    "ap": "pressure"
  })

  #converting timestamps
  df["timestamp"] = pd.to_datetime(
    df['timestamp'],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce" #coerce mtlb errors ko forcefully convert kr dega
  )

  #converting measurements to numeric
  numeric_columns = [
    "temperature",
    "humidity",
    "wind_speed",
    "wind_direction",
    "pressure"
  ]

  for column in numeric_columns:
    df[column] = pd.to_numeric(
      df[column],
      errors="coerce"
    )

  #sorting chronologically
  df = df.sort_values("timestamp")

  #reset index (have to do in pandas, not relevant to understand)
  df = df.reset_index(drop=True)

  #saving the file
  OUTPUT_FILE.parent.mkdir(parents = True, exist_ok=True)

  df.to_csv(OUTPUT_FILE, index = False)

  print("\nNormalization complete.")
  print(f"Rows: {len(df)}")
  print(f"Columns: {list(df.columns)}")
  print(f"Saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
  normalize_aws_data()
