# S2S AI competition Datasets

Sub seasonal to Seasonal (S2S) Artificial Intelligence Competition : http://todo.link

In this README is a description of how to get the data for the S2S AI competition. You can find a full description of the dataset here : http://todo.link.int

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
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ecmwf-hindcast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ecmwf-hindcast/0.1.50/netcdf/index.html),
   zarr
  - ECCC hindcast data in `training-input` dataset
    - forecast_time : from , weekly every 7 days (every Thurday).
    - lead_time : 1 to 32 days
    - valid_time (forecast_time + lead_time): from 
    - variables sm20, sm100, st20, st100 not available
    - `training-input/eccc` :
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/eccc-hindcast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/eccc-hindcast/0.1.50/netcdf/index.html),
   zarr
  - NCEP hindcast data in `training-input` dataset
    - forecast_time : from 1999/01/07 to 2010/12/30, weekly every 7 days (every Thurday).
    - lead_time : 1 to 44 days
    - valid_time (forecast_time + lead_time): from 1999/01/07 to 2011/02/11
    - variable "rsn" not available.
    - `training-input/ncep` : 
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ncep-hindcast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ncep-hindcast/0.1.50/netcdf/index.html),
  zarr

### Forecast input
The `forecast-input` dataset consists also in data from three different models : ECMWF (ecmf), ECCC (cwao), NCEP (eccc), for different dates.
These data are forecast data.
This could be used the input for applying the ML models in order to generate the output which is submitted for the competition.
Using data from earlier date that 2020/01/01 is also allowed during the prediction phase.
The forecast start dates in this dataset are from 2020/01/02 to 2020/12/31.
  - For all 3 models : 
    - forecast_time : from 2020/01/02 to 2020/12/31, weekly every 7 days (every Thurday).
    - valid_time (forecast_time + lead_time): from 2020/01/02 to 2020/12/31
  - ECMWF forecast data in `forecast-input` dataset
    - lead_time : 0 to 46 days
    - `forecast-input/ecmwf`
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.1.50/netcdf/index.html),
  zarr
  - ECCC hindcast data in `forecast-input` dataset
    - lead_time : 1 to 32 days
    - variables sm20, sm100, st20, st100 not available
    - `forecast-input/eccc` 
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/eccc-forecast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/eccc-forecast/0.1.50/netcdf/index.html),
  zarr
  - NCEP hindcast data in `forecast-input` dataset
    - lead_time : 1 to 44 days
    - variable "rsn" not available.
    - `forecast-input/ncep`
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ncep-forecast/0.1.50/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ncep-forecast/0.1.50/netcdf/index.html),
 zarr

### Observations
The `observations` dataset is the ground truth to compare with the ML model output and evaluate them. It consists in observation from instruments of temperature and total precipitation (TODO add more description). 
Dates in the observation dataset are from 1998/01/01 to 2021/02/20.

The observation data should be used for training and forecast (i.e. separation between training and evaluation). 
The rule is that (TODO choose one):
- _Allow using 2020 data during training_
  - Observed data beyond the forecast date should not be used for training and forecast (for instance a forecast starting on 2020/07/01 should not use observed data beyond 2020/07/01).

- _Allow using 2020 data during training_
  - Observed data beyond the forecast start date should not be used for training and forecast. For instance : 
    - During forecast phase (evaluation): a forecast starting on 2020/07/02 should predict 2020/07/30 (+4 weeks) and 2020/08/13 (+6 weeks). It should not use observed data beyond 2020/07/02.
    - During forecast phase (evaluation): a forecast starting on 2020/01/16 should predict 2020/02/13 (+4 weeks) and 2020/02/28 (+6 weeks). It should not use observed data beyond 2020/01/16.
    - During training phase: observation data on 2020/02/20 can be used. **Including observations from 2020/02/13.**

- _Forbid using 2020 data during training_
  - During training phase, observed data beyond 2019/12/31 should not be used for training.
  - During forecast phase (evaluation using the forecast-input dataset), observed data beyond the forecast start date should not be used for prediction (for instance a forecast starting on 2020/07/01 should not use observed data beyond 2020/07/01).
 

The `observations` dataset can be splitted into `observations/training` and `observations/forecast`: 
  - `observations/training`
    - From 2000/01/01 to 2019/12/31, weekly every 7 days (every Thurday).
    - This is the truth to evaluate and optimize the ML models during training.
  - `observations/forecast`
    - From 2020/01/01 to 2021/02/20, weekly every 7 days (every Thurday).
    - This a evaluation dataset and must **not** be used during training.
    - In theory, these data should not be disclosed during the competition, but the nature of the data make is possible to access it from other means. That is the reason why the code used for training model must be submitted along with the prediction (as a jupyter notebook) and the top ranked proposition will be reviewed by the organizing board. (_Question:To be discussed_)

_Question : Should we split this "observations" dataset into two dataset to make it clear to communicate : "do not use observation/forecast during training"._

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
- {version} is 0.1.50.

Example to retrieve the file with wget :

``` wget https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.1.50/grib/ecmwf-forecast-sp-20200116.grib ``` (132.8M )

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
