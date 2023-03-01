
Documentation for our internal developers.

## Development environment for Python

We use MambaForge to create a development environment.

With the mamba command, you can create the needed tools by building an
environment from the environment-dev.yml file in the root of the Git archive.

### MambaForge

The [`mamba` official documentation][MAMBA-INSTALLATION] recommends installnig
MambaForge rather than installing the `mamba` program with `conda`.

On [GitHub][MAMBA-INSTALLER] the following command for Linux/Unix installs the
software:

[MAMBA-INSTALLATION]: https://mamba.readthedocs.io/en/latest/installation.html
[MAMBA-INSTALLER]: https://github.com/conda-forge/miniforge#mambaforge

```sh
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh
```


## Documentation

The documentation is built using MkDocs with the Material extension. The
lightbox feature is installed using PIP from the mamba environment.

### Visualise and Build the Diagrams

The architecture and overall functionality is viaualised using the C4-model tool
Structurizr.

A single [workspace][STRUCTURIZR-WORKSPACE-DSL] contains a collection of
software systems, the main system's container and their components.

[STRUCTURIZR-WORKSPACE-DSL]:
    https://github.com/sdfidk/autobernese/workspace/structurizr/workspace.dsl

The diagrams are produced using the docker container for [Structurizr
Lite][STRUCTURIZR-LITE], and the generated images are manually created from the
web application accessing the workspace file.

[STRUCTURIZR-LITE]: https://structurizr.com/help/lite

Command for running it in development:

```sh
docker run -d -it --rm -p 8080:8080 -v /path/to/git/AutoBernese/workspace/structurizr:/usr/local/structurizr structurizr/lite
```

For VS Code, there is a syntax extension called **Structurizr DSL syntax
highlighting** from publisher *ciarant* that is useful, when editing the
workspace file.

!!! note "Note"

    Running the docker container above for the first in a directory which does not
    already have a `workspace.dsl` file, a new file is created with root ownership.

    In this case, change the permissions on the `workspace.dsl` to give yourself
    write permissions for the file.

### Alternative diagramming tools:

*   [Ilograph](https://www.ilograph.com/) has an online viewer, which may be used for free.

    Structurizr diagram can be converted to this with the CLI tool.


## Data

*   [IGS switch to IGS20/igs20.atx and repro3 standards](https://igs.org/news/igs20/)
*   [IGS Site Log Manager User Guide](https://www.igs.org/site-log-manager-user-guide) | [Empty sitelog](https://files.igs.org/pub/station/general/blank.log)

*   [Standards and data formats](https://gssc.esa.int/education/library/standards-and-data-formats/)
*   [Research group of Astronomy and GEomatics. gAGE](https://gage.upc.edu/en)
