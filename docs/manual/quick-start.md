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

!!! note "Bernese user environment"

    Make sure that you have configured a Bernese user environment
    for the active user. Run

    ```
    $EXE/configure.pm
    ```

    and select option 3.
    AutoBernese will fail without a functional Bernese user environment.

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

??? info "Expand to see the AutoBernese campaign-configuration file for the EXAMPLE campaign"

    ``` title="`campaign.yaml`" linenums="1"
    --8<-- "docs/manual/assets/campaign.yaml"
    ```

The three standard sections in this file are `metadata`, which contain data
about the campaign, `tasks` which contain a list of tasks to run for the
campaign, and `sources`, which contain a list of data sources.

!!! warning "IMPORTANT"

    For the EXAMPLE campaign, the provided data cover several two-day intervals
    instead of having a single interval, that can be defined by the beginning and
    end dates in the `metadata`section. AutoBernese only supports creating campaigns
    with a single date interval, but the campaign configuration can easily be
    amended to accommodate the case, where several arbitrary dates are used.

    In this case, a custom section, arbitrarily named `custom`, has been added, in
    which a YAML anchor `&dates` is defined for the sequence of dates that all
    `.PCF` files, except `LEOPOD.PCF`, use in the EXAMPLE campaign.

    This section is not 'seen' by AutoBernese, since it does not use this key, when
    loading the configuration. But the configuration settings that use the YAML
    alias `*dates` do have its values inserted, before being read by AutoBernese.

See a short description of each section below or an expanded description in the
section on [campaign-specific configuration files][AB-C-CONFIG]:

[AB-C-CONFIG]: configuration-files.md#campaign-configuration

*   The `metadata` section contains data about the context in which the campaign
    was created, if it was created by AutoBernese. With YAML anchors
    [`&<anchor>`], information such as the campaign directory [here,  `EXAMPLE`]
    and the date interval [`beg` and `end`] covered by the campaign can be
    re-used later in the document

    Here, the beginning and end dates define an interval in which there are data
    for the `LEOPOD.PCF` file in the EXAMPLE campaign.

*   The `custom` section, as explained above is not a part of AutoBernese, but a
    useful construct, that works as a container for manually-set-up data.

*   The `tasks` section contains short definitions of each BPE process to run,
    and in which the details depend on the input dates that the `.PCF` file
    should run for.

*   The `sources` section define external or otherwise remote data sources
    needed for the campaign. The EXAMPLE campaign does not come with all needed
    data by default, and the missing source is defined as a single entry here.

To learn more about how to configure campaigns, go to [Configuration files]. To
learn how to use AutoBernese to create Bernese campaigns based on templates, go
[Command-line reference].

[Configuration files]: configuration-files.md
[Command-line reference]: command-reference.md
