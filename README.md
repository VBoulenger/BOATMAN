# PMI 

## Installation


This project uses [SNAP](https://step.esa.int/main/download/snap-download/), however its installation will be done automatically by conda. 
To access `SNAP` through python, we use `snapista`, a conda package. 
Unfortunately, very specific version of python packages are needed to install it. 

To ease the installation, we provide an `yml` file for conda to create a clean environment.

You can install it with:

```bash
conda env create -f environment.yml
```
The new environment will be called `snap`, documentation to change this can be found [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).

Don't forget to activate the environment with:
```bash
conda activate snap
```

## Authentication

This project uses data from the Copernicus Open Access Hub.
Like most Data Hubs, it requires authentication.
In order to be able to download data from the Copernicus Open Access Hub, you will need to enter your credentials in a file .netrc in your user home directory in the following form:

```
machine apihub.copernicus.eu
login <your_username>
password <your_password>
```

Getting a `401 Unauthorized` error means your credentials are wrong or not yet active.

## Git Hooks

This project uses a formater and a linter on the codebase.
Therefore, it is greatly recommended to use git hooks to enforce this behavior.

A basic `pre-commit` hook is available within the repo, you can use it with:

```bash
git config --local core.hooksPath .githooks/
```
