!!! note "Work in progress"

    We are currently preparing the installation of Bernese GNSS Software version 5.4
    [BSW].

    This page will eventuelly explain to the users how we have set up the server
    that runs the software.

    For now, here are the settings that we have set during installation.

    The settings below are apt to change until we have established a good working solution
    for BSW and the automation program.


## Production | PROD

| What                       | Value                       |
| -------------------------- | --------------------------- |
| Installation directory     | `/home/bin/BERN54`          |
| DATAPOOL                   | `/home/data/bsw/DATAPOOL`   |
| CAMPAIGN                   | `/home/data/bsw/CAMPAIGN54` |
| SAVEDISK                   | `/home/data/bsw/SAVEDISK`   |
| User environment           | `$HOME/bsw/user`            |
| Temporary user environment | `$HOME/bsw/temp`            |


## Test | TEST

| What                       | Value                            |
| -------------------------- | -------------------------------- |
| Installation directory     | `/home/bin/bsw54/test`           |
| DATAPOOL                   | `/home/data/bsw/test/DATAPOOL`   |
| CAMPAIGN                   | `/home/data/bsw/test/CAMPAIGN54` |
| SAVEDISK                   | `/home/data/bsw/test/SAVEDISK`   |
| User environment           | `$HOME/bsw/test/user`            |
| Temporary user environment | `$HOME/bsw/test/temp`            |

## Setup user environment

!!! note "Deviations from the default installation"

    Between versions 5.2 and 5.4, the default names for the user environment
    directories have changed. However, we chose a different naming convention than
    the default one:

    | Directory      | 5.2         | 5.4       | 5.4 (our names) |
    | -------------- | ----------- | --------- | --------------- |
    | `basename($U)` | `GPSUSER52` | `GPSUSER` | `user`          |
    | `basename($T)` | `GPSTEMP`   | `GPSWORK` | `temp`          |


On the server

*   Set environment variables for the current shell session

    ```sh
    source /home/bin/BERN54/LOADGPS.setvar
    ```

*   Run the BSW configuration tool.

    ```
    $EXE/configure.pm
    ```

    ``` title="Output" hl_lines="6"
    ==========================================
    CONFIGURATION OF THE BERNESE GNSS SOFTWARE
    ==========================================
    1 ... Update LOADGPS.setvar
    2 ... Install online updates
    3 ... Add a new user environment
    4 ... Compile the menu
    5 ... Compile the programs
    6 ... Install the example campaign
    7 ... Update / install Bernese license file
    8 ...   ---

    x ... Exit

    Enter option:
    ```

*   Choose option 3

    ``` title="Output" hl_lines="3"
    Enter option: 3

    Create user environment /home/<user>/bsw/user (y/n):
    ```

* Say yes `y`

    ``` title="Output" hl_lines="8"
    Create user environment /home/<user>/bsw/user (y/n): y

    Copying menu and program input files...
    Copying BPE user scripts...
    Copying examples for process control files...
    Copying BPE options for processing examples...
    Copying ICONS ...
    ### Archive of ICONS not found!

    **********************************************************************
    * User area /home/<user>/bsw/user
    * has been added/updated.
    **********************************************************************
    ```

Despite the warning above, the environment is now created by creating the above
directory as well as a temporary directory.
