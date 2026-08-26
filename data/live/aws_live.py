from pathlib import Path
import csv
import time


#CONFIGURATION (input historical data hai aur output live stream wali csv hogi)

INPUT_FILE = Path(
  "data/processed/aws_normalized_2012.csv"
)

OUTPUT_FILE = Path(
  "data/live/aws_stream.csv"
)

STREAM_DELAY = 3 #har new observation bhejne se pehle 3 seconds wait karega

def get_observations():
  """current data source se weather observations nikalta hai (abhi historical CSV, future me Weather Union API)"""

  #csv ko DictReader se read kr rhe hain taaki har row column name ke saath dictionary ban jaye
  with INPUT_FILE.open("r",encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
      yield row #yield ek ek row return krta hai, saari rows ek saath memory me store nahi hoti


#STREAM OUTPUT (ek observation ko live stream csv me write karega)
def write_observation(row,writer,output_file):

  writer.writerow(row) #current weather row ko output csv me add kr do

  #flush se new observation immediately file me save hoti hai, taaki dusre parts/applications use read kar saken
  output_file.flush()

  #terminal me current streamed observation dikhane ke liye
  print(
      f"New observation: "
      f"{row['timestamp']} | "
      f"Temperature: {row['temperature']} | "
      f"Humidity: {row['humidity']} | "
      f"Wind: {row['wind_speed']}"
  )


#MAIN STREAM (stream ko start aur control karega)

def main():

  print("Starting weather data stream...")
  print(f"Source: {INPUT_FILE}")
  print(f"Output: {OUTPUT_FILE}")
  print("Press Ctrl+C to stop.\n")

  #output folder exist nahi karta toh create kr do
  OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
  )

  #har run me fresh stream start hoga, purani stream file delete kr do
  if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

  observations = get_observations() #generator bana diya, rows ab ek ek karke milengi

  try:
    #first row se column names nikal rhe hain, output csv ki heading ke liye
    first_row = next(observations)
    fieldnames = first_row.keys()

    with OUTPUT_FILE.open(
      "w",
      newline="",
      encoding="utf-8"
    ) as output_file:
      writer = csv.DictWriter(
        output_file,
        fieldnames=fieldnames
      )

      writer.writeheader() 

      #first observation immediately bhej do, delay sirf next rows ke beech me chahiye
      write_observation(
        first_row,
        writer,
        output_file
      )

      #remaining observations would be streamed one by one
      for row in observations:

        time.sleep(STREAM_DELAY) #real-time jaisa effect dene ke liye delay

        write_observation(
          row,
          writer,
          output_file
        )
  except StopIteration:
    #input file empty hogi toh first row nahi milegi
    print("No observations available.")

  except KeyboardInterrupt:
    #Ctrl+C dabane par error nahi, stream safely stop ho jayegi
    print("\nStream stopped by user.")


if __name__ == "__main__":
  main()
