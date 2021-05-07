#!/usr/bin/env python3

# make sure scipy is installed
import argparse

import climetlab as cml
import pandas as pd
import scipy  # noqa: F401
import xarray as xr

try:
    import logging

    import coloredlogs

    coloredlogs.install(level="DEBUG")
except ImportError:
    import logging


def main(args):
    if args.temperature:
        build_temperature(args, test=args.test)
    if args.rain:
        build_rain(args, test=args.test)


global FINAL_FORMAT
FINAL_FORMAT = None


def get_final_format():
    global FINAL_FORMAT
    if FINAL_FORMAT:
        return FINAL_FORMAT
    is_test = "-dev"
    ds = cml.load_dataset(
        "s2s-ai-challenge-training-input" + is_test,
        origin="ecmwf",
        date=20200102,
        parameter="2t",
        format="netcdf",
    ).to_xarray()
    FINAL_FORMAT = ds.isel(forecast_time=0, realization=0, lead_time=0, drop=True)
    logging.info(f"target final coords : {FINAL_FORMAT.coords}")
    return FINAL_FORMAT


lm = 46
leads = [pd.Timedelta(f"{d} d") for d in range(lm)]

start_year = 2000
reforecast_end_year = 2019


def create_valid_time_from_forecast_reference_time_and_lead_time(inits, leads):
    """Take forecast_reference_time and add lead_time into the future creating two-dimensional valid_time."""
    inits = xr.DataArray(
        inits, dims="forecast_reference_time", coords={"forecast_reference_time": inits}
    )
    valid_times = xr.concat(
        [
            xr.DataArray(
                inits + pd.Timedelta(f"{x} d"),
                dims="forecast_reference_time",
                coords={"forecast_reference_time": inits},
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
    return create_valid_time_from_forecast_reference_time_and_lead_time(
        forecasts_inits, leads
    )


def create_reforecast_valid_times():
    """Inits from year 2000 to 2019 for the same days as in 2020."""
    reforecasts_inits = []
    for year in range(start_year, reforecast_end_year + 1):
        dates_year = pd.date_range(
            start=f"{year}-01-02", end=f"{year}-12-31", freq="7D"
        )
        dates_year = xr.DataArray(
            dates_year,
            dims="forecast_reference_time",
            coords={"forecast_reference_time": dates_year},
        )
        reforecasts_inits.append(dates_year)
    reforecasts_inits = xr.concat(reforecasts_inits, dim="forecast_reference_time")
    return create_valid_time_from_forecast_reference_time_and_lead_time(
        reforecasts_inits, leads
    )


def check_lead_time_forecast_reference_time(ds, copy_filename=None):
    """Check that ds has lead_time and forecast_reference_time as dim and coords and valid_time as coord only."""
    assert "lead_time" in ds.coords
    assert "lead_time" in ds.dims
    assert "forecast_reference_time" in ds.dims
    assert "forecast_reference_time" in ds.coords
    assert "valid_time" in ds.coords
    assert "valid_time" not in ds.dims

    if copy_filename is None or copy_filename is False:
        import os
        import tempfile

        fd, copy_filename = tempfile.mkstemp()
        os.close(fd)
    ds.to_netcdf(copy_filename)
    ds = xr.open_dataset(copy_filename)

    assert "lead_time" in ds.coords
    assert "lead_time" in ds.dims
    assert "forecast_reference_time" in ds.dims
    assert "forecast_reference_time" in ds.coords
    assert "valid_time" in ds.coords
    assert "valid_time" not in ds.dims


def build_temperature(args, test=False):
    logging.info("Building temperature data")
    start_year = args.start_year
    outdir = args.outdir
    param = "t2m"

    # chunk_dim = "T"
    # chunk_dim = "X"
    # tmin = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.tmin/dods', chunks={chunk_dim:'auto'}) # noqa: E501
    # tmax = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.temperature/.daily/.tmax/dods', chunks={chunk_dim:'auto'}) # noqa: E501

    tmin = xr.open_mfdataset(f"{args.input}/tmin/data.*.nc").rename({"tmin": "t"})
    tmax = xr.open_mfdataset(f"{args.input}/tmax/data.*.nc").rename({"tmax": "t"})
    t = xr.concat([tmin, tmax], "m").mean("m")

    t["T"] = xr.cftime_range(start="1979-01-01", freq="1D", periods=t.T.size)

    t = t.rename({"X": "longitude", "Y": "latitude", "T": "time"})
    if test:
        t = t.sel(time=slice("2009-10-01", "2010-03-01"))
    t = t.sel(time=slice(f"{start_year-1}-12-24", None))

    t["t"].attrs = tmin["t"].attrs
    t["t"].attrs["long_name"] = "Daily Temperature"  # check with EWC S2S
    # set standard_name for CF
    t = t.rename({"t": param})
    t = t + 273.15
    t[param].attrs["units"] = "K"
    t[param].attrs["long_name"] = "T"
    t[param].attrs["standard name"] = "air_temperature"
    t = t.interp_like(get_final_format())

    write_to_disk(ds=t, outdir=outdir, param=param, freq="daily", start_year=start_year)

    t["time"] = t["time"].compute()
    # first_thursday = t.time.where(t.time.dt.dayofweek == 3, drop=True)[1]

    # forecasts issued every thursday: obs weekly aggregated from thursday->wednesday
    # t = t.sel(time=slice(first_thursday, None)).resample(time="7D").mean()
    t = t.sel(time=slice(str(start_year), None)).chunk("auto")

    # takes an hour
    t.compute()

    # thats temperature with dimensions (time, longitude, latitude)
    # write_to_disk(
    #     ds=t, outdir=outdir, param=param, freq="weekly", start_year=start_year
    # )

    forecast_valid_times = create_forecast_valid_times()

    # but for the competition it would be best to have dims (forecast_reference_time, lead_time, longitude, latitude)
    t = t.rename({"time": "valid_time"})
    logging.info("Format for forecast valid times")
    logging.debug(t)
    logging.debug(forecast_valid_times)
    t_forecast = t.sel(valid_time=forecast_valid_times)
    check_lead_time_forecast_reference_time(t_forecast)
    t_forecast.to_netcdf(
        f"{outdir}/{param}_verification_forecast_reference_time_2020_lead_time_weekly.nc"
    )

    logging.info("Format for REforecast valid times")
    reforecast_valid_times = create_reforecast_valid_times()
    # takes massive memory, maybe need to do for individual years to netcdf files
    logging.debug(t)
    logging.debug(reforecast_valid_times)
    t_reforecast = t.sel(valid_time=reforecast_valid_times)
    check_lead_time_forecast_reference_time(t_reforecast)
    t_reforecast.to_netcdf(
        f"{outdir}/{param}_verification_forecast_reference_time_{start_year}_{reforecast_end_year}_lead_time_weekly.nc"
    )


#    full = t_forecast
#    key = 'forecast_reference_time'
#    for x in full[key].values:
#       splitds = full.sel(**{key : x})
#       write_to_disk(f'{oudir}/{param}-{x}.nc')
#       write_to_disk(splitds, outdir, param, freq, start_year, netcdf=True, zarr=False):


def write_to_disk(ds, outdir, param, freq, start_year, netcdf=True, zarr=False):
    _write_to_disk(ds, outdir, param, freq, start_year, netcdf, zarr)

    # ds_dev = ds.sel(time=slice("2010-01-01", "2010-03-01"))
    # _write_to_disk(ds_dev, outdir + "-dev", param, freq, start_year, netcdf, zarr)


def _write_to_disk(ds, outdir, param, freq, start_year, netcdf, zarr):
    import os

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if netcdf:
        filename = f"{outdir}/{param}-{freq}-since-{start_year}.nc"
        logging.info(f'Writing {param} in "{filename}"')
        logging.debug(str(ds))
        ds.to_netcdf(filename)

    if zarr:
        filename = f"{outdir}/{param}-{freq}-since-{start_year}.zarr"
        logging.info(f'Writing {param} in "{filename}"')
        logging.debug(str(ds))
        ds.chunk("auto").to_zarr(filename, consolidated=True, mode="w")


def build_rain(args, test=False):
    logging.info("Building rain data")
    start_year = args.start_year
    outdir = args.outdir
    param = "tp"  # TODO this is pr
    # rain = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/dods', chunks={'X':'auto'}) # noqa: E501
    # rain = xr.open_dataset('http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.extREALTIME/.rain/dods', chunks={'T':'auto'}) # noqa: E501
    rain = xr.open_mfdataset(f"{args.input}/rain/data.*.nc")
    rain = rain.rename({"X": "longitude", "Y": "latitude", "T": "time"})
    if test:
        rain = rain.sel(time=slice("2009-10-01", "2010-03-01"))
    rain = rain.sel(time=slice(f"{start_year-1}-12-24", None))
    rain = rain.rename({"rain": param})

    rain = rain.interp_like(get_final_format())

    write_to_disk(
        ds=rain, outdir=outdir, param=param, freq="daily", start_year=start_year
    )

    rain["time"] = rain["time"].compute()
    first_thursday = rain.time.where(rain.time.dt.dayofweek == 3, drop=True)[
        1
    ].compute()

    # forecasts issued every thursday: obs weekly aggregated from thursday->wednesday
    rain = (
        rain.sel(time=slice(first_thursday, None))
        .resample(time="7D")
        .mean()
        .sel(time=slice(str(start_year), None))
        .chunk("auto")
    )

    rain.compute()
    # takes an hour
    write_to_disk(
        ds=rain, outdir=outdir, param=param, freq="weekly", start_year=start_year
    )


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
    parser.add_argument("--start-year", type=int, default=2000)

    args = parser.parse_args()
    main(args)
