import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
from typing import Literal
import requests  # type: ignore

env_to_docker_image = {
    "dev": "885886606610.dkr.ecr.us-east-2.amazonaws.com/environments",
    "staging": "905418339935.dkr.ecr.us-east-2.amazonaws.com/environments",
    "prod": "211125665565.dkr.ecr.us-east-2.amazonaws.com/environments",
}


def post_environment(
    base_url: str,
    *,
    folder_path: str,
    headers: dict | None = None,
    environment: Literal["dev", "staging", "prod"] = "dev",
):
    """
    Send an experiment.zip file to the server via POST request.

    Args:
        base_url (str): The base URL of the API
        folder_path (str): Path to the folder the contains the experiment
        headers (dict, optional): Additional headers to include in the request

    Returns:
        requests.Response: The response from the server
    """
    env_name = Path(folder_path).name

    # Search the `metadata.json` file in the folder
    metadata_path = Path(folder_path) / "metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.json not found in {folder_path}")

    metadata = {}

    with open(metadata_path, "r") as f:
        try:
            metadata = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing metadata.json: {e}")

    version = metadata.get("version")
    instance = metadata.get("instance")
    python_version = metadata.get("python_version")
    cuda_version = metadata.get("cuda_version")

    if not version:
        raise ValueError("version is required in metadata.json")

    if not instance:
        raise ValueError("instance is required in metadata.json")

    if not python_version:
        raise ValueError("python_version is required in metadata.json")

    if instance == "gpu" and not cuda_version:
        raise ValueError("cuda_version is required in metadata.json if instance is gpu")

    print("Checking if environment already exists")
    response = requests.get(
        f"{base_url}/environments/{env_name}",
        headers=headers,
        params={"identifier": "name"},
    )
    if response.status_code == 200:
        print(f"Environment {env_name} already exists")

        # Check the version of the environment
        existing_env = response.json()

        if (metadata := existing_env.get("metadata")) and (
            metadata.get("version") == version
        ):
            print(f"Environment {env_name} already exists with version {version}")
            sys.exit(0)

        print(f"Continuing creation of new environment with version {version}")

    print(f"Building docker environment for {env_name} in {environment} environment")

    result = subprocess.run(
        ["bash", "./scripts/build-docker-env.sh", env_name, version, environment]
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to build docker environment: {result.stderr.decode()}"
        )

    print(f"Docker environment built successfully: {result.stdout.decode()}")

    tag = f"{env_name}-{version}"

    instance = metadata.get("instance")
    python_version = metadata.get("python_version")
    cuda_version = metadata.get("cuda_version")

    if not instance and instance not in ["gpu", "cpu"]:
        raise ValueError("instance is required in metadata.json as gpu or cpu")

    if not python_version:
        raise ValueError("python_version is required in metadata.json")

    if not cuda_version and instance == "gpu":
        raise ValueError("cuda_version is required in metadata.json if instance is gpu")

    # Construct the full URL
    url = base_url + "/environments"

    print("..:: Request to create environment ..:: ", base_url)

    # Create JSON payload with all fields including base64-encoded file

    description = f"Python {python_version}. "

    if instance == "gpu":
        description += f"GPU with CUDA {cuda_version}"
    else:
        description += "CPU"

    payload = {
        "name": env_name,
        "description": description,
        "configuration": {
            "tag": tag,
            "version": "0.0.1",  # This is the version of the configuration
            "provider": "modal",
            "docker_image": env_to_docker_image[environment],
        },
        "metadata": {
            "instance": instance,
            "python_version": python_version,
            "cuda_version": cuda_version,
            "version": version,
        },
    }

    print("..:: Payload ..:: ", payload)

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("..:: Response ..:: ", response)
        print(response.json())
        response.raise_for_status()
    except Exception:
        headers = headers or {}
        headers.update(
            {
                "Authorization": f"x-api-key {os.getenv('X_API_KEY')}",
                "Content-Type": "application/json",
            }
        )

        print("..:: Headers ..:: ", headers)

        # Make the POST request with JSON payload
        try:
            response = requests.post(url, json=payload, headers=headers)
            print("..:: Response ..:: ", response)
            print(response.json())
            response.raise_for_status()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Check if the request was successful
    response.raise_for_status()

    return response


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy docker image and create environment"
    )
    parser.add_argument(
        "--base-url", help="Base URL of the API", default="http://localhost:8001/api/v1"
    )

    parser.add_argument(
        "--folder-path",
        help="Path to folder environment (Should contain the Dockerfile)",
        required=True,
    )

    parser.add_argument("--environment", help="Environment to deploy to", default="dev")

    args = parser.parse_args()

    # Set up headers if token is provided
    headers = None
    token = os.getenv("X_API_KEY")
    if token:
        headers = {"Authorization": f"x-api-key {token}"}

    try:
        response = post_environment(
            args.base_url,
            folder_path=args.folder_path,
            headers=headers,
            environment=args.environment,
        )
        print(f"Success! Status code: {response.status_code}")
        print("Response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        stacktrace = traceback.format_exc()
        print(stacktrace)
        sys.exit(1)
