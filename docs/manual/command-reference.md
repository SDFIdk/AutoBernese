
## Running AutoBernese

With AutoBernese installed, you have a new command `ab` available, which lets
you explore the rest of the available functionality based on the help system. By
itself it also does a few house-hold things.

### `ab`

#### Output

Help text printed to the terminal, describing the core themes of the application
and showing the available sub commands.

#### Process and Side Effects

The command itself is a script that imports the AutoBernese Python package `ab`
and runs the corresponding command-line interface API.

Whenever the AutoBernese package is imported, the following happens:

*   The built-in package-configuration file is read.

    -   If a user-configuration file is available, it, too, is loaded and
        allowed sections override the same sections in the built-in
        configuration.

*   From the loaded configuration, the directory of the Bernese installation is
    known. (This directory will be referred to as the environment directory.) If
    not already present, a directory `autobernese` is created in the environment
    directory.

*   Finally, the AutoBernese log file `autobernese.log` is created if not
    already created.


### `ab --version`

=== "Output"

    The current software version of AutoBernese is printed.


## Show rendered configuration during runtime

AutoBernese uses a built-in configuration file to integrate seamlessly into the
given activated Bernese environment. Most of the functionality of AutoBernese
relies on some configuration setting.

The configuration format is a YAML whose syntax features make it highly useful.
These features include re-using content in one place of the YAML document in
some other part of the same document.

<!-- Sort of like using variables in a computer
program. -->

<!-- This means that repeating some value can be done by referring to the value in
another place. -->

The static document, while being easy to create this way, does
make it harder to read and find potential errors in, when the data structure in
the document becomes larger or more complex in what is re-used, and how.

For this reason, it is often very helpful to look at what the documents looks
like, when everything written in it is resolved by the YAML loader.

### `ab config`

=== "Configuration file"

    ```yaml  linenums="1"
    --8<-- "src/ab/configuration/env.yaml::31"
    # (...)
    ```

=== "Rendered configuration"

    ```python
    {
        'bsw_env': {
            'C': '/home/bsw/prod/BERN54',
            'PAN': '/home/bsw/prod/BERN54/SUPGUI/PAN',
            'MODEL': '/home/bsw/prod/BERN54/GLOBAL/MODEL',
            'CONFIG': '/home/bsw/prod/BERN54/GLOBAL/CONFIG',
            'D': '/home/bsw/prod/data/DATAPOOL',
            'P': '/home/bsw/prod/data/CAMPAIGN54',
            'S': '/home/bsw/prod/data/SAVEDISK',
            'U': '/home/USERNAME/bsw/prod/user',
            'T': '/home/USERNAME/bsw/prod/temp'
        },
        # (...)
    }
    ```

### `ab config <section>`

Adding the name of one of the outer-most keys in the YAML configuration, only
this *section* will be shown:

**Example**

Let us look at the resolved Bernese-installation environment that
AutoBernese has access to. The following command prints the content of the
section [`bsw_env`] of the AutoBernese-configuration file containing the
environment variables that the software uses:

Here, you see that not all the variables set in BSW's `LOADGPS.setvar` script
are included, but this is all that AutoBernese is using for now.

=== "Configuration file"

    ```yaml  linenums="1"
    --8<-- "src/ab/configuration/env.yaml:44:69"
    ```

=== "Rendered configuration"

    ```python
    {
        'ab': PosixPath('/home/bsw/prod/autobernese'),
        'logging': {
            'filename': PosixPath('/home/bsw/prod/autobernese/autobernese.log'),
            'format': '%(asctime)s | {user} | %(levelname)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '%',
            'level': 'DEBUG'
        },
        'campaign_templates': PosixPath('/home/bsw/prod/autobernese/templates'),
        'user_config': PosixPath('/home/bsw/prod/autobernese/autobernese.yaml'),
        'user_sections': ['station', 'campaign', 'sources']
    }
    ```

<!-- ### Given / requirements / configuration -->


## Download sources

Data acquisition from and management of external sources is a large part of the
work performed, before creating Bernese campaigns.

AutoBernese lets users download external sources from HTTP anf FTP and store
them in any available local filepath desired.

AutoBernese can download sources common to all users as well as
campaign-specific sources.

To do either, the sources must be specified in the relevant configuration file:

| Download      | File                               |
| ------------- | ---------------------------------- |
| Common data   | `autobernese.yaml`                 |
| Campaign data | `$P/<campaign-name>/campaign.yaml` |


[A separate document](download-sources.md) describes in detail how to set up
sources in the configuration files.


### `ab download`

This downloads data from the sources specified in the common AutoBernese
configuration file `autobernese.yaml`.


### `ab download -c <campaign-name>`

This downloads data from the sources specified in the campaign-specific
configuration file `campaign.yaml` in the root of the campaign directory of
campaign `<campaign-name>`.


## Campaign management

```sh
ab campaign
```

### List existing Bernese campaigns

```sh
ab campaign ls
```

### List AutoBernese details of each Bernese campaign

List campaign templates and template content.

```sh
ab campaign ls -v
```


### List available campaign-configuration templates

```sh
ab campaign templates
```


### Show content of the campaign-configuration template

```sh
ab campaign templates <template>
```

<div class="result" markdown>
  ![Dummy image](https://dummyimage.com/600x400/){ width=50% }
</div>


## Create a campaign

```sh
ab campaign create WK2222 -b 2022-08-07 -e 2022-08-13
ab campaign create WK2222 -t <template-name> -b 2022-08-07 -e 2022-08-13
```

<div class="result" markdown>
  ![Creating a campaign-configuration file](assets/create-campaign-configuration.png)
</div>


## Show the sources specified for a given campaign

```sh
ab campaign sources <campaign-name>
```


## Show the runnable tasks for a given campaign

```sh
ab campaign tasks <campaign-name>
```


## Run tasks for a given campaign

```sh
ab campaign run <campaign-name>
```


## Show what is parsed from a sitelog when creating a STA file.

```sh
ab station
ab station parse-sitelog BLAH00DNK_20230101.log
```


## Create STA file from sitelogs

```sh
ab station sitelogs2sta
ab station sitelogs2sta -f/--filename station.yaml
ab station sitelogs2sta -i BLAH00DNK_20230101.log -i BLUH00DNK_20220101.log -c BLUH -o sitelogs.STA
```


## Combine troposphere hour files to day

```sh
ab troposphere
ab troposphere status <input-path> <output-path> [BEG, END]
ab troposphere build <input-path> <output-path> [BEG, END]
```


## Show date information for a specific date or GPS week

Get general date information based on input date as GPS week, date, year+day-of-year.

```sh
ab dateinfo
ab dateinfo ymd 2022-08-07
ab dateinfo ydoy 2022 219
ab dateinfo gpsweek 2222
```


## Examine the Logfile to get more verbose output

```sh
ab logfile
```

### Station data



### Troposphere data
