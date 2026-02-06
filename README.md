# PiSense_Backend

Backend for PiSense written using python and FastApi



### UV

#### Install UV

https://docs.astral.sh/uv/getting-started/installation/

For Linux - curl -LsSf https://astral.sh/uv/install.sh | sh


#### Add new dependency to project

`uv add requests`

This will resolve the new dependency and add it to our list of dependencies in `pyproject.toml`. You will need to run `uv lock` afterwards to update the lock file. ( We will later setup a pipeline to yell at you when you forget )

#### Developing

git clone the repo and install uv

navigate to the project folder and run `uv sync`. This will create a python virtual environment and install all of the packages from the lock file.

In linux ( wsl ) `source .venv/bin/activate` to enter the local environment. ( If you setup a vscode workspace this can be done automatically ) This will give you access to all of the libraries that `PiSense_Backend` uses ( mostly for autocomplete context )

#### Pushing new code and updating project

Update version number in `pyproject.toml` ( Do we want to enforce versioning semantics )

`uv lock` to update lock file ( This will be eventually required by the pipeline )


