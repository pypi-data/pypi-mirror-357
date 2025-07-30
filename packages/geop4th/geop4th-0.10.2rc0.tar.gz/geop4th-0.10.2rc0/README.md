# GEOP4TH
[![version](https://gitlab.com/AlexandreCoche/geop4th/-/badges/release.svg?version=latest)](https://gitlab.com/AlexandreCoche/geop4th)  [![Documentation](https://gitlab.com/AlexandreCoche/geop4th/badges/doc/pipeline.svg?key_text=📚+doc)](https://AlexandreCoche.gitlab.io/geop4th)

![preview](imgs/logo_v0.10.0a_smaller.png "Logo")

## Presentation
**GEOP4TH** /ʤiɒpɑːθ/ jee-uh-pa-th (for GEOspatial Python Pre-Processing Platform for Trajectories in Hydro-socio-ecosystems) is a collection of generic, 
format-agnostic, python tools (*geobricks*) designed to easily standardize, manipulate and visualize space-time data. 

Besides, these *geobricks* are designed to be assembled into complete pre-processing workflows for specific data or to specific models. 
Such workflows can be collaboratively developped and shared within GEOP4TH. 
So far, GEOP4TH includes the workflows for pre-processing some of the most common French datasets ([SIM2](https://www.data.gouv.fr/fr/datasets/donnees-changement-climatique-sim-quotidienne/), 
[DRIAS/EXPLORE2](https://www.drias-climat.fr), [BNPE](https://bnpe.eaufrance.fr), [IGN](https://geoservices.ign.fr/bdalti)...), as
well as the workflows to format inputs for [CWatM](https://cwatm.iiasa.ac.at). Collaborative developments are welcome :)

In the end, GEOP4TH intends to help working on hydro-socio-ecosystems trajectories and diagnostics. 

URL of the main source: https://gitlab.com/AlexandreCoche/geop4th

![abstract](imgs/illustration_globale_03short.png "Abstract"){width=750}

## Documentation
The most up-to-date documentation can be found online at:
- 📗 Documentation : https://AlexandreCoche.gitlab.io/geop4th

> **Note**
> Additionnaly, this documentation can be accessed offline through the *public/index.html* [file](public/index.html) on the *doc* branch 

## Getting started

> **Note**  
> Latest quickstart instructions are described in the [Documentation](https://AlexandreCoche.gitlab.io/geop4th) with more details.

### Installation requirements
To install the python environment required to use this module, it is necessary to install an Anaconda distribution (such as [Miniconda3](https://docs.anaconda.com/miniconda/install/)).

> **Tip**  
> For a start, we also advise using a Git Management tool (such as [GitHub Desktop](https://desktop.github.com/download)).

#### Retrieve this remote git folder to a local machine
To clone this git folder using for example GitHub Desktop, you can:
1. Go to `File` > `Clone repository...` 
2. Got to `URL` tab and enter https://gitlab.com/AlexandreCoche/geop4th.git
	- the `local path` should end with *geop4th*

#### Python environment
GEOP4TH requires some common open-source python packages (xarray, rioxarray, rasterio, numpy, pandas, geopandas, shapely, fiona, pysheds, plotly, matplotlib).

Installing the python environment can be done in the conda console (admin mode advised) by entering:
```bash
# If geop4th has been cloned to another disk than C:, it is necessary to enter the name of the disk first
# d: (for example)
cd "path/to/geop4th/install"
conda env create -f environment.yml -n geoenv

```

### Set up
1. Open conda prompt and activate environment:
```bash
conda activate geoenv
```

2. Install and open an IDE such as Spyder or Jupyter Notebook:
```bash
conda install spyder -c conda-forge

spyder
```

3. Once in the IDE, the parent folder (the root folder containing *geop4th* folder) should be added to the `PYTHONPATH`

4. Then, the main modules can be imported as follow:
```python
# Basics elements
from geop4th import (
    geobricks as geo,
    download_fr as dl,
    trajplot as tjp,
    )
	
# or complete workflows
from geop4th import (
    standardize_fr as stz,
    cwatm,
    )
```

### Docker image
A Docker image of 0.10.1 version is available here: https://hub.docker.com/r/alexandrecoche/geop4th.

## Support
alexandre.co@hotmail.fr

## Project status
Currently under developpement.

## Roadmap
- [ ] generalize data paths in *trajplot* and document it
- [ ] document all the functions
- [ ] implement logging everywhere and add a workflow log
- [ ] implement a comparison function
- [ ] for contributing, test and resolve the installation procedure with pip
- [ ] clean code (functions in *geohydroconvert* `#%% EXTRACTIONS`, *georef* in double, clean comments, restructure *SIM2_tools* and *advanced_visualization* into *geohydroconvert*...)

## Authorship & contributions

### Contribute
See the [CONTRIBUTING.md](CONTRIBUTING.md) file

### Authors and acknowledgment
This work has been created by Alexandre Kenshilik Coche, with the help of the following first contributors:
The design of the *trajplot* figures was conceived with the help of **Laurent Longuevergne**, **Elias Ganivet** and **Veronique Van Tilbeurgh**.  
Part of the functions to handle SIM2 data were conceived with the help of **Ronan Abhervé** and some code parts from **Loïc Duffar**'s [scripts](https://github.com/loicduffar).  
Packing functions were based on **James Hiebert**'s [work](http://james.hiebert.name/blog/work/2015/04/18/NetCDF-Scale-Factors.html).
**Alexandre Gauvain** shared insightful ideas on how to structure the gitlab and the ReadTheDocs documentation.
**Bastien Boivin** and **Pape Saara Ngom** provided helpful advice to improve the installation procedure.
**Damien Belvèze** and **Martin Komlavi Amouzou** brought a significant help and crucial advice on software development good practices, replicability, testing and containerization.
Programmer web communities brought a considerable help to this work.

To see a more detailled and up-to-date view on authors and contributors, please refer to the [codemeta.json](codemeta.json) file.

### Funding
This work has been partly funded by [PAGAIE ANR research project](https://eau-et-territoire.org/le-projet-pagaie/) (EOTP776392) and the "Ressources en Eau du futur" Rennes Métropole Chaire (19JA305-01D).

## License
GNU GPLv3
see the [COPYING](COPYING) file.

***