import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest

INPUT_FILE = Path("data/live/aws_stream.csv")
MODEL_FILE = Path("ml/models/live_model.pkl")

# features used by the live model
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

  # Convert timestamp into datetime
  df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="%Y-%m-%d %H:%M:%S"
  )

  # Change from previous observation
  df["temperature_change"] = (
    df["temperature"].diff()
  )

  df["humidity_change"] = (
    df["humidity"].diff()
  )

  df["wind_speed_change"] = (
    df["wind_speed"].diff()
  )

  # Rolling statistics
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

  # Deviation from recent average
  df["temperature_deviation"] = (
    df["temperature"]
    - df["temperature_rolling_mean"]
  )

  df["humidity_deviation"] = (
    df["humidity"]
    - df["humidity_rolling_mean"]
  )

  return df


def train_live_model():

  print("LOADING LIVE WEATHER DATA")

  df = pd.read_csv(INPUT_FILE)

  print(f"Live observations: {len(df)}")

  # Create features
  df = prepare_live_data(df)

  # Remove rows where features cannot be calculated
  model_data = df.dropna(
    subset=FEATURES
  ).copy()

  X = model_data[FEATURES]

  print(f"Training observations: {len(X)}")
  print(f"Model features: {len(FEATURES)}")

  # Create Isolation Forest
  model = IsolationForest(
    n_estimators=100,
    contamination="auto",
    random_state=42
  )

  # Train model
  model.fit(X)

  # Save model
  MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
  )

  joblib.dump(
    model,
    MODEL_FILE
  )

  print("\nLIVE MODEL TRAINING COMPLETE!")
  print(f"Model saved to: {MODEL_FILE}")


if __name__ == "__main__":
  train_live_model()