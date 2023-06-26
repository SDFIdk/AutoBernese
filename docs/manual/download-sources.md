## Download common and campaign-specific data

AutoBernese can download external data sources specified in the [common
configuration file]() or in any campaign configuration [i.e. `campaign.yaml` in
a campaign directory].

!!! warning "TODO: Add links to section of the documentation where the configuration files are explained"

    *   The configuration format.
    *   The configuration locations.
        *   User directory. (common concept) -- autobernese.yaml.
            *   Should the user also be able to have local configuration?
        *   The campaign directory root. -- campaign.yaml.

    *   How to add a campaign configuration (to an existing campaign)
    *   How to manage campaign-configuration templates for common campaign types.

As examples, AutoBernese comes with a preset list of sources to download from:


This approach illustrates the use of the builtin `Source` instance which is also
available as a YAML tag `!Source`. This lets you download one or more files from
a remote path and put it in a directory of your choice.

The `max_age` directive is in the unit of whole days and can be used to limit
how long a given file should be stored locally, before needing an update. This
is useful, if you run the command daily to update you sources. IN this case, set
`max_age` to `1`, and the source will be force-downloaded if it is more than one
day old. The default value is &infin;.

!!! warning ""

    To deal with remote-path directory structures that depend on time, and in
    general any other parameter, a `Source` instance can use Python's builtin string
    templates as input for paramaters that are expanded during runtime to produce
    the needed combinations of URIs to download from.




=== "`autobernese.yaml`"

    ```yaml
    sources:

    - !Source
      name: EUREF STA file
      url: ftp://epncb.oma.be/pub/station/general/EUREF.STA
      destination: /path/to/DATAPOOL/station
      max_age: 1
    ```

=== "`campaign.yaml`"

    TODO

## Supported scenarios

### FTP: Download specific file

In this example, a single file is specified in the full path to the remote
source. This is put into the given destination directory.

=== "Basic"

    ```yaml
    sources:

    - !Source
      name: EUREF STA file
      url: ftp://epncb.oma.be/pub/station/general/EUREF.STA
      destination: /path/to/DATAPOOL/station
      max_age: 1
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      name: EUREF STA file
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
      name: BSW Model data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/MODEL/
      destination: /path/to/BERN54/GLOBAL/MODEL
      filenames: ['*']
      max_age: 1

    - !Source
      name: BSW Configuration data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/CONFIG/
      destination: /path/to/BERN54/GLOBAL/CONFIG
      filenames: ['*']
      max_age: 1
    ```

=== "Advanced"

    ```yaml
    sources:

    - !Source
      name: BSW Model data
      url: ftp://ftp.aiub.unibe.ch/BSWUSER54/MODEL/
      destination: *MODEL
      filenames: ['*']
      max_age: 1

    - !Source
      name: BSW Configuration data
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
      name: Universal and BSW-specific antenna files
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
      name: Universal and BSW-specific antenna files
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
      name: Ionosphere and satellite-bias files
      url: ftp://ftp.aiub.unibe.ch/CODE/2022/
      destination: /path/to/DATAPOOL/CODE/2022
      filenames:
      - '*.ION.gz'
      - '*.ION.Z'
      - '*.BIA.gz'
      - '*.BIA.Z'

    - !Source
      name: Ionosphere and satellite-bias files
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
      name: Ionosphere and satellite-bias files
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
      name: TU Wien Vienna Mapping Model 3
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
      name: TU Wien Vienna Mapping Model 3
      url: https://vmf.geo.tuwien.ac.at/trop_products/GRID/1x1/VMF3/VMF3_OP/{date.year}/VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}
      destination: !Path [*D, VMF3, '1x1_OP', '{date.year}']
      parameters:
        date: !DateRange
          beg: 2023-01-01
          end: 2023-01-02
        hour: ['00', '06', '12', '18']
    ```

### Advanced examples

Using Python template strings and AutoBernese parameterisation, you can also
specifiy sources in the following way:

!!! note "Note"

    Another key difference between the simpler and the more advanced usage examples
    is that the destination paths use another AutoBernese builtin construct which is
    a YAML tags `!Path` and `!DateRange`. `!Path` combines a list of path segments
    to a full Python `pathlib.Path` instance.

    The dates used with the `!DateRange` YAML tag are instances of a GPSDate, which
    is a subclass of Python's `datetime.date` type. GPSDate adds a two useful
    properties `gps_week` and `doy` to the instance which otherwise acts (and *is*)
    in all other respects a Python `datetime.date` instance.

    These two properties make it easier to build paths that require these date
    properties, and this special data type was added to make them available in
    template strings, since predefined template strings are not able to run
    arbitrary functions inside them (for security reasons) as is possible with
    Python's f-strings.

    The `*D` is a YAML alias that is automatically available in the context that
    reads the configuration file. This is what makes AutoBernese seamlessly
    integrate into any loaded Bernese installation [henceforth referred to as a
    Bernese *environment*]. Essential environment variables set by `LOADGPS.setvar`
    are loaded and aliased when the configuration file is loaded, and thus `*D` is
    YAML syntax that, when loaded, replaces the `*D` with value that that the alias
    `D` refers to, which in this case is the full path to the Bernese DATAPOOL
    directory as specified in `LOADGPS.setvar`. Thus, with aliases and the `!Path`
    YAML tag, you may specify paths that, when loaded, become the paths you already
    have available in your environment, when you are running AutoBernese commands.
