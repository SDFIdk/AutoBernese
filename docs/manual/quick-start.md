The purpose of this section is to give a quick demonstration of how to use
AutoBernese to run PCF-files with the Bernese Processing Engine for a campaign.

To get a feel for how AutoBernese works, when everything is set up, this section
goes through running the PPP-script with the Bernese Processing Engine for the
EXAMPLE campaign that comes bundled with the Bernese GNSS Software.


## Preparation

Before proceeding, make sure that you have performed the following steps:

*   [Install AutoBernese](install-autobernese.md).
*   Install the Bernese EXAMPLE campaign [see Bernese manual].
*   Download [this campaign configuration](assets/campaign.yaml) to the
    EXAMPLE-campaign directory [`$P/EXAMPLE`].

What you have now is a configuration file that lets you run the default PPP.PCF
file for the first two days available in the EXAMPLE campaign's interval.


### Initialise environments

First, initialise the environments:

*   Load your Bernese environment as defined in `LOADGPS.setvar`.
*   Activate the AutoBernese `conda`/`mamba` environment [`ab`]


## Run the campaign

To run the PCF file for each specified day, type the following in the terminal
with the activated environments:

```sh
(ab) $ ab campaign run EXAMPLE
# (output) from BPE
```


### Recorded example

Below is a demonstration of the process above:

<div id="demo"></div>

<script>
window.onload = () => {
    let filename = '../assets/quick-start_run.cast';
    let element_id = 'demo';
    let options = {
        speed: 2,
        idleTimeLimit: 2,
    };
    AsciinemaPlayer.create(filename, document.getElementById(element_id), options);
}
</script>


## The configuration for the EXAMPLE campaign

The file that you downloaded to the EXAMPLE-campaign directory above is an
example of a campaign-configuration file that AutoBernese uses to download
campaign-specific data and configure and run the Bernese Processing Engine.

The three sections in this file are `metadata`, which contain data about the
campaign, `tasks` which contain a list of tasks to run for the campaign, and
`sources`, which contain a list of data sources.

See a short description of each section in the tabs below:

!!! info "AutoBernese campaign-configuration file for the EXAMPLE campaign"

    === "Raw"

        ``` title="`campaign.yaml`" linenums="1"
        --8<-- "docs/manual/assets/campaign.yaml"
        ```

        The campaign-specific configuration is an additional file that AutoBernese uses
        to manage data and run tasks related to a specific Bernese campaign.

    === "`metadata`"

        ``` title="`campaign.yaml`" linenums="1" hl_lines="1-8"
        --8<-- "docs/manual/assets/campaign.yaml"
        ```

        The `metadata` section contains data about the contet in which the campaign was
        created, if it was created by AutoBernese. With YAML anchors [`&<anchor>`],
        information such as the campaign directory [here,  `EXAMPLE`] and the date
        interval [`beg` and `end`] covered by the campaign can be re-used later in the
        document

        Here, the beginning and end dates define an interval in which there are data in
        the EXAMPLE campaign.

    === "`tasks`"

        ``` title="`campaign.yaml`" linenums="1" hl_lines="10-23"
        --8<-- "docs/manual/assets/campaign.yaml"
        ```

        A single task is specified to use the `PPP.PCF` file included in the BSW user
        scripts. As specified here, the task has a name [`name`] used to display what is
        going on, some arguments [`arguments`] which are sent to the Bernese Processing
        Engine. `arguments` contain a dictionary with items having a string to be used
        with the BSW BPE program.

    === "`sources`"

        ``` title="`campaign.yaml`" linenums="1" hl_lines="25"
        --8<-- "docs/manual/assets/campaign.yaml"
        ```

        External or otherwise remote data sources needed for the campaign can be
        specified here, but as the EXAMPLE campaign comes with the data included, the
        list is empty.


To learn more about how to configure campaigns, go to [Configuration files]. To
learn how to use AutoBernese to create Bernese campaigns based on templates, go
[Command-line reference].

[Configuration files]: configuration-files.md
[Command-line reference]: command-reference.md
