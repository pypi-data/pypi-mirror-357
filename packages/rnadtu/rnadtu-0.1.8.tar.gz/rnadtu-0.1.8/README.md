# rnadtu

A Python package for running the CIDR algorithm (originally implemented in R) for clustering single-cell RNA-seq data using `AnnData` objects.

## Features

- Run the CIDR algorithm from Python using:

  - **`cidr()`** — subprocess-based, using temporary CSV files (recommended for large datasets)
  - **`cidr_non_csv()`** — subprocess-based, using in-memory buffers (faster but memory intensive and difficult to debug)
  - **`cidr_rpy2()`** — uses the `rpy2` bridge (direct R integration, less suitable for large datasets)

- Optional configuration options:

  - `data_type`: default is `"raw"`, can be `"cpm"` (counts per million)
  - `n_cluster`: default is `None` (CIDR calculates the optimal number), or manually specify an positive integer
  - `layer`: which layer of the `AnnData` object to use for input
  - Optional output controls:
    - `pc`: store principal coordinates
    - `dissim`: store dissimilarity matrix
    - `dropout`: store dropout matrix
    - `save_clusters`: (only in cidr_rpy2) choose store cluster labels (default `True`)

- Results are saved in the `AnnData` object:

  - `obsm[layer + "_cidr_pc"]` — principal components
  - `obsm[layer + "_cidr_clusters"]` — cluster labels (if `save_clusters=True`)
  - `obsp[layer + "_cidr_dissimilarity_matrix"]` — pairwise distances
  - `uns[layer + "_cidr_variation"]`, `uns[layer + "_cidr_eigenvalues"]` — PCA variation
  - `uns[layer + "_cidr_dropout_candidates"]` — dropout data

- Generates a clustering plot in `cidr_plots.pdf`

## Installation
Important: Before installing the package via `pip install rnadtu`, please follow the installation prerequisites below
### Install R and CIDR

To get the package up and running you first need to install R and the CIDR library:

- Install R ≥ 4.4.0 with default settings
- On windows, make sure R is added to **PATH**, typically as  
  `C:\Program Files\R\R-<your-version>\bin`
- Install Corresponding version of RTools
- Open an R console in a terminal or in Rstudio and run the following command:  
  `install.packages("devtools")` (this may take a little)
- install CIDR with the following command:  
  `devtools::install_github('VCCRI/CIDR')`
- **OPTIONAL if you want to run individual functions of the CIDR algorithm:**
  - install the Arrow with the following command:  
    `install.packages('arrow')`
  - install the qs package with the following command:  
    `install.packages('qs')`

---

### Install rpy2

To install rpy2, which is a package that some of the functions in our package depends on, simply use the command `pip install rpy2`. However, if you are on windows, do the following:  
The R-version in the steps is 4.4.0, but should be replaced with your respective version, this should be replaced with the R-version on your pc.

- Make sure python is installed with `Python --version`
- Update your pip version with `python -m pip install --upgrade pip`
- Make sure you have R installed, typically placed at  
  `C:\Program Files\R\R-4.4.0`
- As mentioned earlier, add the following to your **PATH** variable  
  `C:\Program Files\R\R-4.4.0\bin` (No action needed for mac)
- Install rpy2 without compiling with  
  `pip install --only-binary :all: rpy2`(Skip this step for mac)

Finally, go ahead and install the rnadtu package with  
`pip install rnadtu`

## License

RNADTU is licensed under the GNU General Public License v2.0.

It includes source code from the VCCRI/CIDR project, which is also distributed under the GPL v2.0.

See the License file for full details.