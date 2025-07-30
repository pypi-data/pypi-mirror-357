# Insolation


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15682056.svg)](https://doi.org/10.5281/zenodo.15682056)

This software consists of three Python libraries:

* astro.py: an interface (or computational module) providing various astronomical solutions (Berger 1978, Laskar 2004, ...) to deliver parameters needed for insolation: eccentricity, obliquity, and climatic precession. The reference solution is Laskar 2004.
* inso.py (depends on astro.py): computes different types of insolation—instantaneous, daily averaged, or other averaged insolation—as well as "caloric seasons", useful for paleoclimatic and long-term climate studies.
* minmax_inso.py (depends on astro.py and inso.py): computes extremal values of daily insolation.

Some usage examples are also provided.  
figures.py generates several figures (for a paper to be submitted soon).
```
import inso
inso.figure.display("1")
```
