AutoBernese uses configuration files to integrate with Bernese, have
customisable shared settings and defaults, as well as campaign-specific
settings.

The active configuration files are read into AutoBernese in the following order,
each file overriding the previous, when merging is possible: 1) core
functionality and default settings, 2) common user-defined settings and
defaults, and 3) campaign-specific settings, created anew or from a template
based on a previous campaign. The campaign-specific settings are only read, when
working with a campaign.

In addition, AutoBernese also has a template system that enables users to set up
re-usable campaign settings for common *campaign types* and use these templates
to create new campaigns.

The different types of configuration are shown in the table below:

| Configuration     | File                   | Location                                               | Purpose                                                                             |
| ----------------- | ---------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Core              | `env.yaml`             | Inside the package                                     | Integrate with activated Bernese environment and provide core and default settings. |
| Common            | `autobernese.yaml`     | AutoBernese runtime directory                          | Contain common data sources, campaign-creation setup and station sitelog settings.  |
| Campaign          | `campaign.yaml`        | Campaign directory                                     | Campaign-specific environment, data sources and actions                             |
| Campaign template | `<campaign-type>.yaml` | `templates` directory in AutoBernese runtime directory | Have pre-set campaign configuration for campaigns of the same type.                 |

The configuration files are in [YAML][] format, and how AutoBernese use it is
explained in the examples given below together with the required and permitted
content of each file.

[YAML]: https://yaml.org/


## Core configuration

The core configuration file makes the integration with Bernese possible, and
establishes the location of the AutoBernese runtime directory for log data and
files shared by the users of the given Bernese installation. It is built in to
the package, and the user is not supposed to edit this file. Its contents are
explained here, since the two user-edited configuration types are meant to
utilise YAML features to re-use values in this file.

The overall structure of the core configuration file looks like this.

```yaml title="Main sections of the core configuration"
bsw_env: {}
bsw_files: {}
env: ''
runtime: {}
campaign: {}
```

Each section is explained below.


### BSW environment variables

Inside the `bsw_env` section are key-value pairs whose values are the names of
relevant environment variables set by the `LOADGPS.setvar` script. The extracted
values are made available for re-use in other parts of the configuration.

```yaml linenums="1"
--8<-- "src/ab/configuration/env.yaml::33"
```

The section is a YAML mapping whose items have values that are dynamically
generated, when the document is parsed. As defined here, the key `C` for
instance, will have the string inside the the environment variable `$C` (or
`${C}` in the Perl syntax used by Bernese).

Starting from the right, the environment variable is grabbed by using the YAML
tag `!ENV` before the string `C`. When parsed as a YAML document, this invokes a
special constructor that takes the string `C` as an argument and returns the
value of the environment variable of that name.

The additional YAML syntax `&C` defines a YAML anchor (also named `C`) which
functions as a variable that can referenced and thus reused later in the
document.


### Files used by AutoBernese

The `bsw_files` section has entries for Bernese files used by AutoBernese. These
file paths are derived by referencing the dynamically-loaded environment
variables in the previous section.

```yaml linenums="35"
--8<-- "src/ab/configuration/env.yaml:35:42"
```


### Runtime settings

The `env` and `runtime` sections are settings that AutoBernese use to create and
maintain a directory `autobernese` for its runtime files (listed below). It also
defines names of configuration sections that one may override in the common
configuration file `autobernese.yaml` or, for some of them, the
campaign-specific configuration file; both described further below.

```yaml linenums="44"
--8<-- "src/ab/configuration/env.yaml:44:78"
```

As there may be more than one Bernese installation on a system, the AutoBernese
runtime directory is, currently, set to be next to the activated Bernese
installation directory `BERN54`.

!!! info "Bernese environmemt"

    The directory containing the AutoBernese runtime directory and the Bernese
    installation directory is referred to in this context, variously, as *the
    Bernese environment*, *the activated environment* or *runtime environment*.

The files in the AutoBernese runtime directory include:

*   The logfile `autobernese.log`
*   The common configuration file `autobernese.yaml` with possible overrides for
    the built-in configuration file.
*   Campaign-configuration templates inside the sub directory `templates`


### Settings overridable

The `campaign` section determines the default directory structure of a new
campaign. This section is overridable by the common configuration.

```yaml linenums="79"
--8<-- "src/ab/configuration/env.yaml:79:99"
```


## Common configuration

The common configuration file is for functionality that does not require a
Bernese campaign or which is common to all campaigns. To use common settings,
put them inside a file called `autobernese.yaml` in the AutoBernese runtime
directory. The settings work as defaults for campaigns, unless they are
overridden in the campaign-specific configuration file.

``` title="The AutoBernese runtime directory"
/path/to/environment
├── autobernese
│   ├── autobernese.log  # Log file with user-separable entries
│   ├── autobernese.yaml # Users can (and should) add this to configure
│   │                    # campaign setup and external-data download
│   │
│   └── (...)
│
├── BERN54
└── (...)
```

With this file, users may configure the following:

*   The directory structure of a new Bernese campaign
*   Directory structure for troposphere-model data
*   Common sources of external data
*   Settings for generating a STA-file from station site-log files


### Campaign-directory structure for new campaigns

```yaml title="Campaign-creation settings in autobernese.yaml" linenums="1"
--8<-- "docs/manual/assets/autobernese.yaml:1:16"
```


### Troposphere data directory structure

```yaml title="Troposphere-data settings in autobernese.yaml" linenums="18"
--8<-- "docs/manual/assets/autobernese.yaml:18:20"
```


### Data-source specification and local directory structure

```yaml title="Data source management settings in autobernese.yaml" linenums="22"
--8<-- "docs/manual/assets/autobernese.yaml:22:84"
```


### Station site-log files to use for STA-file creation

```yaml title="Station site-log data to STA-file settings in autobernese.yaml" linenums="91"
--8<-- "docs/manual/assets/autobernese.yaml:86:89"
```


## Campaign configuration

Campaigns differ by their purpose, time interval, data needed and actions
required. To *run* a Bernese campaign, AutoBernese requires a configuration file
`campaign.yaml` in the root of the campaign directory.

``` title="Location of a campaign-specific configuration"
/path/to/CAMPAIGN54
├── EXAMPLE
│   ├── (...)
│   └── campaign.yaml
│
└── (...)
```

It stores all information about the campaign, defines what data sources to
retrieve and what actions [tasks] to perform. It also allows one to (re-)define
environment variables which can be helpful, if a given campaign uses a special
directory for the Bernese `.PCF`-files it needs.

One can build the campaign configuration file manually, e.g. by copying the
example in this manual. But AutoBernese is made to automatically create a
Bernese campaign from a pre-defined configuration template. AutoBernese comes
with an empty, default template to allow basic campaign-creation.


### Creating a new campaign configuration

A campaign-specific configuration file is **created** by AutoBernese by
combining information gathered at the campaign creation time with a
campaign-configuration template. The combination of these metadata and the
template go into a campaign-specific configuration file `campaign.yaml` which is
added to root of the newly-created campaign directory.

The gathered data are stored in a `metadata` section at the top. Its purpose is
to specify the YAML anchors used in the template part of the
campaign-configuration template file. The metadata are also used when displaying
verbose information about the created campaign, when using AutoBernese to list
all the campaigns in the environment.

```yaml title="Sections in a campaign-specific configuration file"
# Required
metadata: {}

# Optional, but needed to make use of autobernese
environment: {}
tasks: []
sources: []
clean: []
```

It is also possible to use AutoBernese on existing campaigns by, manually,
adding a `campaign.yaml` file to the campaign-directory root. The quick-start
section provides an example of such a file, which is prepared to work with the
EXAMPLE campaign that comes bundled with Bernese 5.4 (works for releases
2022-10-23 and 2023-10-16).

For reference, you can se the contents of that file by unfolding the section
below.

??? note "Unfold to see an AutoBernese configuration for the pre-created EXAMPLE campaign"

    As it is only the presence of the configuration file that enables AutoBernese to
    do its work, existing campaigns can be run with AutoBernese by adding a
    campaign-configuration file to those campaign directories.

    Below is an example of the campaign-configuration template `campaign.yaml`,
    which, when put into the EXAMPLE campaign directory
    `/path/to/CAMPAIGN54/EXAMPLE` enables AutoBernese to use this existing campaign:

    ```yaml title="EXAMPLE campaign configuration"
    --8<-- "docs/manual/assets/campaign.yaml"
    ```

What follows is a description of the contents in each main section of the
campaign-specific configuration file.


### The `metadata` section

The `metadata` section is there, because the data written here can be referred
to in the rest of the document using the YAML anchors [the words starting with
`&...`] prefixing the values for each key in the section. The keys are seen in
the task lists, which is explained below.

```yaml title="Campaign metadata"
metadata:
  version: &version 0.3.0
  username: &username USERNAME
  created: &created 2024-04-08
  template: &template example
  campaign: &campaign EXAMPLE
  beg: &beg 2019-02-13
  end: &end 2019-02-14
```

The `metadata` section contains data about the campaign. The first four items in
the mapping contain the context in which the campaign was created. `version`
refers to the AutoBernese version, `username` is the user that created the
campaign, `created` is the campaign-creation time, and `template` is the
filename without suffix for the campaign template that was used to create the
[in this case `example.yaml`].

The last three items are shortcuts available, primarily, for the tasks in the
`tasks` section. The string value in `campaign` is the name of the directory in
the campaign directory containing the Bernese campaign. The *YAML anchor*
`&campaign` can be resolved in other places in the YAML document to re-use the
string value, in this case `EXAMPLE`. The same is the case for the items `beg`
and `end` which denote the beginning and end date [both included] that the
campaign covers.

!!! tip "Key idea"

    This is particularly useful for specifying a BPE task to be run for the
    campaign, since the campaign name, thanks to the YAML specification, need not be
    repeated explicitly, but can be written once. Similarly, as illustrated, one may
    use the beginning and end dates to define the beginning and end date for which a
    given task needs to be run.


### The `environment` section

Adding an `environment` section to a campaign configuration, you are able to set
or update environment variables for the given campaign at runtime. The variables
are set after the campaign configuration has been loaded, so it affects only
actions invoked by AutoBernese afterwards which rely on these variables.

For Bernese, campaign-specific input can be defined in a single location from
which values are created/updated at runtime, 1) dynamically, changing
directories, before running Bernese, and 2) propagating input data to `.PCF`
files and scripts using them.

This addresses three issues:

*   **Reproducibility**

    By default, each user has their own Bernese-user environment (the directory
    `$U`) with `.PCF` files and options set for their work. These files require
    effort to maintain, and different users doing the same calculations, might
    have diverging settings in their user-environment. This can be a problem.

    Settings should come from a single source of truth if one wants to maintain
    a high-quality workflow and avoid human errors.

*   **Adaptability**

    The `.PCF` files in a Bernese-user environment also have variables for
    easier re-use throughout the file. This makes them easier to maintain and
    adapt for campaigns of the same type. The values of these variables can be
    set from existing environment variables, which means that users can avoid
    changing the `.PCF` file itself and thus use the same file across different
    campaigns. This adaptability is great.

    But as with the need for reproducibility, having a single source of settings
    reduces maintenance effort and improves quality assurrance, by needing fewer
    mechanisms for changing those settings, dynamically.

*   **Separation of concerns**

    Having all one's critical `.PCF` files and scripts in one directory, and
    maybe having some `.PCF` files use the same `OPT`-directories for their
    input, can be good for reproducibility and adaptability.

    But the maintenance effort increases, when complexity of the file
    organisation and functionality dependence increases. The overview may be
    lost and/or require a specialist to see the consequences of changes in
    shared `.INP` files and scripts. Testing also becomes harder with increasing
    complexity. If there is no testing done to see what these consequences might
    be, it is not easy to ascertain the quality of the results that come out.

    Similarly, a user might share a common workflow with colleagues in other
    organisations. Having the workflow stored separate from one's own
    user-environment allows for a much cleaner way to maintain and test this
    workflow, but also to share it, e.g. using distributed version control
    systems such as Git or simply copying from a shared FTP server.

The `environment` section solves these issues in the following ways:

1.  A user should be able to specify what directory to use as for a given
    campaign in order to separate workflows between different campaign types,
    thus decreasing maintenaince effort and allow them to, easily, share
    workflows with other organisations.

    The example below shows how to do this, by *changing* the variable `$U` to
    point to another directory.

2.  A user should be able to change or add environment variables as needed for
    different campaigns, thus having a single source from which to control the
    variable input in e.g. `.PCF` files, and in turn make use of these files for
    different campaigns easier.

    The example below shows how a new environment variable
    `AB_PATH_CAMPAIGN_REFDIR` is defined and added during runtime. Its value, a
    path to the given campaign, is thus available to any software component run
    by AutoBernese using this as input.

```yaml title="Custom environment variables for a campaign"
environment:
- variable: U
  # Use a campaign-specific directory with only the needed PCF files and settings
  value: !Path [*U, .., campaign_type]

# Set a variable that can be used e.g. inside the the campaign-specific PCF files.
- variable: AB_PATH_CAMPAIGN_REFDIR
  value: !Path [*D, REF54, *campaign]
```

!!! question "Is this safe?"

    **Answer:** Yes.

    The user may set/change their environment variables before execution of any
    command, so the mutation of any variable is already possible.

Redirection is a powerful thing and can be done at many levels, and one of the
main powers of Bernese GNSS Software is the use of environment variables to
define where things are located. AutoBernese is designed to take advantage of
this without forcing the user to have to re-structure their entire workflow
setup, but, instead, make it easier to use the existing abstractions and
centralise control at the campaign-level, not as a requirement, but as a
liberating alternative.


### The `tasks` section

When *running* a campaign using the `ab campaign run` command, AutoBernese looks
in the `tasks` section of the configuration file, loads the selected task
definitions and runs the tasks they define in the order they are defined.

The following is an example of a single task definition which illustrates the
features implemented for our primary usecase: It instructs AutoBernese to run
the Bernese Processing Engine for each day in the given campaign. The repetitive
pattern is encoded once as a template, and the actual sessions run are based on
a set of parameters, here a single one, the `date` for which to run the BPE:

```yaml title="Example of a task definition"
tasks:

- identifier: BPE_PPP
  description: Run the BPE using PPP.PCF
  run: RunBPE
  arguments:
    pcf_file: PPP
    campaign: *campaign
    year: '{date.year}'
    session: '{date.doy:0>3d}0'
    sysout: 'PPP_{date.doy:0>3d}0'
    status: 'PPP_{date.doy:0>3d}0.RUN'
    taskid: PPP
  parameters:
    date: !DateRange {beg: *beg, end: *end}
```

As seen, the `campaign`-argument gets its value by referencing the YAML alias
`*campaign` which in turn is defined in the `metadata` section of the
configuration file.

Arguments `year`, `session`, `sysout` and `status` use the [Python format-string
syntax][PYDOC-FORMAT-STRINGS] to access the four-digit year or day-of-year [doy]
of the parameter `date`.

As mentioned, the dates that `date` refers to are the ones covering the
campaign. The sequence is generated at runtime, when the YAML aliases `*beg` and
`*end` are sent to a custom constructor in AutoBernese by using the custom YAML
tag `!DateRange` in front of the mapping.


#### The task definition

As seen in the above example, a task definition is a mapping that in a compact
way may define a larger set of tasks. It names an API-level function to run, the
arguments needed and possible parameters used in the argument mapping. When
loaded, the task definition expands to a set of concrete tasks that are run with
the `run` sub-command. So far, tasks are run, sequentially.

A task definition needs a unique `identifier`, a `description`, something to
`run` as a task, `arguments` (if needed) for the task and `parameters` (if
specified in the `arguments` section) that will be used to create a set of
concrete tasks based on the task definition. If no parameters are used, the
arguments provided are used to perform a single task. If no arguments are
needed, the API-level function is run as a single task with no arguments given
to the function.

Requirements:

*   The identifier must be without whitespace. It is used, when selecting only
    specific tasks definitions. (The concrete tasks may still be several.)

*   The description can be long, but short descriptions are easier to read when
    printed to the terminal.

*   `run` needs a key to a mapping, currently, hard-coded in AutoBernese; or a
    reference to the API-level Python function that you want to run.

*   `dispatch_with` needs a value in the same way as the `run` part. If not
    present, the arguments are sent directly to the API-level function refered
    to by `run`. When defined, the arguments are first sent through the function
    pointed to by `dispatch_with` to be pre-processed or to convert their input
    to match the signature of the API-level function.

    **The point of the dispatch function is to make independent API-level calls
    move up to a corresponding task so that the task runner may handle the
    delegation of ressources at a finer level.**


*   Keyword arguments inside the `arguments` section contain arguments readable
    by the function in `run` or, if used, `dispatch_with`.

*   Any keyword arguments using string templates, must have a key of the same
    name in the `parameters` section. The value must be a sequence or iterable
    of values that the parameter may take inside any of the argument string
    template formats.

[PYDOC-FORMAT-STRINGS]: https://docs.python.org/3/library/string.html#formatstrings

!!! info "More examples using built-in `run` and `dispatch_with` shortcuts"

    === "`Compress`"

        This example uses `Compress` which points to a function that takes a concrete
        path. The `dispatch_with` key uses a shortcut to a dispatch function which
        resolves any wildcards in the given paths.

        ```yaml title="Example of a task definition"
        tasks:

        - identifier: GZIP
          description: Compress results using gzip
          run: Compress
          dispatch_with: DispatchCompress
          arguments:
            fname: !PathStr [*P, *campaign, '{filename}']
          parameters:
            filename:
            - /OUT/*.PRC
            - /SOL/*.SNX
            - /ATM/*.TRO
        ```

    === "`SFTPUload`"

        This example uses `SFTPUpload` which points to a function that takes the list of
        files and the single remote directory and transfers them in a batch operation to
        the server.

        ```yaml title="Example of a task definition"
        tasks:

        - identifier: SFTP_TO_COLLABORATION
          description: Upload campaign results to collaboration directory
          run: SFTPUpload
          arguments:
            host: ftp.example.com
            pairs:
            - filename: !PathStr [*P, *campaign, '{filename}']
            remote_dir: !PathStr [Collaboration/GNSS/, '{date.gps_week}']
          parameters:
            date: [*beg]
            filename:
            - /STA/*.CRD
            - /OUT/*.PRC.gz
            - /OUT/*.SUM
            - /SOL/*.SNX.gz
            - /ATM/*.TRO.gz
        ```




### The `sources` section

Campaign-specific sources of external data can be specified in a `sources` section
in the campaign configuration.

As illustrated in the EXAMPLE-campaign configuration file, a single FTP source
with two files needed for the built-in process-control file `ITRF.PCF` is
included so that the data can be downloaded to the DATAPOOL area to be used in
this (and in this case, other) campaigns.

```yaml
sources:

- identifier: ITRF14
  description: IERS data needed for the EXAMPLE campaign
  url: https://datacenter.iers.org/products/reference-systems/terrestrial/itrf/itrf2014/
  filenames:
  - ITRF2014-IGS-TRF.SNX.gz  # 1.4 GB
  - ITRF2014-psd-gnss.dat  # 38 KB
  destination: !Path [*D, ITRF14]
```


### The `clean` section

With the campaign command `clean`, it is possible to specify directories at the
root of the campaign directory which will have their entire content deleted, if
the user grants it when prompted.

To use the `clean` command, add a `clean` section to the campaign (template)
configuration and provide a list of directories that exist at the root of the
campaign.

```yaml title="Example of a clean section in a campaign-specific configuration file"
clean: [SOL, OUT]
```


## Campaign templates

A main feature of AutoBernese is the ability to store common campaign settings
as templates and use them to create campaigns of the same type. This will
further speed up common workflows, since newly-created Bernese campaigns are
ready to be 'run' with AutoBernese. By adding different templates for different
campaign types, users avoid having to copy over settings to set environment
variables, download data, and run tasks.

This *campaign type* is defined by a template campaign-configuration file in
the `templates` directory of the AutoBernese runtime directory.

``` title="Campaign-configuration template location in the AutoBernese runtime directory"
/path/to/environment
├── autobernese
│   ├── (...)
│   └── templates        # Directory for user-created templates,
│       │                # one for each campaign type
│       │
│       └── default.yaml # This default file is used as
│                        # template if none specified.
├── BERN54
└── (...)
```

The default campaign template is empty and comes with the AutoBernese package,
but is selected if none given by the user.

!!! note "Template maintenance"

    Over time, templates will need to be changed. Changes to templates will not
    change the configuration in existing campaigns, and these would need to be
    edited, manually. However, needing to 're-run' these campaigns anyway, it might
    be safer to start over and create new campaigns to 're-create' the output.


## Notes on Python-string templates in YAML documents

This section describes some caveats when using Python string template as values
in a YAML document.

Python has multiple ways to work with strings, and many of the string-values
given in the AutoBernese configuration files have content that requires soe
knowldge about Python's Template strings. In addition, the format of these
strings may clash with the YAML syntax, so a few potential problems and
solutions are shown below.


### Caveats on difference between Template strings and `f` string syntax

This example shows the difference in Python syntax between two Python-string
types:

=== "`f` string"

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

=== "String template"

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
format.

### Clash with the the YAML syntax

There is a subtle drawback in clarity, when the string template begins with a
template part, since it clashes with the YAML syntax for a mapping which also
begins and ends with `{` and `}`, respectively. In these cases, one must,
explicitly, put quotes around the string:

=== "Without explicit quotes"

    ```python title="Example"
    import yaml
    s = """\
    some configuration key: a string with {date.day}
    another configuration key: {template} is at the beginning of the string.
    """
    yaml.safe_load(s)
    ```

    ``` title="Output"
    # Output:
    # ParserError: while parsing a block mapping
    #   in "<unicode string>", line 1, column 1:
    #     some configuration key: a string ...
    #     ^
    # expected <block end>, but found '<scalar>'
    #   in "<unicode string>", line 2, column 37:
    #     another configuration key: {prefix} is at the beginning of the string.
    ```

=== "With explicit quotes"

    ```python title="Example"
    import yaml
    s = """\
    some configuration key: a string with {date.day}
    another configuration key: '{template} is at the beginning of the string.'
    """
    yaml.safe_load(s)
    ```

    ``` title="Output"
    # Output:
    # {
    #   'some configuration key': 'a string with {date.day}',
    #  'another configuration key': '{template} is at the beginning of the string.'
    # }
    ```
