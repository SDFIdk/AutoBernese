
## Prerequisites

Before installing AutoBernese, you must have the following software installed:

*   [Bernese GNSS Software version 5.4][BSW]
*   [Git] for downloading [the AutoBernese source code][GH-AB]
*   [The MambaForge Python distribution](../prerequisites.md)

[BSW]: http://www.bernese.unibe.ch/
[Git]: https://git-scm.com/download/linux
[GH-AB]: https://github.com/SDFIdk/AutoBernese


## Install AutoBernese

*   Using git on your system, get the code by cloning the repository to your
    machine.

    ```sh
    (base) $ git clone https://github.com/SDFIdk/AutoBernese.git
    ```

*   In the directory of the Git archive use `environment.yml` to install the
    package dependencies:

    ```sh
    (base) $ mamba env create -f environment.yml
    ```

*   Activate the environment:

    ```sh
    (base) $ mamba activate ab
    (ab) $
    ```

*   Using the `ab` environment's Python interpreter, install AutoBernese with
    `pip`:

    ```sh
    (ab) $ python -m pip install .
    ```

From now on, you will have the AutoBernese command-line tool `ab` available,
when the `ab` mamba environment is activated.

!!! tip "Set up login script to activate AutoBernese mamba environment automatically"

    To automatically activat the AutoBernese mamba environment, whenever you open a
    terminal, add the activation command to your login script [`~/.bashrc` or
    similar for your shell]:

    ```bash
    # .bashrc
    # ...
    mamba activate ab
    ```

## Update AutoBernese

The package is so far only distributed on GitHub. Updating to a newer version of
AutoBernese means downloading the latest revision from the main branch and 1)
update the environment dependencies in `environment.yml` and 2) re-install
AutoBernese from the Git archive directory:

*   Go to the repository to your machine.

    ```sh
    (base) $ cd /path/to/AutoBernese
    ```

*   Pull the latest revisions from GitHub:

    ```sh
    (base) $ git pull
    ```

*   Update the package dependencies:

    ```sh
    (base) $ mamba env update -n ab -f environment.yml
    ```

*   Activate the environment:

    ```sh
    (base) $ mamba activate ab
    (ab) $
    ```

*   Using the `ab` environment's Python interpreter, update AutoBernese with
    `pip`:

    ```sh
    (ab) $ python -m pip install -U .
    ```
