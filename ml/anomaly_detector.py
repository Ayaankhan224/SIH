from pathlib import Path
import pandas as pd
from sklearn.ensemble import IsolationForest

INPUT_FILE = Path("data/processed/aws_features_2012.csv")
OUTPUT_FILE = Path("data/processed/aws_anomalies_2012.csv")

def train_anomaly_detector():
  print("LOADING PREPARED AWS DATA")

  df = pd.read_csv(INPUT_FILE)

  #features used by the model
  features = [
    "temperature",
    "humidity",
    "wind_speed",
    "wind_direction",
    "pressure",
    "temperature_change",
    "humidity_change",
    "pressure_change",
    "wind_speed_change",
    "temperature_rolling_mean",
    "temperature_rolling_std",
    "humidity_rolling_mean",
    "pressure_rolling_mean",
    "temperature_deviation",
    "humidity_deviation",
    "pressure_deviation",
  ]

  model_data = df.dropna(
    subset=features
  ).copy()

  X = model_data[features]

  print(f"Training observations: {len(X)}")
  print(f"Model features: {len(features)}")

  #ISOLATION FOREST
  model = IsolationForest(
    n_estimators=200,
    contamination=0.2,
    random_state=42
  )

  model.fit(X)

  #prediction
  #1 : normal
  #-1 : anomaly

  model_data["prediction"] = model.predict(X)

  #ISOLATION FOREST DECISION SCORE
  model_data['anomaly_score'] = model.decision_function(X)

  #CONVERT PREDICTION INTO READABLE LABEL
  model_data["status"] = model_data[
    "prediction"
  ].map({
    1: "normal",
    -1: "anomaly"
  })

  #SAVE RESULTS
  OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

  model_data.to_csv(OUTPUT_FILE, index=False)

  print("\nMODEL TRAINING COMPLETE!")

  print(f"Normal Observation: ")
  print(f"{(model_data['prediction']==1).sum()}")

  print(f"Anomalies Detected: ")
  print(f"{(model_data['prediction']==-1).sum()}")

  print(f"Saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
  train_anomaly_detector()