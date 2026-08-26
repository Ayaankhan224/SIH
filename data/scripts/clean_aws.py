from pathlib import Path
import csv

RAW_FILE = Path('data/raw/aws_2012.csv')
OUTPUT_FILE = Path('data/processed/aws_clean_2012.csv')

def clean_aws_data():
  """TO CLEAN THE RAW AWS FILE TO USABLE PROCESSED FORMS (CSV data humko chahie, HTML hatana hai)"""
  print(f'Reading: {RAW_FILE}')

  #opening the raw file as "file"
  with RAW_FILE.open("r", encoding="utf-8", errors="ignore") as file:

    lines = file.readlines() #storing all the lines inside lines (lines is an array)

  #finding the actual CSV header inside the HTML(RAW_FILE)
  header_index = None

  #iterating through every line
  for i, line in enumerate(lines): #enumerate gives both index (stored in i) and value (stored in line)
    if '"obstime","tempr","rh","ws","wd","ap"' in line: #selecting only the required texts
      header_index = i
      break

  if header_index is None:
    raise ValueError("Could not find AWS Header") #shows a custom message rather than showing error

  print(f"CSV Header found at line {header_index+1}")

  """now we have our header i.e. wo line jaha se required text start krta"""

  data_lines = lines[header_index+1:] #stores everything after the header

  cleaned_rows = []

  for line in data_lines:
    line = line.strip() #strips the data from lines

    #ignores the html after the csv
    if not line or line.startswith('<'):
      continue

    values = [value.strip() for value in line.split(",")]

    #we expect exactly 6 columns "obstime", "tempr", "rh", "ws", "wd", "ap"
    if len(values) != 6:
      continue

    cleaned_rows.append(values)

    """now we have our data, isko ab write krna hai ek file me"""

  OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

  with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    #creating headings
    writer.writerow([
      "obstime",
      "tempr",
      "rh",
      "ws",
      "wd",
      "ap"
    ])

    writer.writerows(cleaned_rows)

  print(f"Cleaned Rows: {len(cleaned_rows)}")
  print(f"Saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
  clean_aws_data()
