
This is the documentation website for AutoBernese, a Command-line application
that automates and generalises common workflows when working with the Bernese
GNSS Software [*Bernese* or *BSW*].

This package is built and maintained by the Geodetic IT team at the [Danish
Agency for Data Supply and Infrastructure](https://eng.sdfi.dk/)

The package is mainly built for our internal use, but as the tool may have some
general application, it is published with the hope that it may be useful for
other users of Bernese.

The package is still a work in progress as far as point 5. below is concerned.
Note also, for instance, that all development assumes that AutoBernese runs in a
Linux environment.

If you want to reach out, feel free to open an issue on GitHub [see link to the
archive in the top-right corner of this website].

Note, however, that we do not offer any support other than what is already
provided here and in the code comments and documentation strings.


## Background

As geodesists that use the [Bernese GNSS Software](http://www.bernese.unibe.ch/)
5.4, we need a software system that simplifies and eases the following
processes:

1.  Create Bernese campaigns for different campaign types.
2.  Download necessary external data, either for common or campaign-specific
    purposes.
3.  Produce or preprocess local data products for use in Bernese campaigns.
4.  Simplify setting up recipes and starting the Bernese Processing Engine [BPE]
    for a given campaign.
5.  Assures the quality of and handles the end products that come out of the BPE
    process.

Below the introduction is a more detailed overview of what is possible with the
software.


## AutoBernese

With AutoBernese installed, you have a new command `ab` available, which does
several things behind the scenes for you as it helps you create campaigns in
Bernese GNSS Software and automatically run the Bernese Processing Engine for
all the PCF files you need for a given campaign. It does so by automating the
otherwise manual workflow of selecting a campaign, session and each individual
PCF file to run.

The same AutoBernese installation can be used for different installations, since
it integrates, seamlessly, with the given loaded Bernese installation. This may
be, especially, useful, if you are a user or developer working in more than one
Bernese installation, e.g. one for either development, testing and production.

<!--
``` title="asd" linenums="1" hl_lines="1"
--8<-- "docs/assets/bsw_env_dir_tree"
```
-->

``` title="AutoBernese runtime directory is in the parent directory of `$C`"
/path/to/environment
├── autobernese     # AutoBernese runtime directory automatically
│                   # created one level up from Bernese-installation directory
│
├── BERN54          # Bernese 5.4 installation directory, a.k.a. `$C`
└── ...
```

With its generalised workflow, AutoBernese is prepared, specifically, for a
multi-user scenario, giving users the ability to easily share ressources such as
a common configuration and templates for generalised campaign workflow.

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

<!-- === "`ab/configuration/env.yaml`"

    ```yaml title="BSW environment loaded with each configuration" linenums="1" hl_lines="1"
    --8<-- "src/ab/configuration/env.yaml::24"
    ``` -->

AutoBernese lets users of a given Bernese installation share a common
configuration file [see `autobernese.yaml` below], where, for instance, you can
maintain a list of common data sources to download.

Campaign-specific sources and, especially, PCF files to run with BPE, are
managed from a campaign-specific configuration file in the root of the Bernese
campaign directory.

Based on the assumption that most users do the same things over and over again
to different data sets, and thus to avoid copying-and-pasting recurring
processing workflow between Bernese campaigns, AutoBernese has the concept of a
*campaign type* which is defined by a template campaign-configuration file in
the templates directory of the AutoBernese runtime directory [see `example.yaml`
below].


=== "`autobernese/autobernese.yaml`"

    ```yaml title="Configuration overrides"
    --8<-- "docs/manual/assets/autobernese.yaml:6"
    ```

=== "`autobernese/templates/example.yaml`"

    ```yaml title="Configuration used for the EXAMPLE campaign"
    --8<-- "docs/manual/assets/campaign.yaml:10:"
    ```

<!--
Having templates for typical campaign scenarios minimises the time needed to set
up each campaign. And since the templates are stored as plain-text files in a
shared directory, they are usable by everyone and easy to maintain and keep a
history of, e.g. using a version control software.
-->

Below is a more general view of the overall workflow of AutoBernese with some
key concepts introduced as well.

If your would rather like to try out the software, go to the
[Quick-start](manual/quick-start.md) page or go to the [command-line
interface](manual/commands.md) page to read a complete walk-through of the
different commands so far available.


## Overall workflow so far

This is a conceptual view of the workflow that AutoBernese supports. The
following illustrates the order of tasks from the user perspective.

```kroki-bpmn
@from_file:assets/workflows.bpmn
```

Below is an overview of the concepts.


### Configure AutoBernese

Given that Bernese has been activated in the user terminal by `source`'ing
`LOADGPS.setvar`, the first thing that a user must consider is setting up the
local configuration of AutoBernese.

**Built-in and user-defined AutoBernese configuration**

When AutoBernese is run for the first time, by simply running `ab`in the
terminal, it create a directory `autobernese` at the same level as the
Bernese-installation directory [`BERN54` if using the default name]. In this
directory, a configuration file `autobernese.yaml` common to all users will
override the built-in configuration that comes with the package.

In short, the user-defined configuration file that AutoBernese can read must be
located at the following path [using the set Bernese environment variables]:
`$C/../autobernese/autobernese.yaml`.

This general configuration file lets you do the following:

*   Specify what open GNSS-data sources your want to download.

    Use case: Download common data files, independently, from any campaign.

*   Specify directory setup for campaigns that AutoBernese creates.

    Use case: Provide an option similar to the one in the Bernese GUI, where the
    campaign structure of a new campaign can be changed.

*   Specify information used by AutoBernese to create a STA file from locally
    available station-sitelog files.

    Use case: A user needs to continuously build a STA file from updated
    sitelogs, so that it may be combined with STA files from other sources in a
    Bernese campaign.


**Template management for generic campaign types**

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

To sum it up, a campaign-configuration template lets you do the following:

*   Create campaigns based on your own campaign types.

*   Just as with general data sources, you may have campaign-specific data
    depend on the campaign template used. Specify these in the campaign-specific
    configuration file.

*   Provided a list of one or more sets of input arguments to the Bernese
    Processing Engine [BPE], you may have a recipe for the given campaign type that
    can be easily run with a single command.


### The rest of the processes in the overall workflow diagram

this section will not go into much detail about the processes following the configuration of AutoBernese.

With the general settings configured in the general AutoBernese configuration
file, and at least one campaign-configuration template added to the templates
directory of the autobernese directory, you are able to either go download and
pre-process your general data or create a Bernese campaign.

While the workflow diagram above shows that downloading general data and
creating Bernese campaigns are processes that can be performed in parallel, the
process of running the BPE for that campaign with AutoBernese does require that
the campaign is created.

To read how to do all these things and more, go to the relevant section of the
manual to get started.
