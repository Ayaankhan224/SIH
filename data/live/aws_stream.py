from pathlib import Path
import csv
import time
import os

import requests
from dotenv import load_dotenv

load_dotenv()

#loading api key from env key ko private rakhne ke liye and github pe na rahe
WEATHER_UNION_API_KEY = os.getenv(
    "WEATHER_UNION_API_KEY"
)

WEATHER_UNION_URL = (
    "https://www.weatherunion.com/"
    "gw/weather/external/v0/get_weather_data"
)

OUTPUT_FILE = Path(
  "data/live/aws_stream.csv"
)

STREAM_DELAY = 60 #har new observation bhejne se pehle 60 seconds wait karega

def get_observations(latitude, longitude):
  """Taking in real time data from weather union api key"""

  if not WEATHER_UNION_API_KEY:
    raise RuntimeError(
      "WEATHER_UNION_API_KEY is not set."
    )
  
  while True:
    try:

      #connecting to weather union 
      response = requests.get(
        WEATHER_UNION_URL,  #to this url
        headers={
          'X-Zomato-Api-Key':WEATHER_UNION_API_KEY  #using this key
        },
        params={    #with these parameters
          "latitude" : latitude,  
          "longitude" : longitude
        },
        timeout=10
      )

      response.raise_for_status()

      data = response.json() #storing the response from weather union inside data in json format

      print("\nRAW WEATHER UNION RESPONSE:")
      print(data)
      
      #checking api response
      if str(data.get("status")) != "200": #200 status code means OK, therfor if !200 then raise errror
        raise RuntimeError(
          data.get(
            "message",
            "Weather Union APi error"
          )
        )

      weather = data.get('locality_weather_data')

      if weather is None:
        raise RuntimeError(
          "Weather data unavailable."
        )

      #converting the data sent by weather union to the format our data pipeline uses
      yield {
        "timestamp": time.strftime(
          "%Y-%m-%d %H:%M:%S"
        ),

        "temperature": weather.get(
          "temperature"
        ),

        "humidity": weather.get(
          "humidity"
        ),

        "wind_speed": weather.get(
          "wind_speed"
        ),

        "wind_direction": weather.get(
          "wind_direction"
        ),

        "pressure": None
      }

    #raising errors
    except requests.RequestException as error:
      print(
        f"Weather Union request failed: "
        f"{error}"
      )

    except ValueError as error:
      print(
        f"Invalid API response: "
        f"{error}"
      )

    except RuntimeError as error:
      print(
        f"Weather Union error: "
        f"{error}"
      )

    #Wait before requesting again
    time.sleep(STREAM_DELAY)


def write_observation(row,writer,output_file):
  """Write ONE weather observation to the live CSV."""

  writer.writerow(row)

  # Make sure the row is immediately written to disk.
  output_file.flush()

  print(
    f"New observation: "
    f"{row['timestamp']} | "
    f"Temperature: {row['temperature']} | "
    f"Humidity: {row['humidity']} | "
    f"Wind: {row['wind_speed']}"
  )

#main stream
def main():
  print("Starting real-time weather stream...")
  print(
      f"Output: {OUTPUT_FILE}"
  )
  print(
      "Press Ctrl+C to stop.\n"
  )

  OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
  )

  # Start with a fresh file.
  if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

  #WEATHER UNION LOCATION (Salt Lake, Kolkata)
  latitude = 22.582808
  longitude = 88.416526

  #calling the observation fn
  observations = get_observations(
    latitude,
    longitude
  )

  try:
    first_row = next(observations)

    # Use the returned fields as CSV columns.
    fieldnames = list(
      first_row.keys()
    )

    with OUTPUT_FILE.open(
      "w",
      newline="",
      encoding="utf-8"
    ) as output_file:

      writer = csv.DictWriter(
        output_file,
        fieldnames=fieldnames
      )

      # write CSV header.
      writer.writeheader()

      # write first observation.
      write_observation(
        first_row,
        writer,
        output_file
      )
      # continue receiving observations.
      for row in observations:
        write_observation(
          row,
          writer,
          output_file
        )

  except KeyboardInterrupt:
    print(
      "\nWeather stream stopped."
    )

if __name__ == "__main__":
  main()
