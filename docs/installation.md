
## Prerequisites

*   Bernese GNSS Software version 5.4 installed and ready to use.
*   Git for downloading the source of AutoBernese.
*   The MambaForge Python distribution.

## Install AutoBernese

*   Using git on your system, get the code by cloning the repository to your machine.
*   In the directory of the Git archive use `environment.yml` to install the package dependencies:

    ```sh
    mamba env create -f environment.yml
    ```

*   Activate the environment:

    ```sh
    mamba activate ab
    ```

*   Using the `ab` environment's Python interpreter, install AutoBernese with PIP:

    ```sh
    python -m pip install .
    ```

From now on, you will have the AutoBernese command-line tool `ab` available,
when the `ab` mamba environment is activated.
