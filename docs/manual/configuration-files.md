
This section describes the various ways in which to configure shared AutoBernese
settings and build templates for campaign-specific configuration files.

## The built-in configuration file

The AutoBernese package comes with a built-in configuration that:

*   Determines what environment variables set by the `LOADGPS.setvar` script to
    load into AutoBernese. These, in turn, are made available for re-use in
    other configuration settings, so that can these integrate into relevant
    Bernese directories such as the DATAPOOL [`${D}`] and SAVEDISK [`${S}`]
    areas.

*   Enables AutoBernese to create a directory for runtime files at the same
    directory level as the activated Bernese-installation directory. Runtime
    files are the logfile, campaign templates and a file with configuration
    overrides for common user settings.

*   Provides default settings for campaign creation, external-data source
    specification and sitelog-to-STA file transformation, the latter being a
    specific need we have at the agency.

The built-in configuration file is prepended the campaign-specific configuration
files, so that the relative paths and other data can be re-used here as well.
(More on this later below.)


??? code "Look at the built-in configuration file"

    === "Raw"

        ```yaml title="Built-in configuration file `env.yaml`" linenums="1"
        --8<-- "src/ab/configuration/env.yaml"
        ```

    === "BSW environment variables"

        ```yaml title="Built-in configuration file `env.yaml`" linenums="1" hl_lines="1-30"
        --8<-- "src/ab/configuration/env.yaml"
        ```

    === "Runtime settings"

        ```yaml title="Built-in configuration file `env.yaml`" linenums="1" hl_lines="43-69"
        --8<-- "src/ab/configuration/env.yaml"
        ```

    === "Settings overridable"

        ```yaml title="Built-in configuration file `env.yaml`" linenums="1" hl_lines="71-103"
        --8<-- "src/ab/configuration/env.yaml"
        ```


## Configuration locations

### Common user configuration file and templates in the runtime directory

When run, AutoBernese creates a *runtime directory* at the same directory level
as the Bernese installation directory `BERN54`, i.e .in the parent directory of
the `$C`.

``` title="AutoBernese runtime directory is in the parent directory of `$C`"
/path/to/environment
├── autobernese     # AutoBernese runtime directory automatically
│                   # created one level up from Bernese-installation directory
│
├── BERN54          # Bernese 5.4 installation directory, a.k.a. `$C`
└── ...
```

As indicated above, a few sections of the built-in AutoBernese configuration can be overridden with a common user configuration file.

<!-- Adding a file `autobernese.yaml` in the AutoBernese runtime directory, sections `station`,  -->

*   Adding a file `autobernese.yaml` in the AutoBernese runtime directory,
    users may configure e.g. common sources of external data and the
    directory structure of a new Bernese campaign.

*   Adding different templates for different campaign scenarios, i.e. campaign
    types, will speed up the process of creating a new campaign, getting it
    ready by downloading data, and running the BPE tasks set in the
    campaign-specific configuration file.

``` title="Environment-specific files in the AutoBernese runtime directory"
/path/to/environment
├── autobernese
│   ├── autobernese.log  # Log file with user-separable entries
│   ├── autobernese.yaml # Users can (and should) add this to configure
│   │                    # campaign setup and external-data download
│   │
│   └── templates        # Directory for user-created templates,
│       │                # one for each campaign type
│       │
│       ├── default.yaml # This default file is used as
│       │                # template if none specified.
│       │
│       └── example.yaml # Example of a user-created template
│                        # for campaign type named `example`.
│
├── BERN54
└── ...
```


<!--Additional content that can be added is

*   A configuration file `autobernese.yaml` common to all users that will
    override some sections of the built-in configuration that comes with the
    package.

    This file must be added manually by the user(s).

    [TODO: Read more on how to confgure AutoBernese](TODO).

*   A directory `templates` for campaign-configuration template files. [TODO: See more on creating templates below](TODO).

*   In short, the user-defined configuration file that AutoBernese can read must be
located at the following path [using the set Bernese environment variables]:
`$C/../autobernese/autobernese.yaml`.
-->


<!-- === "`ab/configuration/env.yaml`"

    ```yaml title="BSW environment loaded with each configuration" linenums="1" hl_lines="1"
    --8<-- "src/ab/configuration/env.yaml::24"
    ``` -->

AutoBernese lets users of a given Bernese installation share a common
configuration file [see `autobernese.yaml` below], where, for instance, you can
maintain the default campaign-directory content as well as a list of common data
sources to download.

```yaml title="Configuration overrides in `autobernese/autobernese.yaml`"
--8<-- "docs/manual/assets/autobernese.yaml:6"
```

Campaign-specific sources and, especially, PCF files to run with BPE, are
managed from a campaign-specific configuration file in the root of the Bernese
campaign directory.

```yaml title="Configuration used for the EXAMPLE campaign in `$P/EXAMPLE/campaign.yaml`"
--8<-- "docs/manual/assets/campaign.yaml"
```

Based on the assumption that most users do the same things over and over again
to different data sets, and thus to avoid copying-and-pasting recurring
processing workflow between Bernese campaigns, AutoBernese has the concept of a
*campaign type* which is defined by a template campaign-configuration file in
the templates directory of the AutoBernese runtime directory [see `example.yaml`
below].

```yaml title="Template on which the EXAMPLE-campaign configuration is based on `autobernese/templates/example.yaml`"
--8<-- "docs/manual/assets/campaign.yaml:10:"
```

As seen above, the difference between a campaign-configuration file and its
template it the metadata section that is part of the concrete Bernese campaign.
AutoBernese adds the metadata section automatically, but a user can also ad it
manually, if the configuration is made for an existing campaign such as the
EXAMPLE campaign.

Using a campaign-specific configuration file in the root of a Bernese-campaign
directory, AutoBernese is able to do two things at the campaign level:

1.  Download campaign-specific data from sources specified in the same way as in
    the general AutoBernese configuration file.
2.  Run the Bernese Processing Engine for PCF files with campaign-specific
    settings.

AutoBernese lets a user define configuration templates for common campaign
scenarios, where the only difference is in the time interval for which a given
campaign is created and run.

A default campaign template `default.yaml` is added to the `autobernese`
directory, automatically, when the command `ab campaign` is run. If the file
already exists, AutoBernese does nothing.

As the user create a campaign with AutoBernese, if no other template name is
specified, the default campaign template is used. Therefore, this file should be
edited to suit the most common scenario. Even so, having more than one
configuration template will make common scenarios faster to setup.

With this template-management system, you only need to set up your Bernese
campaigns once, or rarely. AS it is only the presence of the configuration file
that enables AutoBernese to do its work, existing campaigns can be 'runable'
with AutoBernese by adding a campaign-configuration file to those campaign
directories.


---

#### The `metadata` section

The `metadata` section contains data about the campaign. The first four items
in the dictionary contain the context in which the campaign was created.
`version` refers to the AutoBernese version, `username` is the user that
created the campaign, `created` is the campaign-creation time, and `template`
is the filename without suffix for the campaign template that was used to
create the [in this case `example.yaml`].

The last three items are shortcuts available, primarily, for the tasks in the
`tasks` section below. The string value in `campaign` is the name of the
directory in the campaign directory containing the Bernese campaign. The *YAML
anchor* `&campaign` can be resolved in other places in the YAML document to
re-use the string value, in this case `EXAMPLE`. this is particularly useful for
specifying BPE tasks to be run for the campaign, since the campaign name, thanks
to the YAML specification, need not be repeated explicitly, but can be written
once. The same is the case for the items `beg` and `end` which denote the
beginning and end date [both included] that the campaign covers.

The metadata section is there, because the data written here can be referred to
in the rest of the document using the YAML anchors [the words starting with
`&...`] prefixing the values for each key in the section. The keys are seen in
the task lists, which is explained below.


#### The `tasks` section

A task in the list of tasks is something that is runnable by AutoBernese. Each
list item specifies something that AutoBernese may initialise and start, when
user decides to 'run' the campaign.

For now, AutoBernese only has one type of task, which is the primary goal of
the first release: The concept of a BPETask. Using the YAML tag `!BPETask`
before the content of the list-item, AutoBernese will run the BPE Perl module
that is included in BSW.

<!-- For the `EXAMPLE` campaign, a single task is specified to use the `PPP.PCF`
file included in the BSW user scripts. As specified here, the task has a
name [`name`] used to display what is going on, some arguments
[`arguments`] which are sent to the Bernese Processing Engine. `arguments`
contain a dictionary with items having a string to be used with the BSW BPE
program. -->

```yaml
tasks:

- !BPETask
  name: Run PPP for the EXAMPLE campaign
  arguments:
    pcf_file: PPP
    campaign: *campaign
    year: '{date.year}'
    session: '{date.doy:0>3d}0'
    sysout: 'PPP_{date.doy:0>3d}0'
    status: 'PPP_{date.doy:0>3d}0.RUN'
    taskid: PP
  parameters:
    date: !DateRange {beg: *beg, end: *end}

```

Here, the YAML alias `&campaign` is referred to with the syntax `*campaign` so
that, in this case, the name of the campaign directory is inserted, when the
configuration file is loaded.

Some of the strings given to the other items, e.g. `year` and `session` are
Python format strings [more on this [below][F-STRINGS]]. The `date` reference
is an AutoBernese GPSDate which has the day-of-year property `doy` that can
be used inside the strings.

[F-STRINGS]: #how-to-get-things-right-with-pythons-format-strings-f-strings

To use template strings requires that a `parameters` item is included as part
of the BPETask. The `parameters` dictionary must have items with the keys
used inside the Python format strings. The values must be a sequence of possible values.

In this case, the value of `date` in the `parameters` dictionary is another
AutoBernese construction, denoted with the YAML tag `!DateRange`. When
resolved as the document is loaded, the value of `date`is a list of
AutoBernese `GPSDdate` instances, one for each day in the interval specified.
Here, the power of the metadata section is seen, as the dates defining the
Bernese-campaign interval are referenced by their YAML alias. The user
therefore only needs to write these dates once during campaign-creation
time.

When runnning the tasks, each task is resolved to the concrete set of possible
values that BPE can receive, and the BPE is run for each concrete given by
the task specification. IN this case, the BPe will run for each of three days
that the EXAMPLE campaign stretches over.



!!! note "Python format strings"

    The strings using the Python format-string syntax are explicitly written
    as strings with quotes, since they contain Python syntax for template
    strings that clash with YAML syntx for dictionaries.


## More on campaign tasks


What is runnable are Python-object instances in AutoBernese that has a `run()`
method. A `BPETask` is such YAML allows users to create tags that can be
specified by the software that loads the YAML document, and

---



## How to get things right with Python's string templates and format strings [`f` strings]

```python
import datetime as dt

date = dt.date(2019, 2, 13)
date.day
# 13
f'{date.day}'
# '13'
f'{date.day:3d}'
# ' 13'
f'{date.day:03d}'
# '013'
```

Using string templates, the above would look like this:

```python
import datetime as dt

date = dt.date(2019, 2, 13)
date.day
# 13
'{date.day}'.format(date=date)
# '13'
'{date.day:3d}'.format(date=date)
# ' 13'
'{date.day:03d}'.format(date=date)
# '013'
```

String templates are used in the YAML files that are used as configuration-file
format. Note that there is a subtle drawback in clarity, when the string
template begins with a template part, since it clashes with the YAML syntax for
a mapping which also begins and ends with `{` and `}`, respectively:

```python
import yaml
s = """\
some configuration key: a string with {date.day}
another configuration key: {template} is at the beginning of the string.
"""
yaml.safe_load(s)
# Output:
# ParserError: while parsing a block mapping
#   in "<unicode string>", line 1, column 1:
#     some configuration key: a string ...
#     ^
# expected <block end>, but found '<scalar>'
#   in "<unicode string>", line 2, column 37:
#     another configuration key: {prefix} is at the beginning of the string.
```

In these cases, one must, explicitly, put quotes around the string:

```python
import yaml
s = """\
some configuration key: a string with {date.day}
another configuration key: '{template} is at the beginning of the string.'
"""
yaml.safe_load(s)
# Output:
# {
#   'some configuration key': 'a string with {date.day}',
#  'another configuration key': '{template} is at the beginning of the string.'
# }
```
