
This is the documentation for our internal developers.

Note, again, that we, currently, only work on this project for the purpose of
reaching our own internal goals.


## Development environment for Python

We use [MambaForge] to create a development environment. To build the `mamba`
environment `ab-dev` for development, go to your local Git archive with the
repository and type:

[MambaForge]: ../prerequisites.md

```sh
(base) $ mamba env create -f environment-dev.yml
```

Then, activate the environment by typing:

```sh
(base) $ mamba activate ab-dev
(ab-dev) $
```

Finally, install AutoBernese in developer mode, so that you can run the
application using the current revision state of the archive:

```sh
(ab-dev) $ python -m pip install -e .
```

### Contribution guidelines

Code changes must be made from any branch on your own fork of the official
repository and submitted as a GitHub pull request.

Make sure that contributed code passes the checks made on GitHub, before
requesting a review.

We aim for type consistency, but for now, type checking is not enforced.


## Documentation

The documentation is built using MkDocs with the Material extension. Other
features are used as well. (See which ones in `environment-dev.yml`.)


### Illustration Business-Process Modelling and Notation [BPMN]

To illustrate the business-process model, the BPMN XML-format is used.

The `.bpmn` files are edited using the Javascript-based application from
[bpmn.io](https://bpmn.io/) which can be added as [an extension to VS
Code][VSC-EXT-BPMN].

[VSC-EXT-BPMN]: https://marketplace.visualstudio.com/items?itemName=bpmn-io.vs-code-bpmn-io

The files are visualised using [kroki](https://kroki.io/) in an MkDocs
extension.


### Shell recording for examples

Examples are recoreded using [asciinema](https://asciinema.org/) and `.cast`
files are included in the documentation by adding extra CSS and JavaScript for
the visualiser and adding HTML `script` elements in the Markdown source
documents.


### System Diagrams

The architecture and overall functionality is viaualised using the C4-model tool
Structurizr.

A single [workspace][STRUCTURIZR-WORKSPACE-DSL] contains a collection of
software systems, the main system's container and their components.

[STRUCTURIZR-WORKSPACE-DSL]:
    https://github.com/sdfidk/autobernese/blob/main/workspace/structurizr/workspace.dsl

The diagrams are produced using the docker container for [Structurizr
Lite][STRUCTURIZR-LITE], and the generated images are manually created from the
web application accessing the workspace file.

[STRUCTURIZR-LITE]: https://structurizr.com/help/lite

Command for running it in development:

```sh
docker run -d -it --rm -p 8080:8080 -v /path/to/git/AutoBernese/workspace/structurizr:/usr/local/structurizr structurizr/lite
```

For VS Code, there is a syntax extension called [**Structurizr DSL syntax
highlighting**][VSC-EXT-STRUCTURIZR] from publisher *ciarant* that is useful,
when editing the workspace file.

[VSC-EXT-STRUCTURIZR]: https://marketplace.visualstudio.com/items?itemName=ciarant.vscode-structurizr

!!! note "Note"

    Running the docker container above for the first in a directory which does not
    already have a `workspace.dsl` file, a new file is created with root ownership.

    In this case, change the permissions on the `workspace.dsl` to give yourself
    write permissions for the file.
