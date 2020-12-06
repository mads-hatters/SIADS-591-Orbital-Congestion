Import Environment
---
Importing the conda environment.

`conda env create -f env/conda/environment.yml`

Activate Environment
---
`conda activate siads-orbital`

Export Current Environment
---
Export your environment whenever you installed new packages.

`conda env export --name siads-orbital > env/conda/environment.yml`


Create Environment From Scratch
---
This shouldn't need to be done, but is documented in case it is needed.

`conda create --prefix ./env jupyterlab matplotlib numpy pandas line_profiler markdown notebook python scipy scikit-learn`
