[![Check and publish Python Package](https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml/badge.svg)](https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml) [![pypi](https://img.shields.io/pypi/v/climetlab-s2s-ai-challenge.svg)](https://pypi.python.org/pypi/climetlab-s2s-ai-challenge/) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ecmwf-lab/climetlab-s2s-ai-challenge/main?urlpath=lab)

# S2S AI challenge Datasets

Sub seasonal to Seasonal (S2S) Artificial Intelligence Challenge : http://todo.link

In this README is a description of how to get the data for the S2S AI challenge. Here is a more general [description of the S2S data](https://confluence.ecmwf.int/display/S2S/Description). The data used for the S2S AI challenge is a subset of this S2S data.

Related github page https://github.com/wmo-im/s2s_ai_challenge

There are several ways to use the datasets. Either by direct download (wget, curl, browser) for GRIB and NetCDF formats ; or using the climetlab python package with this addon, for GRIB and NetCDF and zarr formats. Zarr is a cloud-friendly experimental data format and supports dowloading only the part of the data that is required. It has been designed to work better than classical format on a cloud environment (experimental).

## Datasets description

There are four datasets: `training-input`, `forecast-input`, `observations`, `forecast-benchmark`.

### Training input

The `training-input` dataset consists in data from three different models : ECMWF (ecmf), ECCC (cwao), NCEP (eccc).
These data are hindcast data. This is used as the input for training the ML models.
This dataset is available as grib, netcdf or zarr.
In this dataset, the data is available from 1998 for the oldest, to 2019/12/31 for the most recent. 
  - ECMWF hindcast data in `training-input` dataset
    - forecast_time : from 2000/01/01 to 2019/12/31, weekly every 7 days (every Thurday).
    - lead_time : 0 to 46 days
    - valid_time (forecast_time + lead_time): from 2000/01/01 to 2019/12/31
    - `training-input/ecmwf` :
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ecmwf-hindcast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ecmwf-hindcast/0.2.3/netcdf/index.html),
   zarr
  - ECCC hindcast data in `training-input` dataset
    - forecast_time : from , weekly every 7 days (every Thurday).
    - lead_time : 1 to 32 days
    - valid_time (forecast_time + lead_time): from 
    - variables sm20, sm100, st20, st100 not available
    - `training-input/eccc` :
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/eccc-hindcast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/eccc-hindcast/0.2.3/netcdf/index.html),
   zarr
  - NCEP hindcast data in `training-input` dataset
    - forecast_time : from 1999/01/07 to 2010/12/30, weekly every 7 days (every Thurday).
    - lead_time : 1 to 44 days
    - valid_time (forecast_time + lead_time): from 1999/01/07 to 2011/02/11
    - variable "rsn" not available.
    - `training-input/ncep` : 
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ncep-hindcast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ncep-hindcast/0.2.3/netcdf/index.html),
  zarr

### Forecast input
The `forecast-input` dataset consists also in data from three different models : ECMWF (ecmf), ECCC (cwao), NCEP (eccc), for different dates.
These data are forecast data.
This could be used the input for applying the ML models in order to generate the output which is submitted for the challenge.
Using data from earlier date that 2020/01/01 is also allowed during the prediction phase.
The forecast start dates in this dataset are from 2020/01/02 to 2020/12/31.
  - For all 3 models : 
    - forecast_time : from 2020/01/02 to 2020/12/31, weekly every 7 days (every Thurday).
    - valid_time (forecast_time + lead_time): from 2020/01/02 to 2020/12/31
  - ECMWF forecast data in `forecast-input` dataset
    - lead_time : 0 to 46 days
    - `forecast-input/ecmwf`
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.2.3/netcdf/index.html),
  zarr
  - ECCC hindcast data in `forecast-input` dataset
    - lead_time : 1 to 32 days
    - variables sm20, sm100, st20, st100 not available
    - `forecast-input/eccc` 
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/eccc-forecast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/eccc-forecast/0.2.3/netcdf/index.html),
  zarr
  - NCEP hindcast data in `forecast-input` dataset
    - lead_time : 1 to 44 days
    - variable "rsn" not available.
    - `forecast-input/ncep`
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ncep-forecast/0.2.3/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ncep-forecast/0.2.3/netcdf/index.html),
 zarr

### Observations
The `observations` dataset is the ground truth to compare with the ML model output and evaluate them. It consists in observation from instruments of temperature and total precipitation (TODO add more description). 
Dates in the observation dataset are from 1998/01/01 to 2021/02/20.

The `observation` dataset will used separately for training and forecast (i.e. separation between training and evaluation). Generally speaking, only past data can be used by the ML models to perform their forecast :

__Rule 1 : Observed data beyond the forecast date should not be used for prediction, for instance a forecast starting on 2020/07/01 should not use observed data beyond 2020/07/01).__

The `observations` dataset have been build from real instrument observations :
 - Available from 2000/01/01 to 2021/02/20, weekly every 7 days (every Thurday) (see the scripts to create them here TODO).
 - Observation data before 2019/12/31 can be used for training (as the truth to evaluate and optimize the ML models).
- Observation data from 2020/01/01 to 2021/02/20 must **not** be used during training. In theory, these data should not be disclosed during the challenge, but the nature of the data make is possible to access it from other sources. That is the reason why the code used for training model must be submitted along with the prediction (as a jupyter notebook) and the top ranked proposition will be reviewed by the organizing board. 

![train_validation_split](https://user-images.githubusercontent.com/8441217/114999589-e5f29f80-9e99-11eb-90e3-8a4a3e9545d5.png)

During training phase, observed data beyond 2020/01/01 must not be used for training.
During forecast phase (i.e. the evaluation phase using the forecast-input dataset), 2020 observation data is used. Rule 1 still stands : Observed data beyond the forecast start date should not be used for prediction.

### Forecast Benchmark
The `forecast-benchmark` dataset is an example of output of a ML model to be submitted.
The "ML model" used to produce this dataset is very crude and consists in applying to the `forecast-input' a simple re-calibration of from the mean of the hindcast (training) data.
  - forecast_time : from 2020/01/01 to 2020/12/31, weekly every 7 days (every Thurday).
  - lead_time : two values : 28 days and 35 days (To be discussed)
  - valid_time (forecast_time + lead_time): from 2020/01/01 to 2020/12/31


## Data download (GRIB or NetCDF)

The list of GRIB and files for the 'training-input' dataset can be found at : 

https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/{origin}-{fctype}/{version}/grib/{origin}-{fctype}-{parameter}-YYYYMMDD.grib

The list of NetCDF and files for the 'training-input' dataset can be found at : 

https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/{origin}-{fctype}/{version}/netcdf/{origin}-{fctype}-{parameter}-YYYYMMDD.nc


The URLs are constructed according to the following pattern: 

- {origin} : ecmwf or eccc or ncep.
- {fctype} : hindcast or forecast (hindcast or forecast).
- {param} is "t2m" for surface temperature at 2m, "tp" for total precipitation using CF convention.
- YYYYMMDD is the date of retrieval.
- {version} is 0.2.3.

Example to retrieve the file with wget :

``` wget https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.2.3/grib/ecmwf-forecast-sp-20200116.grib ``` (132.8M )

### Zarr format (experimental).

The zarr storage location include all the reference data. The zarr urls are **not** designed to be open in a browser (see [zarr](https://zarr.readthedocs.io/en/stable)):
While accessing the zarr storage without climetlab may be possible, we recommend using climetlab with the appropriate plugin (climetlab-s2s-ai-challenge)

Zarr urls are :
  -  `training-input` https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/{origin}/0.1.43/zarr/ TODO
  -  `forecast-input` https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/{origin}/0.1.43/zarr/ TODO
  -  `observations` : not available.
  -  `forecast-benchmark` : not available.

## Using climetlab to access the data (supports grib, netcdf and zarr)

See the demo notebooks here (https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/notebooks) : 
- Netcdf [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_netcdf.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_netcdf.ipynb)(TODO update the notebooks)
- Grib [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_grib.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_grib.ipynb)(TODO update the notebooks)
- Zarr [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_zarr.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/master/notebooks/demo_zarr.ipynb)  <span style="color:red;">(experimental)</span> .(TODO update the notebooks)

The climetlab python package allows easy access to the data with a few lines of code such as:
```

Full data not uploaded. Only two dates available for now.

!pip install climetlab climetlab_s2s_ai_challenge
import climetlab as cml
ds = cml.load_dataset("s2s-ai-challenge-training-input", origin="ecmwf", date="20200102", parameter='t2m')
ds.to_xarray()
```
