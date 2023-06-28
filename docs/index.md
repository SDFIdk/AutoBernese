
This is the documentation website for AutoBernese, a Command-line application
that automates and generalises common workflows with the [Bernese GNSS
Software](http://www.bernese.unibe.ch/) [*Bernese* or *BSW*].

AutoBernese is written i Python and the package is built and maintained by the
geodetic software developers at the [Danish Agency for Data Supply and
Infrastructure](https://eng.sdfi.dk/)

The software was created for our internal use, but as it may have some general
application, it is published for a larger audience with the hope that it may be
useful for other users of Bernese.

Please note that:

*   We do not offer any support other than what is already provided here and in
    the code comments and documentation strings.
*   All development assumes that AutoBernese runs in a Linux environment.
*   The package is still a work in progress as far as point 5. below is concerned.

However, if you want to reach out, feel free to open an issue on GitHub [see
link to the archive in the top-right corner of this website].


## Background

As geodesists that use the Bernese GNSS Software 5.4, we need a software system
that simplifies and eases the following processes:

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

If your would rather like to try out the software, go to the
[Quick-start](manual/quick-start.md) page or go to the [command-line
interface](manual/command-reference.md) page to read a complete walk-through of
the available commands.


## AutoBernese

AutoBernese does several things behind the scenes for you as it helps you create
campaigns in Bernese GNSS Software and automatically run the Bernese Processing
Engine for all the PCF files you need for a given campaign. It does so by
automating the otherwise manual workflow of selecting a campaign, session and
each individual PCF file to run.

The same AutoBernese installation can be used for different installations, since
it integrates, seamlessly, with the given loaded Bernese installation. This may
be, especially, useful, if you are a user or developer working in more than one
Bernese installation, e.g. one for either development, testing and production.

With its generalised workflow, AutoBernese is prepared, specifically, for a
multi-user scenario, giving users the ability to easily share ressources such as
a **common configuration** and **templates for generalised campaign workflow**.

Having templates for typical campaign scenarios minimises the time needed to set
up each campaign. And since the templates are stored as plain-text files in a
shared directory, they are usable by everyone and easy to maintain and keep a
history of, e.g. using a version control software.

<!-- Below is a more general view of the overall workflow of AutoBernese with some
key concepts introduced. -->

This is a conceptual view of the workflow that AutoBernese supports. The
following illustrates the order of tasks from the user perspective.

```kroki-bpmn
@from_file:assets/workflows.bpmn
```

Given that Bernese has been activated in the user terminal by `source`'ing
`LOADGPS.setvar`, the first thing that a user must consider is setting up the
local configuration of AutoBernese.

**Built-in and user-defined AutoBernese configuration**

This general configuration file lets you do the following:

1.  Specify what open GNSS-data sources your want to download.

    **Use case:** Download common data files, independently, from any campaign.

2.  Specify directory setup for campaigns that AutoBernese creates.

    **Use case:** Provide an option similar to the one in the Bernese GUI, where
    the campaign structure of a new campaign can be changed.

3.  Specify information used by AutoBernese to create a STA file from locally
    available station-sitelog files.

    **Use case:** A user needs to continuously build a STA file from updated
    sitelogs, so that it may be combined with STA files from other sources in a
    Bernese campaign.



**Template management for generic campaign types**

A campaign-configuration template lets you do the following:

1.  Create campaigns based on your own campaign types.

2.  Just as with general data sources, you may have campaign-specific data
    depend on the campaign template used. Specify these in the campaign-specific
    configuration file.

3.  Provided a list of one or more sets of input arguments to the Bernese
    Processing Engine [BPE], you may have a recipe for the given campaign type that
    can be easily run with a single command.


**The rest of the processes in the overall workflow diagram**

<!-- This section will not go into much detail about the processes following the
configuration of AutoBernese. -->

With the general settings configured in the general AutoBernese configuration
file, and at least one campaign-configuration template added to the templates
directory of the autobernese directory, you are able to either go download and
pre-process your general data or create a Bernese campaign.

!!! note "Parallel processes"

    While the diagram above shows that downloading general data and creating Bernese
    campaigns are processes that can be performed in parallel, the process of
    running the BPE for that campaign with AutoBernese does require that the
    campaign is created.

To read how to do all these things and more, go to the relevant section of the
manual to get started.
