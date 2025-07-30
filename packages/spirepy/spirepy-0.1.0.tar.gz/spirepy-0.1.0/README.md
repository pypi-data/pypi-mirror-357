# SPIREpy

<!--toc:start-->
- [SPIREpy](#spirepy)
  - [Usage](#usage)
  - [Documentation](#documentation)
  - [Installation](#installation)
  - [Credits](#credits)
<!--toc:end-->

SPIREpy is a Python package and command-line tool that allows users to interact
with the [SPIRE](https://spire.embl.de/) database in a more convinient way.

## Usage


### Python package

The Python package encapsulates the study and samples types from SPIRE into
classes with properties that allow you to access and interact with their data.
To load a study, we do:

```{python}
from spirepy import Study

study = Study("Lloyd-Price_2019_HMP2IBD")
```

We can then obtain the list of samples that belong to this study.

```{python}
study.get_samples()  
```

The study's metadata:

```{python}
study.get_metadata()
```

Or even the assembled genomes:

```{python}
study.get_mags()
```

Likewise, many of these attributes and operations are parallel to samples
(`Sample` class) as well. For the full documentation and how to interact with
them, see [here](#documentation)

### Command-line tool

The command-line interface tool allows the interaction with data from SPIRE directly in the terminal. It possesses 2 main interfaces:

- `view`
- `download`

These 2 sub-commands allows us to print tables and download data from both studies and samples. For more information on the available commands use:

```{bash}
spire --help
```

 To view a study's metadata we can use:

```{bash}
spire --study view metadata Lloyd-Price_2019_HMP2IBD
```

And to download the same table as a `.csv` file we can instead:

```{bash}
spire --study download metadata Lloyd-Price_2019_HMP2IBD -o study/
``` 

## Installation

TODO: need to add to PyPI and conda first

## Documentation

TODO: need readthedocs

## Credits
