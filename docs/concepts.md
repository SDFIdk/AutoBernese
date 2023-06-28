
## Bernese environment

In AutoBernese terms, the Bernese environment is the directory one level above
the Bernese installation directory `BERN54`.

If we install Bernese GNSS Software in a directory for production use:

```
/path/to/prod/BERN54
```

, the Bernese environment refers to this part of the path:

```
/path/to/prod
```

!!! note "Assumption"

AutoBernese uses the environment variable `${C}` set in `LOADGPS.setvar` to find
out where the current activated Bernese environment is.


## AutoBernese runtime directory

AutoBernese will, automatically, create its *runtime directory* at the same
level as the BERN54 directory of the *Bernese environment*.

For the activated *Bernese environment*, say `test` located here:

```
/path/to/test
```

, AutoBernese will create a directory `autobernese` there, i.e. the full path to
the runtime directory will be:

```
/path/to/test/autobernese
```


## AutoBernese configuration file or common configuration



## campaign-specific configuration

## campaign-specific configuration template

## campaign type


### Campaign templates

Differentiation between the different configuration files:

*   The general configuration file has configuration about campaign creation and
    management.

*   The module here creates a campaign-specific configuration file that is also
    a campaign configuration, but campaign-specific (an instance)

*   The package also has internal package data thate are ued to create the
    campaign-specific configuration file, and whose name says that it is a
    campaign-template.

*   However, the campaign template internal to the package, is an example of a
    campaign-specific configuration template (to be prepended with a meta-data
    section) that is copied over to the campaign-template directory that is the
    source where users put their templates and manage them.

*   Finally, the list of existing campaigns known to Bernese is put in the
    installation directory under SUPGUI and is called MENU_CMP.INP. This file is
    used by BSW to know where the campaign is located. It has to be read and
    updated, when a user creates a campaign with this program.
