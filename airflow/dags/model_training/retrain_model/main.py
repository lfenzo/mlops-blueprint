import mlflow
import argparse
from mlflow.models import infer_signature

import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Model name in MLflow registry")
    return vars(parser.parse_args())


def load_data():
    X, y = datasets.load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)


if __name__ == "__main__":
    args = parse_cli_args()
    X_train, X_test, y_train, y_test = load_data()

    params = {
        "solver": "lbfgs",
        "max_iter": 1000,
        "multi_class": "auto",
        "random_state": 8888,
    }

    lr = LogisticRegression(**params)
    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.set_experiment("Autologging test")

    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.set_tag("Training Info", "Basic LR model for iris data")

        signature = infer_signature(X_train, lr.predict(X_train))
        model_info = mlflow.sklearn.log_model(
            sk_model=lr,
            artifact_path="iris_model",
            signature=signature,
            input_example=X_train,
            registered_model_name=args["name"],
        )
