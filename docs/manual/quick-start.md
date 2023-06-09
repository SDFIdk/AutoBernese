The purpose of this section is to give a quick demonstration of how to use
AutoBernese to run PCF-files with the Bernese Processing Engine for a campaign.

To get a feel for how AutoBernese works, when everything is set up, this section
goes through running the PPP-script with the Bernese Processing Engine for the
EXAMPLE campaign that comes bundled with the Bernese GNSS Software.


## Preparation

Before proceeding, make sure that you have performed the following steps:

*   [Install AutoBernese](installation.md).
*   Install the Bernese EXAMPLE campaign [see Bernese manual].
*   Download [this campaign configuration](assets/campaign.yaml) to the EXAMPLE-campaign directory [`$P/EXAMPLE`].

What you have now is a configuration file that lets you run the PPP.PCF file for
the first two days available in the EXAMPLE campaign's interval.


## Initialise environments

First, initialise the environments:

*   Load your Bernese environment as defined in `LOADGPS.setvar`.
*   Activate the AutoBernese `conda`/`mamba` environment [`ab`]


## Run the campaign

To run the PCF file for each speficied day, type the following in the terminal
with the activated environments:

```sh
(ab) $ ab campaign run EXAMPLE

```


## Recorded example

Below is a demonstration of the process above:

<div id="demo"></div>

<script src="/javascript/asciinema-player.min.js"></script>
<script>
    let filename = '/assets/asciicasts/quick-start_run.cast';
    let element_id = 'demo';
    let options = {
        speed: 2,
        idleTimeLimit: 2,
    };
    AsciinemaPlayer.create(filename, document.getElementById(element_id), options);
</script>
