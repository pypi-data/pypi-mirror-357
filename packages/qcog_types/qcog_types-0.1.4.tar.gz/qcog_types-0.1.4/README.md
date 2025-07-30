## Deploy new Environment

### Steps

1. Create a new folder in the `docker-environments` directory
2. Create a new Dockerfile in the new folder. (The name of the folder will be used as a tag for the environment)
3. Add the a pyproject.toml file to the new folder with the dependencies.
4. Add a metadata.json file to the new folder. It must specify:
    - instance: "cpu" or "gpu"
    - python_version: "3.12"
    - cuda_version: "12.8" (only if instance is "gpu")
    - version: "0.0.1" (The version of the environment)
5. Add all the files that are needed for the new environment

**Gemfury Access**

If the docker build requires access to private repositories, you will need to
provide the credentials to the build script.

We assume that the credentials are used through the `uv` tool.

You can declare a new index for a private package by adding the following to the `pyproject.toml` file:

```toml
[tool.uv.sources]
<my_private_package> = { index = "gemfury" }

[[tool.uv.index]]
name = "gemfury"
url = "https://pypi.fury.io/qognitive"
authenticate = "always"
explicit=true
```

Credentials are passed as environment variables to the build script.

```bash
export UV_INDEX_GEMFURY_USERNAME=<your-username>
export UV_INDEX_GEMFURY_PASSWORD=<your-password>
```

**API Key access**

In order to perform the deployment, you need an API Key with Admin priviledges.

You can export the key in the following way:
```bash
export X_API_KEY=<your-api-key>
```

## Deploying a new environment

The following command will build the docker image and push it to the ECR repository.
`--environment` can be `dev`, `staging` or `prod`.

If you are using the `env` command, it will require a server running locally on `localhost:8001`.
See [QcogAPI](https://github.com/qognitive/qcog-api-2) for more details.

```bash
python scripts/publish_environment.py --folder-path docker-environments/py3.12-cuda --environment dev
```

You should see and output like the following:
```bash
Success! Status code: 200
Response:
{
    'id': '31dee69d-8076-4164-85de-87df825ed6c6',
    'name': 'py3.12-cuda',
    'description': 'Python 3.12. GPU with CUDA 12.8',
    'created_by': 'e8cc8e7e-3fa7-465c-89b6-556f6823a96d',
    'created_ts': '2025-06-19T09:05:10.017320Z',
    'updated_ts': '2025-06-19T09:05:10.017320Z',
    'metadata': {'version': '0.0.1', 'instance': 'gpu', 'cuda_version': '12.8', 'python_version': '3.12'}
}
```

You can reference the environment by its `name`

> NOTE: the procedure is automatized for `staging` and `prod` environments in the CI/CD pipeline. The previous worklflow is useful for local development.



