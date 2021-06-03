[![Check and publish Python Package](https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml/badge.svg)](https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml) 
[![PyPI version fury.io](https://badge.fury.io/py/climetlab-s2s-ai-challenge.svg)](https://pypi.python.org/pypi/climetlab-s2s-ai-challenge/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ecmwf-lab/climetlab-s2s-ai-challenge/main?urlpath=lab)

# S2S AI challenge Datasets


Sub seasonal to Seasonal (S2S) Artificial Intelligence Challenge : https://s2s-ai-challenge.github.io/

In this README is a description of how to get the data for the S2S AI challenge. Here is a more general [description of the S2S data](https://confluence.ecmwf.int/display/S2S/Description). The data used for the S2S AI challenge is a subset of the S2S data library. More detail can be found at https://confluence.ecmwf.int/display/S2S  and https://confluence.ecmwf.int/display/S2S/Parameters.

There are several ways to use the datasets. Either by direct download (`wget`, `curl`, `browser`) for [`GRIB`](https://en.wikipedia.org/wiki/GRIB) and [NetCDF](https://en.wikipedia.org/wiki/NetCDF) formats; or using the `climetlab` python package with this addon, for `GRIB` and `NetCDF` and `zarr` formats. [`zarr`](https://zarr.readthedocs.io/en/stable/) is a cloud-friendly experimental data format and supports dowloading only the part of the data that is required. It has been designed to work better than classical format on a cloud environment (experimental).

## Datasets description

There are four datasets provided for this challenge. As we are aiming at bringing together the two communities of Machine Learning and Weather Prediction, they have been aliases to use both two points of views:

| ML                          | NWP                          |                                                        |
| --------------------------- | ---------------------------- | ------------------------------------------------------ |
| `training-input`            | `hindcast-input`             | Training  dataset (input for training the ML models)   |
| `training-output-reference` | `hindcast-like-observations` | Training dataset (output for training the ML models)   |
| `training-output-benchmark` | `hindcast-benchmark`         | Benchmark output (on the training dataset)             |
| `test-input`                | `forecast-input`             | Test dataset (DO NOT use for training)                 |
| `test-output-reference`     | `forecast-like-observations` | Test dataset (DO NOT use)                              |
| `test-output-benchmark`     | `forecast-benchmark`         | Benchmark output (on the test dataset)                 |


**Overfitting** is always an potential issue when using ML algorithms. To address this, the data is usually split into three datasets : 
[training](https://en.wikipedia.org/wiki/Training,_validation,_and_test_sets#Training_dataset), 
[validation](https://en.wikipedia.org/wiki/Training,_validation,_and_test_sets#Validation_dataset) 
and [test](https://en.wikipedia.org/wiki/Training,_validation,_and_test_sets#Test_dataset). 
This terminology has lead to [some confusion in the past](https://en.wikipedia.org/wiki/Training,_validation,_and_test_sets#Confusion_in_terminology). 
Splitting the `hindcast-input` (`training-input`) dataset between training and validation is standard way and should be decided carefully.

The `forecast-input` (`test-input`) must not be used as a validation dataset  : it must not be used to tune the hyperparameters or make decision about the ML model. 
Fostering discussions about how to prevent overfitting may be an outcome of the challenge.

### Hindcast input (Training input)

The `hindcast-input`(`training-input`) dataset consists of data from three different models: ECMWF (ecmf), ECCC (cwao), NCEP (kwbc).
Use `origin="ecmwf"` (model name) or `origin="ecmwf"` (center name).
These data are hindcast data. This is used as the input for training the ML models.
This dataset is available as `grib`, `netcdf` or `zarr`.
In this dataset, the data is available from 1999 for the oldest, to 2019/12/31 for the most recent. <!-- which model is available from 1998? -->
  - ECMWF hindcast data
    - `forecast_time`: from 2000/01/02 to 2019/12/31, weekly every 7 days (every Thurday).
    - `lead_time`: 0 to 46 days
    - `valid_time` (`forecast_time` + `lead_time`): from 2000/01/02 to 2020/02/13
    - availables parameters : `2t/ci/gh/lsm/msl/q/rsn/sm100/sm20/sp/sst/st100/st20/t/tcc/tcw/tp/ttr/u/v`
  - ECCC hindcast data 
    - `forecast_time`: from to , weekly every 7 days (every Thurday).
    - `lead_time`: 1 to 32 days
    - `valid_time` (forecast_time + lead_time): from 
    - availables parameters: `2t/ci/gh/lsm/msl/q/rsn/sp/sst/t/tcc/tcw/tp/ttr/u/v`
    - parameters not available: sm20, sm100, st20, st100
  - NCEP hindcast data 
    - `forecast_time` : from 1999/01/07 to 2010/12/30, weekly every 7 days (every Thurday).
    - `lead_time` : 1 to 44 days
    - `valid_time` (`forecast_time` + `lead_time`): from 1999/01/07 to 2011/02/11
    - availables parameters: `2t/ci/gh/lsm/msl/q/sm100/sm20/sp/sst/st100/st20/t/tcc/tcw/tp/ttr/u/v`
    - parameter not available: `rsn`

 List of files :
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/netcdf/index.html),
  zarr (not available)

### Forecast input (Test input)
The `forecast-input` (`test-input`) dataset consists also in data from three different models: ECMWF (ecmf), ECCC (cwao), NCEP (eccc), for different dates.
These data are forecast data.
This could be used the input for applying the ML models in order to generate the output which is submitted for the challenge.
Using data from earlier date that 2020/01/01 is also allowed during the prediction phase.
The forecast start dates in this dataset are from 2020/01/02 to 2020/12/31.
  - For all 3 models: 
    - `forecast_time`: from 2020/01/02 to 2020/12/31, weekly every 7 days (every Thurday).
    - `valid_time` (`forecast_time` + `lead_time`): from 2020/01/02 to 2021/02/xx <!-- valid_time extends into 2021 -->
  - ECMWF forecast
    - `lead_time`: 0 to 46 days
    - available parameters (same as for Hindcast input (training input)
  - ECCC forecast 
    - `lead_time`: 1 to 32 days
    - available parameters (same as for Hindcast input (training input)
  - NCEP forecast 
    - `lead_time`: 1 to 44 days
    - available parameters (same as for Hindcast input (training input)

 List of files :
  [grib](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/test-input/0.3.0/grib/index.html),
  [netcdf](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/test-input/0.3.0/netcdf/index.html),
  zarr (missing)
  
### Observations (Reference Output)
The `hindcast-like-observations` (`training-output-reference`) dataset.
The `forecast-like-observations` (`test-output-reference`) dataset.

The observations are the ground truth to compare with the ML model output and evaluate them. It consists in observations from instruments of [temperature](http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/) and accumulated total [precipitation](http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/). The [NOAA CPC](https://www.cpc.ncep.noaa.gov/) datasets were downloaded from [IRIDL](iridl.ldeo.columbia.edu/). We provide observations in the same dimensions as the forecasts/hindcasts to have an easy match of forecasts/hindcast and ground truth. [See the script for technical details](https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/tree/main/tools/observations).


Generally speaking, only data available when the forecast is issued can be used by the ML models to perform their forecast:

__Rule: Observed data beyond the forecast date should not be used for prediction, for instance a forecast starting on 2020/07/01 should not use observed data beyond 2020/07/01).__

For all rules, see the [challenge website](https://s2s-ai-challenge.github.io/#rules).

See also the general rules of the challenge [here](https://s2s-ai-challenge.github.io/#rules).

Dates in the observation dataset are from 2000/01/01 to 2021/02/15.

The observations dataset have been build from real instrument observations.

- The `hindcast-like-observations` (`training-output-reference`) dataset :
 - Available from 2000/01/01 to 2019/12/31, weekly every 7 days (every Thurday)
 - Observation data before 2019/12/31 can be used for training (as the truth to evaluate and optimize the ML models or tweak hyper parameters using train/valid split or cross-validation).
- The `forecast-like-observations` (`test-output-reference`) dataset.
 - Available from2020/01/01 to 2021/02/20 , weekly every 7 days (every Thurday)
 - The test data must **not** be used during training. In theory, these data should not be disclosed during the challenge, but the nature of the data make is possible to access it from other sources. That is the reason why the code used for training model must be submitted along with the prediction (as a jupyter notebook) and the top ranked proposition will be reviewed by the organizing board. 

![train_validation_split](https://user-images.githubusercontent.com/8441217/114999589-e5f29f80-9e99-11eb-90e3-8a4a3e9545d5.png)

During forecast phase (i.e. the evaluation phase using the forecast-input dataset), 2020 observation data is used. Rule 1 still stands : Observed data beyond the forecast start date should not be used for prediction.

### Forecast Benchmark (Benchmark output)

The `forecast-benchmark` (`test-output-benchmark`) dataset is a probabilistic re-calibrated ECMWF forecast with categories `below normal`, `near normal`, `above normal`.

The benchmark consists in applying to the `forecast-input` a simple re-calibration of from the mean of the hindcast (training) data.

The benchmark data is available as follows :

  - `forecast_time`: from 2020/01/02 to 2020/12/31, weekly every 7 days (every Thurday).
  - `lead_time`: 14 days and 28 days, where this day represents the first day of the biweekly aggregate
  - `valid_time` (`forecast_time` + `lead_time`): from 2020/01/01 to 2021/01/29
  - `category`: `'below normal'`, `'near normal'`, `'above normal'` <!-- todo: implement in stoarge and/or climetlab @florian -->


## Data download (GRIB or NetCDF)

The URLs to download the data are constructed according to the following patterns: 

*For input datasets*, the pattern is https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/{datasetname}/0.3.0/{format}/{origin}-{fctype}-{parameter}-YYYYMMDD.nc

*For observations datasets (reference output)*, the pattern is https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/{datasetname}/{parameter}-YYYYMMDD.nc

*For benchmark datasets*, the pattern will be similar to https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-output-benchmark/{parameter}-weeks-{weeks}.nc (NOT AVAILABLE YET)


- {datasetname} : In the URLs the dataset name must follow the ML naming (`training-input` or `training-output-reference` or `training-output-benchmark`).
- {format} is `netcdf`. Training output is also available as GRIB file,  using `format='grib'` and replacing `".nc"` by `".grib"`
- {parameter} is `t2m` for [surface temperature at 2m](https://confluence.ecmwf.int/display/S2S/S2S+Surface+Air+Temperature), `tp` for [total precipitation](https://confluence.ecmwf.int/display/S2S/S2S+Total+Precipitation)
- {origin} : `ecmwf` or `eccc` or `ncep` <!-- we should have a clean table for this once -->
- {weeks} from [`"34"`, `"56"`, `["34", "56"]`] only for `benchmark` <!-- Todo @florian merge and use pd.Timedelta('14/28 d') -->
- `YYYYMMDD` is the date of main forecast time in the file.

The list of files for the `training-input` dataset can be found at
  - GRIB: [https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/grib/index.html](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/grib/index.html),
 - NetCDF: [https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/netcdf/index.html](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/netcdf/index.html),

The list of files for the `training-output-benchmark` dataset can be found at [https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-output-reference/0.3.0/netcdf/index.html](https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-output-reference/0.3.0/netcdf/index.html) (NetCDF only) (Not available yet)


Example to retrieve the file with wget :

``` wget https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/0.3.0/grib/ncep-hindcast-q-20101014.grib ``` (132.8M )

### Zarr format (experimental).
 
The zarr storage location include all the reference data. The zarr urls are **not** designed to be open in a browser (see [zarr](https://zarr.readthedocs.io/en/stable)):
While accessing the zarr storage without climetlab may be possible, we recommend using climetlab with the appropriate plugin (climetlab-s2s-ai-challenge)

Zarr urls are :
  -  `training-input` https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/{origin}/0.3.0/zarr/ (Not fully yet available)
  -  `training-output-reference` https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-output-reference/{origin}/0.3.0/zarr/ (Not full yet available)
  

## Using climetlab to access the data (supports grib, netcdf and zarr)

The climetlab python package allows easy access to the data with a few lines of code such as:
```
!pip install climetlab climetlab_s2s_ai_challenge
import climetlab as cml
cml.load_dataset("s2s-ai-challenge-training-input",
                         origin='ecmwf',
                         date=[20200102,20200109],
                         # optional : format='grib'
                         parameter='tp').to_xarray()
cml.load_dataset("s2s-ai-challenge-training-output-reference",
                         date=[20200102,20200109],
                         parameter='tp').to_xarray()
```

See the demo notebooks here: https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/notebooks.

Accessing the training data :
- Netcdf [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_netcdf.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_netcdf.ipynb)
- Grib [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_grib.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_grib.ipynb)
- Zarr [nbviewer](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_zarr.ipynb) [colab](https://colab.research.google.com/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_zarr.ipynb)  <span style="color:red;">(experimental)</span>.


Getting the observation (reference output) dataset see the [demo_observations notebook](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_observations.ipynb).

Getting the benchmark dataset see the [demo_benchmark notebook](https://nbviewer.jupyter.org/github/ecmwf-lab/climetlab-s2s-ai-challenge/blob/main/notebooks/demo_benchmark.ipynb).
