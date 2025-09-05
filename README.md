# [GNSS-Process Automation with Bernese GNSS Software](https://github.com/SDFIdk/AutoBernese)

## The package

AutoBernese is written i Python and the package is maintained by the [Danish
Agency for Climate Data](https://eng.kds.dk/)

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


## Use-case scenarios

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

With its generalised workflow, AutoBernese is prepared, specifically, for a
multi-user scenario, giving users the ability to easily share ressources such as
a common configuration and templates for generalised campaign workflow.

For example, AutoBernese also lets you maintain a list of common data sources
to download in a common configuration file, whereas campaign-specific sources
and, especially, PCF files to run with BPE, are managed from a campaign-specific
configuration file.

Another key assumption is that most users do the same things over and over again
to different data sets. To address this, AutoBernese has a concept of a
*campaign type*, which is a way to configure a re-usable processing workflow.

Having templates for typical campaign scenarios minimises the time needed to set
up each campaign. And since the templates are stored as plain-text files in a
shared directory, they are usable by everyone and easy to maintain and keep a
history of, e.g. using a version control software.

The same AutoBernese installation can be used for different installations, since
it integrates, seamlessly, with the given loaded Bernese installation. This may
be, especially, useful, if you are a user or developer working in more than one
Bernese installation, e.g. one for either development, testing and production.
