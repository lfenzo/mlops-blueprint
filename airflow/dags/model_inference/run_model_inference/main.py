import json
import requests
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split

db = load_diabetes()
X_train, X_test, y_train, y_test = train_test_split(db.data, db.target)

df = pd.DataFrame(X_test)
json_object = {"inputs": df.values.tolist()}
json_string = json.dumps(json_object, indent=4)

url = "http://mlflow-inference-server:8080/invocations"

response = requests.post(url, headers={"Content-Type": "application/json"}, data=json_string)

if response.status_code == 200:
    print("Predictions:", response.json())
else:
    print("Error:", response.status_code, response.text)
