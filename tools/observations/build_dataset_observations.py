#!/usr/bin/env python3

# make sure scipy is installed
import argparse

import climetlab as cml
import pandas as pd
import scipy  # noqa: F401
import tqdm
import xarray as xr

try:
    import logging

    import coloredlogs

    coloredlogs.install(level="DEBUG")
except ImportError:
    import logging

FORECAST_DATASETNAME = "test-output-reference"
REFORECAST_DATASETNAME = "training-output-reference"


def main(args):
    if args.temperature:
        build_temperature(args, test=args.test)
    if args.rain:
        build_rain(args, test=args.test)


# GLOBAL VARS
lm = 47
leads = [pd.Timedelta(f"{d} d") for d in range(lm)]
start_year = 2000  # TODO: for NCEP starting in 1999
reforecast_end_year = 2019


global FINAL_FORMAT
FINAL_FORMAT = None


def get_final_format():
    global FINAL_FORMAT
    if FINAL_FORMAT:
        return FINAL_FORMAT
    ds = cml.load_dataset(
        "s2s-ai-challenge-training-input",
        origin="ecmwf",
        date=20200102,
        parameter="2t",
        format="netcdf",
    ).to_xarray()
    FINAL_FORMAT = ds.isel(forecast_time=0, realization=0, lead_time=0, drop=True)
    logging.info(f"target final coords : {FINAL_FORMAT.coords}")
    return FINAL_FORMAT


def write_to_disk(  # noqa: C901
    ds_lead_init,
    ds_time,
    basename,
    netcdf=True,
    zarr=False,
    split_key=None,
    split_values=None,
    split_key_values=None,
    verbose=True,
):
    # ds_dev = ds.sel(time=slice("2010-01-01", "2010-03-01"))
    assert type(basename) == str

    import os

    outdir = os.path.dirname(basename)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # add attrs to file
    ds_lead_init.attrs.update(
        {
            "created_by_software": "climetlab-s2s-ai-challenge",
            "created_by_script": "tools/observations/makefile",
        }
    )
    ds_time.attrs.update(
        {
            "created_by_software": "climetlab-s2s-ai-challenge",
            "created_by_script": "tools/observations/makefile",
        }
    )

    # add metadata to coords # open to renaming forecast_time -> forecast_time
    ds_lead_init["forecast_time"].attrs.update(
        {"standard_name": "forecast_reference_time", "long_name": "initial time of forecast"}
    )
    ds_lead_init["lead_time"].attrs.update(
        {"standard_name": "forecast_period", "long_name": "time since forecast_time"}
    )
    if "valid_time" in ds_lead_init:
        ds_lead_init["valid_time"].attrs.update(
            {"standard_name": "time", "long_name": "time", "comment": "valid_time = forecast_time + lead_time"}
        )

    if netcdf and split_key is None:
        filename = basename + ".nc"
        # logging.info(f"{ds_lead_init.sizes}")
        if verbose:
            logging.info(f"Writing {filename}")
            logging.debug(str(ds_lead_init))
        ds_lead_init.to_netcdf(filename)
        if verbose:
            logging.debug(f"Written {filename}")

    if zarr:
        filename = basename + ".zarr"
        if verbose:
            logging.info(f"Writing {filename}")
            logging.debug(str(ds_lead_init))
        # for fine and granular access performance over the internet
        # it would make sense to chunk biweekly once a month
        # chunk={'forecast_time':4, 'lead_time': 14, 'longitude':'auto', 'latitude':'auto'}
        ds_lead_init.chunk("auto").to_zarr(filename, consolidated=True, mode="w")
        if verbose:
            logging.debug(f"Written {filename}")

    if split_key is not None:
        # split along month-day
        for t in tqdm.tqdm(split_values):
            dt = split_key_values
            # select same day and month
            dt = dt.sel({split_key: dt[split_key].dt.month == t.dt.month})
            dt = dt.sel({split_key: dt[split_key].dt.day == t.dt.day})
            ds_lead_init_split = ds_time.sel(valid_time=dt)
            # only for tp, accumulate pr to tp
            if "tp" in ds_lead_init_split.data_vars:
                ds_lead_init_split = (
                    ds_lead_init_split.cumsum("lead_time", keep_attrs=True, skipna=False)
                    .assign_coords(lead_time=leads)
                    .assign_coords(valid_time=dt)
                )
            day_string = str(t.dt.day.values).zfill(2)
            month_string = str(t.dt.month.values).zfill(2)
            check_lead_time_forecast_time(ds_lead_init_split)

            if ds_lead_init_split[split_key].size not in [
                1,
                20,
            ]:  # , print(ds_lead_init_split[split_key].size) # forecast, reforecast
                print(ds_lead_init_split.sizes)
                print(ds_lead_init_split[split_key].size, t, dt)
                assert False
            # assert ds_lead_init_split[split_key].size in [1, 20], print(ds_lead_init_split[split_key].size) # forecast, reforecast # noqa: E501
            write_to_disk(
                ds_lead_init_split,
                ds_lead_init_split,
                basename=f"{basename}-2020{month_string}{day_string}",
                netcdf=netcdf,
                zarr=zarr,
                verbose=False,
            )


def create_valid_time_from_forecast_time_and_lead_time(inits, leads):
    """Take forecast_time and add lead_time into the future creating two-dimensional valid_time."""
    inits = xr.DataArray(
        inits,
        dims="forecast_time",
        coords={"forecast_time": inits},
    )
    valid_times = xr.concat(
        [
            xr.DataArray(
                inits + pd.Timedelta(f"{x} d"),
                dims="forecast_time",
                coords={"forecast_time": inits},
            )
            for x in range(lm)
        ],
        "lead_time",
    )
    valid_times = valid_times.assign_coords(lead_time=leads)
    return valid_times.rename("valid_time")


def create_forecast_valid_times():
    """Forecast start dates in 2020."""
    forecasts_inits = pd.date_range(start="2020-01-02", end="2020-12-31", freq="7D")
    return create_valid_time_from_forecast_time_and_lead_time(forecasts_inits, leads)


def create_reforecast_valid_times():
    """Inits from year 2000 to 2019 for the same days as in 2020."""
    reforecasts_inits = []
    inits_2020 = create_forecast_valid_times().forecast_time.to_index()
    for year in range(start_year, reforecast_end_year + 1):
        # dates_year = pd.date_range(start=f"{year}-01-02", end=f"{year}-12-31", freq="7D")
        dates_year = pd.DatetimeIndex([i.strftime("%Y%m%d").replace("2020", str(year)) for i in inits_2020])
        dates_year = xr.DataArray(
            dates_year,
            dims="forecast_time",
            coords={"forecast_time": dates_year},
        )
        reforecasts_inits.append(dates_year)
    reforecasts_inits = xr.concat(reforecasts_inits, dim="forecast_time")
    return create_valid_time_from_forecast_time_and_lead_time(reforecasts_inits, leads)


def check_lead_time_forecast_time(ds, copy_filename=None):
    """Check that ds has lead_time and forecast_time as dim and coords and valid_time as coord only."""
    assert "lead_time" in ds.coords
    assert "lead_time" in ds.dims
    assert "forecast_time" in ds.dims
    assert "forecast_time" in ds.coords
    assert "valid_time" in ds.coords
    assert "valid_time" not in ds.dims

    # if copy_filename is None or copy_filename is False:
    #    import os
    #    import tempfile
    #
    #    fd, copy_filename = tempfile.mkstemp()
    #    os.close(fd)
    # ds.to_netcdf(copy_filename)
    # ds = xr.open_dataset(copy_filename)

    # assert "lead_time" in ds.coords
    # assert "lead_time" in ds.dims
    # assert "forecast_time" in ds.dims
    # assert "forecast_time" in ds.coords
    # assert "valid_time" in ds.coords
    # assert "valid_time" not in ds.dims


def build_temperature(args, test=False):
    check = args.check
    logging.info("Building temperature data")
    start_year = args.start_year
    outdir = args.outdir
    param = "t2m"

    # chunk_dim = "T"
    # chunk_dim = "X"
    # tmin = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.tmin/dods', chunks={chunk_dim:'auto'}) # noqa: E501
    # tmax = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.tmax/dods', chunks={chunk_dim:'auto'}) # noqa: E501

    tmin = xr.open_mfdataset(f"{args.input}/tmin/data.*.nc", chunks={"T": "auto"}).rename({"tmin": "t"})
    tmax = xr.open_mfdataset(f"{args.input}/tmax/data.*.nc", chunks={"T": "auto"}).rename({"tmax": "t"})
    # t = xr.concat([tmin, tmax], "m").mean("m")
    t = (tmin + tmax) / 2
    t["T"] = pd.date_range(start="1979-01-01", freq="1D", periods=t.T.size)

    t = t.rename({"X": "longitude", "Y": "latitude", "T": "time"})
    if test:
        t = t.sel(time=slice("2009-10-01", "2010-03-01"))
    t = t.sel(time=slice(f"{start_year-1}-12-24", None))

    t["t"].attrs = tmin["t"].attrs

    # metadata
    t = t.rename({"t": param})
    t = t + 273.15
    t[param].attrs["units"] = "K"
    t[param].attrs["long_name"] = "2m Temperature"
    t[param].attrs["standard_name"] = "air_temperature"
    t.attrs.update(
        {
            "source_dataset_name": "temperature daily from NOAA NCEP CPC: Climate Prediction Center",
            "source_hosting": "IRIDL",
            "source_url": "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/",
        }
    )
    t = t.interp_like(get_final_format()).compute().chunk("auto")

    # killed write_to_disk(t, f"{outdir}/{param}-daily-since-{start_year}")
    t = t.sel(
        time=slice(str(start_year), None)
    )  # could use this to calculate observations-as-forecasts locally in climetlab with less downloading

    # but for the competition it would be best to have dims (forecast_time, lead_time, longitude, latitude)
    t = t.rename({"time": "valid_time"})

    forecast_valid_times = create_forecast_valid_times()
    logging.info("Format for forecast valid times")
    logging.debug(t)
    logging.debug(forecast_valid_times)
    t_forecast = t.sel(valid_time=forecast_valid_times)
    if check:
        check_lead_time_forecast_time(t_forecast)
    filename = f"{outdir}/{FORECAST_DATASETNAME}/{param}"  # /daily-since-{start_year}"
    write_to_disk(
        t_forecast,
        t,
        filename,
        split_key="forecast_time",
        split_values=forecast_valid_times["forecast_time"],
        split_key_values=forecast_valid_times,
    )  # push to cloud

    logging.info("Format for REforecast valid times")
    reforecast_valid_times = create_reforecast_valid_times()
    logging.debug(t)
    logging.debug(reforecast_valid_times)
    t_reforecast = t.sel(valid_time=reforecast_valid_times)
    if check:
        check_lead_time_forecast_time(t_reforecast)

    filename = f"{outdir}/{REFORECAST_DATASETNAME}/{param}"  # /weekly-since-{start_year}"  # -to-{reforecast_end_year}"
    write_to_disk(
        t_reforecast,
        t,
        filename,
        split_key="forecast_time",
        split_values=forecast_valid_times["forecast_time"],
        split_key_values=reforecast_valid_times,
    )  # push to cloud


def build_rain(args, test=False):
    check = args.check
    logging.info("Building rain data")
    start_year = args.start_year
    outdir = args.outdir
    param = "tp"
    # rain = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/dods', chunks={'X':'auto'}) # noqa: E501
    # rain = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/dods', chunks={'T':'auto'}) # noqa: E501
    rain = xr.open_mfdataset(f"{args.input}/rain/data.*.nc")
    rain = rain.rename({"X": "longitude", "Y": "latitude", "T": "time"})
    if test:
        rain = rain.sel(time=slice("2009-10-01", "2010-03-01"))
    rain = rain.sel(time=slice(f"{start_year-1}-12-24", None))

    rain = rain.interp_like(get_final_format())
    rain = rain.rename({"rain": "pr"})
    # could use this to calculate tp locally
    # write_to_disk(rain, rain, f"{outdir}/pr-daily-since-{start_year}")

    # accumulate rain
    # metadata
    rain = rain.rename({"pr": param})
    rain[param].attrs["units"] = "kg m-2"
    rain[param].attrs["long_name"] = "total precipitation"
    rain[param].attrs["standard_name"] = "precipitation_amount"
    rain[param].attrs["comment"] = "precipitation accumulated since lead_time including 0 days"
    del rain[param].attrs["history"]
    rain.attrs.update(
        {
            "source_dataset_name": "NOAA NCEP CPC UNIFIED_PRCP GAUGE_BASED GLOBAL v1p0 extREALTIME rain: Precipitation data",  # noqa: E501
            "source_hosting": "IRIDL",
            "source_url": "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/dods",  # noqa: E501
        }
    )
    # write_to_disk(rain, ...)
    # could use this to calculate observations-as-forecasts locally in climetlab with less downloading

    # but for the competition it would be best to have dims (forecast_time, lead_time, longitude, latitude)
    rain = rain.rename({"time": "valid_time"}).compute().chunk("auto")

    forecast_valid_times = create_forecast_valid_times()
    logging.info("Format for forecast valid times")
    logging.debug(rain)
    logging.debug(forecast_valid_times)
    rain_forecast = rain.sel(valid_time=forecast_valid_times)
    if check:
        check_lead_time_forecast_time(rain_forecast)
    # accumulate
    rain_forecast = rain_forecast.cumsum("lead_time", keep_attrs=True, skipna=False)
    filename = f"{outdir}/{FORECAST_DATASETNAME}/{param}"  # /daily-since-{start_year}"
    write_to_disk(
        rain_forecast,
        rain,
        filename,
        split_key="forecast_time",
        split_values=forecast_valid_times["forecast_time"],
        split_key_values=forecast_valid_times,
    )  # push to cloud

    logging.info("Format for REforecast valid times")
    reforecast_valid_times = create_reforecast_valid_times()
    logging.debug(rain)
    logging.debug(reforecast_valid_times)
    rain_reforecast = rain.sel(valid_time=reforecast_valid_times)
    if check:
        check_lead_time_forecast_time(rain_reforecast)
    # accumulate
    rain_reforecast = rain_reforecast.cumsum("lead_time", keep_attrs=True, skipna=False)
    filename = f"{outdir}/{REFORECAST_DATASETNAME}/{param}"  # /weekly-since-{start_year}"

    write_to_disk(
        rain_reforecast,
        rain,
        filename,
        split_key="forecast_time",
        split_values=forecast_valid_times["forecast_time"],
        split_key_values=reforecast_valid_times,
    )  # push to cloud


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parser.add_argument("-p", "--param", nargs="+", help=' Either temperature or rain')
    parser.add_argument("-i", "--input", help="input netcdf files", default="/s2s-obs/")
    parser.add_argument(
        "-o",
        "--outdir",
        help="output netcdf and zarr files",
        default="/s2s-obs/observations",
    )
    parser.add_argument("--temperature", action="store_true")
    parser.add_argument("--rain", action="store_true")
    parser.add_argument(
        "--test",
        action="store_true",
        help="For dev purpose, use only part of the input data",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--start-year", type=int, default=2000)

    args = parser.parse_args()
    main(args)
