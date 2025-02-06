import argparse
import mlflow


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Get the model uri from the model tagged as 'champion' in the Mlflow registry"
    )
    parser.add_argument("-t", "--tag", help="Model tag to be used (default = 'champion')")
    parser.add_argument("-o", "--output", help="Output file where the model uri will be written")
    parser.add_argument("--tracking-uri", help="Uri for the MLflow Tracking Server")
    return vars(parser.parse_args())


def get_models_by_tag(client: mlflow.MlflowClient, tag: str) -> list:
    return [
        model
        for model in client.search_registered_models()
        if tag in list(model.tags.keys())
    ]


def get_latest_model_version(client: mlflow.MlflowClient, model_name: str) -> str:
    latest_versions = client.get_latest_versions(model_name)
    return max(latest_versions, key=lambda v: int(v.version))


def get_champion_model_uri(client: mlflow.MlflowClient, tag: str, assert_unique: bool = True) -> str:
    client = mlflow.MlflowClient()
    selected_models = get_models_by_tag(client=client, tag=tag)

    if assert_unique and len(selected_models) != 1:
        raise Exception(f"Detected {len(selected_models)} models with the tag {tag}.")

    model_name = selected_models[0].name
    latest_version = get_latest_model_version(client=client, model_name=model_name)
    model_uri = f"models:/{model_name}/{latest_version.version}"
    print(model_uri)

    return model_uri


if __name__ == "__main__":
    args = parse_cli_args()

    champion_model_uri = get_champion_model_uri(
        client=mlflow.MlflowClient(tracking_uri=args["tracking_uri"]),
        tag=args["tag"],
    )

    with open(file=args["output"], mode="w") as file:
        file.write(champion_model_uri)
