!!! warning "TODO"

    *   How to add a campaign configuration (to an existing campaign)
    *   How to manage campaign-configuration templates for common campaign types.

## Download common and campaign-specific data

AutoBernese can download external data sources via FTP and HTTP which are
specified in either [`autobernese.yaml`](configuration-files.md) or any campaign
configuration `campaign.yaml` in a campaign directory. Basically, specified
sources lets you download one or more files from a remote path and put it in a
directory of your choice.

These examples demonstrate the use of the custom YAML tag `!Source` that
AutoBernese uses to define sources that users want to download,
before the campaign is run.

Sources are specified in the same way in both kinds of configuration, and
defining their parameters with some of the advanced syntax depends solely on the
context being either the common AutoBernese configuration or a given campaign
configuration.

## `Source` parameters

Source:

*   *`identifier`*
    -   A string without spaces that identifies the source and makes it possible
        to select specific sources to download only. source.
*   *`description`*
    -   A string that will be displayed in the terminal, when downloading the
        source.
*   *`url`*
    -   A string or Python `pathlib.Path` that defines the protocol, host and
        subdirectory to download from. Can contain the filename of a specific
        file or (FTP only) be a directory from which to download given files
        from.
*   *`destination`*
    -   A string or Python `pathlib.Path` with the path to a *directory* (not a
        filename) in which to put the downloaded file(s).
*   *`filenames`*
    -   A list of filenames to download from given remote directory. For FTP, a
        wildcard `*` may be used in the filename. To download all files in an
        FTP directory, use a single filename `*`.
*   *`parameters`*
    -   A mapping [Python `dict`] with keys being valid python variable names,
        and their corresponding values a sequence of possible values that the
        key will represent in a combination of all possible key-value pairs.
        (See the examples below.) The key will be resolved if used in the
        `Source` `url` and filenames.
*   *`max_age`*
    -   An integer limit in the unit of whole days which defines how long a
        given file should be stored locally, before needing an update. This is
        useful, if you run the command daily to update you sources. IN this
        case, set `max_age` to `1`, and the source will be force-downloaded if
        it is more than one day old. The default value is &infin;.


## Supported scenarios

Each example below demonstrates an internal use-case illustrating both a basic
approach as well as an advanced approach where the YAML syntax is used to avoid
repetition.


### FTP: Download specific file

In this example, a single file is specified in the full path to the remote
source. This is put into the given destination directory.

=== "Basic"

    ```yaml
    sources:

    - !Source
      identifier: EUREF_STA
      description: EUREF STA file
      url: ftp://epncb.oma.be/pub/station/general/EUREF.STA
      destination: /path/to/DATAPOOL/station
      max_age: 1
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      identifier: EUREF_STA
      description: EUREF STA file
      url: ftp://epncb.oma.be/pub/station/general/EUREF.STA
      destination: !Path [*D, station]
      max_age: 1
    ```


### FTP: Download all files directly under a given directory

Download all files (excluding directories) from a given directory on an FTP
server to a given destination directory.

In these two examples prefixed, the remote path is a directory, and filenames to
download are given with the wildcard `*`, which means that all files directly
under the remote path will be downloaded to the destination directory.


=== "Basic"

    ```yaml
    sources:

    - !Source
      identifier: BSW_MODEL
      description: BSW Model data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/MODEL/
      destination: /path/to/BERN54/GLOBAL/MODEL
      filenames: ['*']
      max_age: 1

    - !Source
      identifier: BSW_CONFIG
      description: BSW Configuration data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/CONFIG/
      destination: /path/to/BERN54/GLOBAL/CONFIG
      filenames: ['*']
      max_age: 1
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      identifier: BSW_MODEL
      description: BSW Model data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/MODEL/
      destination: *MODEL
      filenames: ['*']
      max_age: 1

    - !Source
      identifier: BSW_CONFIG
      description: BSW Configuration data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/CONFIG/
      destination: *CONFIG
      filenames: ['*']
      max_age: 1
    ```


### FTP: Download files with complete filenames given

Download specific files denoted with complete filenames from a given source
directory on an FTP server. This requires a list of the filenames in the
directory.

This example illustrates the same concept as the above one, but with filenames
either completely specified or, again, more generally using the `*` wildcard to
get all files with a given file extension.


=== "Basic"

    ```yaml
    sources:

    - !Source
      identifier: ANTENNA_FILES
      description: Universal and BSW-specific antenna files
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/REF/
      destination: /path/to/DATAPOOL/REF54
      filenames:
      - ANTENNA_I14.PCV
      - ANTENNA_I20.PCV
      - I14.ATX
      - I20.ATX
      max_age: 1
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      identifier: ANTENNA_FILES
      description: Universal and BSW-specific antenna files
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/REF/
      destination: !Path [*D, REF54]
      filenames:
      - ANTENNA_I14.PCV
      - ANTENNA_I20.PCV
      - I14.ATX
      - I20.ATX
      max_age: 1
    ```


### FTP: Download files from directory using `*` wildcard

Download specific files from an FTP server directory, where filenames are given
with a wildcard, e.g. `*.EPH.Z`.

=== "Basic"

    ```yaml
    sources:

    - !Source
      identifier: ION_BIA_2022
      description: Ionosphere and satellite-bias files
      url: ftp://ftp.aiub.unibe.ch/CODE/2022/
      destination: /path/to/DATAPOOL/CODE/2022
      filenames:
      - '*.ION.gz'
      - '*.ION.Z'
      - '*.BIA.gz'
      - '*.BIA.Z'

    - !Source
      identifier: ION_SAT_2023
      description: Ionosphere and satellite-bias files
      url: ftp://ftp.aiub.unibe.ch/CODE/2023/
      destination: /path/to/DATAPOOL/CODE/2023
      filenames:
      - '*.ION.gz'
      - '*.ION.Z'
      - '*.BIA.gz'
      - '*.BIA.Z'
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      identifier: ION_SAT
      description: Ionosphere and satellite-bias files
      url: ftp://ftp.aiub.unibe.ch/CODE/{year}/
      destination: !Path [*D, CODE, '{year}']
      filenames:
      - '*.ION.gz'
      - '*.ION.Z'
      - '*.BIA.gz'
      - '*.BIA.Z'
      parameters:
        year: [2022, 2023]
    ```


### HTTP: Download specific file URI

For HTTP sources, the remote path to the source must be fully specified, since
e.g. the wild card option is unavailable, since there is no inherent way to get
a directory listing from an HTTP URI.

=== "Basic"

    ```yaml
    sources:

    - !Source
      identifier: VMF3_1x1
      description: TU Wien Vienna Mapping Model 3
      url: https://vmf.geo.tuwien.ac.at/trop_products/GRID/1x1/VMF3/VMF3_OP/2023/
      filenames:
      - VMF3_20230101.H00
      - VMF3_20230101.H06
      - VMF3_20230101.H12
      - VMF3_20230101.H18
      # ... and so on for each day.
      destination: /path/to/DATAPOOL/VMF3/1x1_OP/2023
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      identifier: VMF3_1x1
      description: TU Wien Vienna Mapping Model 3
      url: https://vmf.geo.tuwien.ac.at/trop_products/GRID/1x1/VMF3/VMF3_OP/{date.year}/VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}
      destination: !Path [*D, VMF3, '1x1_OP', '{date.year}']
      parameters:
        date: !DateRange
          beg: 2023-01-01
          end: 2023-01-02
        hour: ['00', '06', '12', '18']
    ```


## Notes on advanced datatypes and parameters


### Custom YAML tags

A key difference between the simpler and the more advanced usage examples is
that the destination paths use another AutoBernese builtin construct which is a
YAML tags `!Path` and `!DateRange`. `!Path` combines a list of path segments to
a full Python `pathlib.Path` instance.

To deal with remote-path directory structures that depend on time, and in
general any other parameter, a `Source` instance can use Python's builtin string
templates as input for parameters that are expanded during runtime to produce
the needed combinations of URIs to download from.

The dates used with the `!DateRange` YAML tag are instances of a GPSDate, which
is a subclass of Python's `datetime.date` type. GPSDate adds a two useful
properties `gps_week` and `doy` to the instance which otherwise acts (and *is*)
in all other respects a Python `datetime.date` instance.

These two properties make it easier to build paths that require these date
properties, and this special data type was added to make them available in
template strings, since predefined template strings are not able to run
arbitrary functions inside them (for security reasons) as is possible with
Python's f-strings.


### YAML aliases

The `*D` is a YAML alias that is automatically available in the context that
reads the configuration file. This is what makes AutoBernese seamlessly
integrate into any loaded Bernese environment.

Essential environment variables set by `LOADGPS.setvar` are loaded and aliased
when the configuration file is loaded, and thus `*D` is YAML syntax that, when
loaded, replaces the `*D` with value that that the alias `D` refers to, which in
this case is the full path to the Bernese DATAPOOL directory as specified in
`LOADGPS.setvar`.

Thus, combining aliases such as `*D` and the custom `!Path` YAML tag, you may
specify paths that, when loaded, become the paths you already have available in
your environment, when you are running AutoBernese commands.
