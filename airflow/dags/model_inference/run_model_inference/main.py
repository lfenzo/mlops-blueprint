import argparse
import json
import requests

import numpy as np
import pandas as pd

from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split


INFERENCE_ENDPOINT = "http://mlflow-inference-server:8080/invocations"


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help="Name of the output file")
    return vars(parser.parse_args())


def load_data() -> np.array:
    db = load_diabetes()
    X_train, X_test, y_train, y_test = train_test_split(db.data, db.target)
    return X_test


def format_input_for_prediction(data: np.array) -> str:
    df = pd.DataFrame(data)
    return json.dumps({"inputs": df.values.tolist()}, indent=4)


if __name__ == "__main__":
    args = parse_cli_args()
    print(args)
    raw_data = load_data()
    json_string = format_input_for_prediction(data=raw_data)

    response = requests.post(
        url=INFERENCE_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json_string
    )

    if response.status_code != 200:
        raise Exception("Error:", response.status_code, response.text)

    with open(args["output"], "w") as file:
        file.writelines([str(pred) + "\n" for pred in response.json()["predictions"]])

    print(f"Predictions saved to {args['output']}")
