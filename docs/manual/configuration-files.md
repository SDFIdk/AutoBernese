AutoBernese uses configuration files to integrate itself with Bernese and
determine actions common to all campaigns and ones that are specific to each
campaign. Core functionality is kept inside the package installation directory,
whereas the common configuration and campaign-specific configuration are stored
in the AutoBernese runtime directory and in the root of the specific campaign
directories, respectively.

Bernese is used for different end-results which the campaign system reflects.
Using AutoBernese, users can create re-usable campaign settings for common
campaign types and have AutoBernese use these templates to create new campaigns.

Thus, there are three configuration files in play, when you run a campaign: 1)
core functionality, 2) common settings and 3) campaign-specific settings, and
they are read into AutoBernese in that order, each file overriding the previous,
when possible. The campaign template files are not active, but only have their
data copied over, when a new campaign is created using them.

<!-- ""AutoBernese uses configuration files to integrate itself with Bernese, using the
same environment variables to know where relevant files and directories are on
the filesystem. There are three configuration files in play, when you run a
campaign: 1) core functionality, 2) common settings and 3) campaign-specific
settings.
"" -->

<!--
"AutoBernese uses configuration files to integrate with Bernese by using its
environment variables allowing the user to switch between the Bernese GUI and
the AutoBernese command-line interface, 2) set up  There are three configuration
files in play, when you run a campaign: 1) core functionality, 2) common
settings and 3)
"
-->

!!! info "Recapitulation"

    The goal of AutoBernese is automation and reproducibility in order to reduce
    human error and achieve higher-quality end-products, easier and faster.

    AutoBernese is, mainly, focused on operating Bernese without the GUI and
    replicating workflows common to all campaigns. This means that it so far, by
    design, puts the campaign workflow at the centre, while at the same time being
    ignorant of the user running it. For AutoBernese, it means that there are
    campaign configurations, and not user-specific configurations, all though this
    could be made possible, it would work against the principle of re-producibility.
    End-products should not depend on the user that created them.

    <!--
    The choice of having each user have their own user directory is irrelevant to
    the actual use of Bernese, since the dynamic location that each user obtains by
    using the `$HOME` environment variable can be replaced with a fixed value so
    that all users have the same path. AutoBernese lets users change the environment
    variables at runtime which allows users to, completely, move away from
    user-specific directories.
    -->

    <!--
    A newly-added feature, changing the environment means that a specific campaign
    type can, as defined in its template, change the 'user' directory `$U` and set
    it to a destination which looks like a user directory, but only contains
    campaign-type-specific files. The PCF files files may then include environment
    variables set dynamically by the campaign-specific configuration. This in turn
    would remove the need for editing PCF files for each specific campaign. On top
    of this, the campaign-type-specific 'user' directory can then be
    version-controlled and shared, internally, or even internationally, between
    different organisations that need to have the same workflow for their
    collaboration.
    -->


These files are in YAML format and makes heavy use of the format's features. How
this is done is explained in the examples given below.

The three types of configuration and the template concept are shown in the table
below:

| Configuration     | File                   | Location                                               | Purpose                                                                                  |
| ----------------- | ---------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Core              | `env.yaml`             | Inside the package                                     | Integrate with activated Bernese environment and provide core and some default settings. |
| Common            | `autobernese.yaml`     | AutoBernese runtime directory                          | Contain common data sources, campaign-creation setup and station sitelog settings.       |
| Campaign          | `campaign.yaml`        | Campaign directory                                     | Campaign-specific environment, data sources and actions                                  |
| Campaign template | `<campaign-type>.yaml` | `templates` directory in AutoBernese runtime directory | Have pre-set campaign configuration for campaigns of the same type.                      |

The core configuration file makes the integration wth Bernese possible, and
establishes the location of the AutoBernese runtime directory for log data and
files shared by the users of the given Bernese installation.

In the AutoBernese runtime directory, is a configuration file used for common
things that need to be done for the users. Common sources of data to be
synchronised or common settings to apply in all campaigns are put here in order
to avoid duplication and thus errors or unwanted differences in workflow between
different users.

Each Benese campaign requires a configuration in the root of the campaign
directory. It has information about the campaign and e.g. defines
campaign-specific data sources and actions that let AutoBernese run the campaign
from the command line.

Last, but not least, a main feature of AutoBernese is to create campaigns that
are similar in goal but uses different input. This is achieved with the
campaign-configuration templates. Once set up, they will make it easy to create
new capaigns of a given type.

The required and permitted content of each file is explained and illustrated
below.


## Core configuration

Inside the installed AutoBernese package is the core-configuration file
`env.yaml`.

Before being parsed and loaded into AutoBernese, the contents of the core
configuration file is concatenated with the common and, if relevant, the
campaign-specific configuration file. This means that settings available in the
core configuration can be used in the remaining configuration files.

Reusable values include relative paths that make it possible to e.g. download
data sources to the DATAPOOL area and create new campaigns in the CAMPAIGN54
directory.

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

Inside the `bsw_env` section are entries that, when loaded, read in the values
of relevant environment variables set by the `LOADGPS.setvar` script. The values
are then available for reference in other configuration settings.

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
--8<-- "src/ab/configuration/env.yaml:35:73"
```


### Runtime settings

The `env` and `runtime` sections are settings that AutoBernese use to create and
maintain a directory for its runtime files. Since there may be more than one
Bernese installation, the runtime directory is set to be in the same directory
as the root directory containing the activated Bernese installation `BERN54`.

```yaml linenums="75"
--8<-- "src/ab/configuration/env.yaml:75:106"
```

The runtime files include:

*   The logfile `autobernese.log`
*   Campaign templates inside the sub directory `templates`
*   The common configuration file `autobernese.yaml` with possible overrides for
    the built-in configuration file.


### Settings overridable

The `campaign` section determines the default directory structure of a new
campaign. This section is overridable by the common configuration.

```yaml linenums="108"
--8<-- "src/ab/configuration/env.yaml:108"
```


## Common configuration

<!-- AutoBernese lets users of a given Bernese installation share a common
configuration file [see `autobernese.yaml` below], where, for instance, you can
maintain the default campaign-directory content as well as a list of common data
sources to download. -->

Provides default settings for campaign creation, external-data source
specification and, specificly for us at the agency, sitelog-to-STA file
transformation.

As mentioned above, a few sections of the built-in AutoBernese configuration can
be overridden/added with a common user configuration file `autobernese.yaml` in
the AutoBernese runtime directory whose path, in turn, is determined at runtime.

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
--8<-- "docs/manual/assets/autobernese.yaml:22:89"
```


### Station site-log files to use for STA-file creation

```yaml title="Station site-log data to STA-file settings in autobernese.yaml" linenums="91"
--8<-- "docs/manual/assets/autobernese.yaml:91:94"
```


## Campaign configuration

Campaign-specific sources and, especially, PCF files to run with BPE, are
managed from a campaign-specific configuration file in the root of a Bernese
campaign directory.

``` title="Environment-specific files in the AutoBernese runtime directory"
/path/to/CAMPAIGN54
├── EXAMPLE
│   ├── (...)
│   └── campaign.yaml
│
└── (...)
```

Using this configuration file allows AutoBernese to work with the campaign,
specifically, by doing two things at the campaign level:

1.  Download campaign-specific data from sources specified in the same way as in
    the general AutoBernese configuration file.
2.  Run the Bernese Processing Engine for PCF files with campaign-specific
    settings.


### Creating a new campaign configuration

A campaign-specific configuration file is **created** by autobernese by
combining information gathered at the campaign creation time with a
campaign-configuration template. The combination of these metadata and the
template go into a campaign-specific configuration file `campaign.yaml` which is
added to root of the newly-created campaign directory.

The gathered data are stored in a `metadata` section at the top. Its purpose is
to specify the YAML anchors used in the template part of the
campaign-configuration template file. The metadata are also used when displaying
verbose information about the created campaign, when using autobernese to list
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
EXAMPLE campaign that comes bundled with Bernese 5.4.

For reference, you can se the contents of that file by unfolding the section
below.

??? note "Unfold to see an AutoBernese configuration for the pre-created EXAMPLE campaign"

    As it is only the presence of the configuration file that enables AutoBernese to
    do its work, existing campaigns can be 'runable' with AutoBernese by adding a
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
the dictionary contain the context in which the campaign was created. `version`
refers to the AutoBernese version, `username` is the user that created the
campaign, `created` is the campaign-creation time, and `template` is the
filename without suffix for the campaign template that was used to create the
[in this case `example.yaml`].

The last three items are shortcuts available, primarily, for the tasks in the
`tasks` section. The string value in `campaign` is the name of the directory in
the campaign directory containing the Bernese campaign. The *YAML anchor*
`&campaign` can be resolved in other places in the YAML document to re-use the
string value, in this case `EXAMPLE`. this is particularly useful for specifying
BPE tasks to be run for the campaign, since the campaign name, thanks to the
YAML specification, need not be repeated explicitly, but can be written once.
The same is the case for the items `beg` and `end` which denote the beginning
and end date [both included] that the campaign covers.


### The `environment` section

Adding an `environment` section to a campaign configuration, you are able to set
or update environment variables for the given campaign. This is a powerful
feature that addresses two problems:

```yaml title="Custom environment variables for a campaign"
environment:
- variable: U
  # Use a campaign-specific directory with only the needed PCF files and settings
  value: !Path [*U, .., campaign_type]

# Set a variable that can be used inside the the campaign-specific PCF files.
- variable: AB_PATH_CAMPAIGN_REFDIR
  value: !Path [*D, REF54, *campaign]
```

Use case: A user should be able to specify, freely, where to have a Bernese-user
environment.

This way, the user no longer needs to set them in an external script or at the
command line before every command.

Additionally, adding new variables using values from the metadata section, these
can be used in the PCF files that are used in that user environment (or the
commons ones in the default user directory), and so in a dynamic way, the same
PCF files can be re-used for different campaigns, but still making it possible
to separate e.g. campaign-specific DATAPOOL sub directories or ditto for the
end-products of each campaign.

!!! question "Is this safe?"

    **Answer:** Yes.

    Since the user may set/change their environment variables before execution of
    any command, the mutation of any variable is already possible. Therefore, this
    feature is not decreasing the safety.

    What it does is making the user(s) able to have specific environment variables
    set for different campaign types, and the campaign-template system again makes
    replication very easy as well as dynamic, since the values being set can depend
    on the values in the `metadata` section of a specific campaign.


### The `tasks` section

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
  identifier: PPP
  description: Run PPP for the EXAMPLE campaign
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

Here, the YAML *anchor* `&campaign` is referred to with the syntax `*campaign`
[a YAML *alias*] so that, in this case, the name of the campaign directory is
inserted, when the configuration file is loaded.

Some of the strings given to the other items, e.g. `year` and `session` are
Python format strings [more on this below]. The `date` reference
is an AutoBernese GPSDate which has the day-of-year property `doy` that can
be used inside the strings.

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
the task specification. In this case, the BPE will run for each of three days
that the EXAMPLE campaign stretches over.


### The `sources` section

Campaign-specific sources of external data can be specified in a `sources` section
in the campaign configuration.

The purpose of the configuration-specific sources section is that a given
campaign type may need, well, specific data for that campaign.

As illustrated in the EXAMPLE-campaign configuration file, a single FTP source
with two files needed for the built-in process-control file `ITRF.PCF` is
included so that the data can be downloaded to the DATAPOOL area to be used in
this (and in this case, other) campaigns.

```yaml
sources:

- !Source
  identifier: ITRF14
  description: IERS data needed for the EXAMPLE campaign
  url: https://datacenter.iers.org/products/reference-systems/terrestrial/itrf/itrf2014/
  filenames:
  - ITRF2014-IGS-TRF.SNX.gz  # 1.4 GB
  - ITRF2014-psd-gnss.dat  # 38 KB
  destination: !Path [*D, ITRF14]
```

Here, the YAML *anchor* `&campaign` is referred to with the syntax `*campaign`


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

<!--
AutoBernese is created with purpose of having reusable campaign settings (using
campaign templates) so that different campaign types are fast to create over and
over again, with any concrete campaign only being different in the ways encoded
by the `metadata` section above. Users may create the campaign configuration by
hand. But the premise of the workflow is that the campaign-specific
configuration is build using the AutoBernese campaign-creation command.
-->

<!--
The power of using campaign templates comes, when the campaign configuration for
a specific campaign type is determined with respect to the Bernese
user-environment and the PCF files used, as well as the sources of data that
must be downloaded and organised. A campaign template for that type of campaign
can then be created by copying the concrete campaign settings over to the
runtime directory's template directory without the `metadata` section and giving
it a meaningful filename.
-->

Based on the assumption that most users do the same things over and over again
to different data sets, and thus to avoid copying-and-pasting recurring
processing workflow between Bernese campaigns, AutoBernese has the concept of a
*campaign type* which is defined by a template campaign-configuration file in
the templates directory of the AutoBernese runtime directory.

Adding different templates for different campaign scenarios, i.e. campaign
types, will speed up the process of creating a new campaign, getting it ready by
downloading data, and running the BPE tasks set in the campaign-specific
configuration file.

With this template-management system, you only need to set up your Bernese
campaigns once, or rarely.

Campaign-configuration templates can be put in the AutoBernese runtime
directory:

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


<!--
### Difference between concrete configuration and its template

The difference between a campaign-configuration file and its template it the
metadata section that is part of the concrete Bernese campaign. AutoBernese adds
the metadata section automatically, but a user can also ad it manually, if the
configuration is made for an existing campaign such as the EXAMPLE campaign.

AutoBernese lets a user define configuration templates for common campaign
scenarios, where the only difference is in the time interval for which a given
campaign is created and run.

A default campaign template `default.yaml` is added to the `autobernese`
directory, automatically, when the command `ab campaign` is run. If the file
already exists, AutoBernese does nothing.

As the user creates a campaign with AutoBernese, if no other template name is
specified, the default campaign template is used. Therefore, this file should be
edited to suit the most common scenario. Even so, having more than one
configuration template will make common scenarios faster to setup.
-->


## Notes on Python-string templates in YAML documents

This section describes some caveats when using Python string template as values
in a YAML document.

Python has multiple ways to work with strings, and many of the string-values
given in the AutoBernese configuration files have content that requires soe
knowldge about Python's Template strings. In addition, the format of these
strings may clash with the YAML syntax, so a few potential problems and
solutions are shown below.


### Difference between Template strings and `f` string syntax

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
