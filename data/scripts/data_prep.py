from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/processed/aws_normalized_2012.csv")
OUTPUT_FILE = Path("data/processed/aws_features_2012.csv")

"""preparing data for further use by the ML part (ML ko sirf raw weather values nahi, patterns bhi chahiye)"""
def data_prepare():

  #everytime we do "df[] = ..." we are storing those values in data frame (data frame is basically like an excel sheet but fancier)
  df = pd.read_csv(INPUT_FILE)

  #timestamp currently text hai, isko datetime bana rhe hain taaki hour/day/month nikal saken
  df["timestamp"] = pd.to_datetime(
      df["timestamp"],
      format="%Y-%m-%d %H:%M:%S"
  )

  #storing time features (ML ko time of day aur season ka pattern samajhne me help karega)
  df["hour"] = df["timestamp"].dt.hour
  df["day"] = df["timestamp"].dt.day
  df["month"] = df["timestamp"].dt.month

  #change from previous observation (diff current value - previous row ki value deta hai)
  df["temperature_change"] = (
      df["temperature"].diff()
  )

  df["humidity_change"] = (
      df["humidity"].diff()
  )

  df["pressure_change"] = (
      df["pressure"].diff()
  )

  df["wind_speed_change"] = (
      df["wind_speed"].diff()
  )

  #rolling statistics (last 6 hours ka average nikal rhe hain, har row ke liye)

  window = 6 #window size 6 means previous 6 observations/hours ko consider karega

  #temperature ka recent average aur spread (std) nikal rhe hain
  df["temperature_rolling_mean"] = (
      df["temperature"]
      .rolling(window)
      .mean()
  )

  df["temperature_rolling_std"] = (
      df["temperature"]
      .rolling(window)
      .std()
  )

  df["humidity_rolling_mean"] = (
      df["humidity"]
      .rolling(window)
      .mean()
  )

  df["pressure_rolling_mean"] = (
      df["pressure"]
      .rolling(window)
      .mean()
  )

  #distance from recent average (current weather apne recent normal se kitna different hai)
  df["temperature_deviation"] = (
      df["temperature"]
      - df["temperature_rolling_mean"]
  )

  df["humidity_deviation"] = (
      df["humidity"]
      - df["humidity_rolling_mean"]
  )

  df["pressure_deviation"] = (
      df["pressure"]
      - df["pressure_rolling_mean"]
  )

  #shortening the long float numbers
  numeric_columns = df.select_dtypes(
      include="number"
  ).columns

  df[numeric_columns] = df[numeric_columns].round(4)

  OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
  )

  df.to_csv(
    OUTPUT_FILE,
    index=False
  )

  print("Feature engineering complete.")
  print(f"Rows: {len(df)}")
  print(f"Features: {len(df.columns)}")
  print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
  data_prepare()
