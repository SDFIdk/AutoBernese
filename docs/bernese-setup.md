We are currently preparing the installation of Bernese GNSS Software version 5.4
[BSW].

This page will eventuelly explain to the users how we have set up the server
that runs the software.

For now, here are the settings that we have set during installation.

!!! warning "These settings are apt to change"

    The settings are apt to change until we have established a good working solution
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
