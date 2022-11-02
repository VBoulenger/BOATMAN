# PMI 

## Installation


This project uses `SNAP`, you can download it [here](https://step.esa.int/main/download/snap-download/).

---
Unfortunately, the interface between `SNAP` and python requires specifics version to work.
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
---

For the final step, you need to configure `snappy` and install it in your python environment.

Read the complete [documentation](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface) for more information, but basically you need to execute:
```bash
cd <snap-install-dir>/bin
./snappy-conf <conda-install-dir>/envs/snap/bin/python3
```
Now that snappy is configured, you can import it manually everytime or install it with:
```bash
cd <snappy-dir>/bin
python3 setup.py install
```

Defaults locations are:

| Location           | Default path              |
|--------------------|---------------------------|
| snap-install-dir   | ~ (home directory)        |
| conda-install-dir  | ~/{Ana,mini}conda3/       |
| snappy-dir         | .snap/snap-python/snappy/ |


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
