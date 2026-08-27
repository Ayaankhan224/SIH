import pandas as pd
import joblib
import time
from pathlib import Path


# FILE LOCATIONS
INPUT_FILE = Path("data/live/aws_stream.csv")
MODEL_FILE = Path("ml/models/live_model.pkl")


# FEATURES THE MODEL EXPECTS
FEATURES = [
  "temperature",
  "humidity",
  "wind_speed",
  "wind_direction",
  "temperature_change",
  "humidity_change",
  "wind_speed_change",
  "temperature_rolling_mean",
  "temperature_rolling_std",
  "humidity_rolling_mean",
  "temperature_deviation",
  "humidity_deviation",
]


def prepare_live_data(df):

  # Convert timestamp from text to datetime
  df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="%Y-%m-%d %H:%M:%S"
  )

  # Calculate changes from previous observation
  df["temperature_change"] = (
    df["temperature"].diff()
  )

  df["humidity_change"] = (
    df["humidity"].diff()
  )

  df["wind_speed_change"] = (
    df["wind_speed"].diff()
  )

  window = 6

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

  df["temperature_deviation"] = (
    df["temperature"]
    - df["temperature_rolling_mean"]
  )

  df["humidity_deviation"] = (
    df["humidity"]
    - df["humidity_rolling_mean"]
  )

  return df


def predict_latest():

  # Read live data
  df = pd.read_csv(INPUT_FILE)

  # Need at least 6 observations
  if len(df) < 6:
    print(
      f"Waiting for more observations..."
      f" ({len(df)}/6)"
    )
    return None

  # Create the same features used during training
  df = prepare_live_data(df)

  # Remove rows where features cannot be calculated
  model_data = df.dropna(
    subset=FEATURES
  ).copy()

  if model_data.empty:
    print("Waiting for enough usable data...")
    return None

  latest = model_data.iloc[-1]

  X = latest[FEATURES].to_frame().T

  model = joblib.load(MODEL_FILE)

  prediction = model.predict(X)[0]

  score = model.decision_function(X)[0]

  if prediction == 1:
    status = "NORMAL"
  else:
    status = "ANOMALY"

  print("\n--------------------------------")
  print("LIVE WEATHER ANALYSIS")
  print("--------------------------------")
  print(f"Time:        {latest['timestamp']}")
  print(f"Temperature: {latest['temperature']}")
  print(f"Humidity:    {latest['humidity']}")
  print(f"Wind Speed:  {latest['wind_speed']}")
  print(f"Wind Dir:    {latest['wind_direction']}")
  print(f"Status:      {status}")
  print(f"Score:       {score:.4f}")
  print("--------------------------------")

  return prediction


def main():

  print("Starting live anomaly detection...")
  print(f"Reading: {INPUT_FILE}")
  print("Press Ctrl+C to stop.")

  last_timestamp = None

  try:
    while True:
      df = pd.read_csv(INPUT_FILE)

      if not df.empty:
        current_timestamp = df.iloc[-1]["timestamp"]
        if current_timestamp != last_timestamp:
          predict_latest()
          last_timestamp = current_timestamp

        time.sleep(5)

  except KeyboardInterrupt:
    print("\nLive anomaly detection stopped.")


if __name__ == "__main__":
  main()