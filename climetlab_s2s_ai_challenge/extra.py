import warnings

import pandas as pd
import xarray as xr


def create_valid_time_from_forecast_time_and_lead_time(inits, leads):
    """Take forecast_time and add lead_time into the future creating two-dimensional
    valid_time."""
    inits = xr.DataArray(
        inits,
        dims="forecast_time",
        coords={"forecast_time": inits},
    )
    valid_times = xr.concat(
        [
            xr.DataArray(
                inits + x,
                dims="forecast_time",
                coords={"forecast_time": inits},
            )
            for x in leads
        ],
        "lead_time",
    )
    valid_times = valid_times.assign_coords(lead_time=leads)
    return valid_times.rename("valid_time")


def create_lead_time_and_forecast_time_from_time(forecast, obs_time):
    """Create observation with dimensions forecast_time and lead_time and valid_time
    coordinate from observations with time dimension"""
    if "valid_time" not in forecast.coords or "valid_time" in forecast.dims:
        raise ValueError("expect valid_time coords and not as dim")
    if "time" not in obs_time.dims:
        raise ValueError("expect time as dim in obs_time")
    # cannot be lazy dask
    forecast["valid_time"] = forecast["valid_time"].compute()
    obs_lead_init = obs_time.rename({"time": "valid_time"}).sel(valid_time=forecast.valid_time)
    return obs_lead_init


def forecast_like_observations(forecast, obs_time):
    """Create observation with dimensions `forecast_time` and `lead_time` and
    `valid_time` coordinate from observations with `time` dimension
    while accumulating precipitation_flux `pr` to precipitation_amount `tp`.

    Note that the newly created output follows the ECMWF S2S convention:
    - `tp`:
        * accumulated for each day from the beginning of the forecast
        * `lead_time = 1 days` accumulates precipitation_flux `pr` from hourly
          steps 0-24 at `forecast_time`, 0 days = 0 (no `tp`) by definition,
          i.e. `lead_time` defines the end of the end of the aggregation period.
        * week 3-4: day 28 minus day 14
        * week 5-6: day 42 minus day 28
        * https://confluence.ecmwf.int/display/S2S/S2S+Total+Precipitation
    - `t2m`:
        * averaged each day
        * `lead_time = 0 days` averages daily from hourly steps 0-24,
          i.e. averaging conditions over the day of `forecast_time`
        * week 3-4: average [day 14, day 27]
        * week 5-6: average [day 28, day 41]
        * https://confluence.ecmwf.int/display/S2S/S2S+Surface+Air+Temperature


    Args:
        forecast (xr.DataArray, xr.Dataset): initialized forecast with `lead_time`
            (continuous with daily strides for `tp`) and `forecast_time` dimension and
            `valid_time` coordinate
        obs_time (xr.Dataset): observations with `time` dimension

    Return:
        xr.Dataset: observations with `lead_time` and `forecast_time` dimension and
            `valid_time` coordinate for data_vars from obs_time. Converts `pr` to `tp`.
            All other variables are not aggregated.

    Example:
        >>> import climetlab as cml
        >>> forecast = cml.load_dataset('s2s-ai-challenge-training-input',
        ...     date=20100107, origin='ncep', parameter='tp',
        ...     format='netcdf').to_xarray()
        >>> obs_lead_forecast_time = cml.load_dataset('s2s-ai-challenge-observations',
        ...     parameter=['pr', 't2m']).to_xarray(like=forecast)
        >>> obs_lead_forecast_time
        <xarray.Dataset>
        Dimensions:        (forecast_time: 12, latitude: 121, lead_time: 44,
                            longitude: 240, realization: 4)
        Coordinates:
          * realization    (realization) int64 0 1 2 3
          * forecast_time  (forecast_time) datetime64[ns] 1999-01-07 ... 2010-01-07
          * lead_time      (lead_time) timedelta64[ns] 1 days 2 days ... 43 days 44 days
          * latitude       (latitude) float64 90.0 88.5 87.0 85.5 ... -87.0 -88.5 -90.0
          * longitude      (longitude) float64 0.0 1.5 3.0 4.5 ... 355.5 357.0 358.5
            valid_time     (forecast_time, lead_time) datetime64[ns]
        Data variables:
            tp             (realization, forecast_time, lead_time, latitude, longitude)
            t2m            (realization, forecast_time, lead_time, latitude, longitude)

        Or explicitly with the function `forecast_like_observations`

        >>> from climetlab_s2s_ai_challenge.extra import forecast_like_observations
        >>> forecast = cml.load_dataset('s2s-ai-challenge-training-input',
        ...     date=20100107, origin='ncep', parameter='tp',
        ...     format='netcdf').to_xarray()
        >>> obs_time = cml.load_dataset('s2s-ai-challenge-observations',
        ...     parameter=['pr', 't2m']).to_xarray()
        >>> obs_lead_time_forecast_time = forecast_like_observations(forecast, obs_time)
        >>> obs_lead_time_forecast_time
        <xarray.Dataset>
        Dimensions:        (forecast_time: 12, latitude: 121, lead_time: 44,
                            longitude: 240, realization: 4)
        Coordinates:
          * realization    (realization) int64 0 1 2 3
          * forecast_time  (forecast_time) datetime64[ns] 1999-01-07 ... 2010-01-07
          * lead_time      (lead_time) timedelta64[ns] 1 days 2 days ... 43 days 44 days
          * latitude       (latitude) float64 90.0 88.5 87.0 85.5 ... -87.0 -88.5 -90.0
          * longitude      (longitude) float64 0.0 1.5 3.0 4.5 ... 355.5 357.0 358.5
            valid_time     (forecast_time, lead_time) datetime64[ns]
        Data variables:
            tp             (realization, forecast_time, lead_time, latitude, longitude)
            t2m            (realization, forecast_time, lead_time, latitude, longitude)
    """
    assert isinstance(obs_time, xr.Dataset)

    obs_lead_init = create_lead_time_and_forecast_time_from_time(forecast, obs_time)
    # cumsum pr into tp
    if "pr" in obs_time.data_vars:
        forecast_lead_strides = forecast.lead_time.diff("lead_time").to_index()
        if forecast_lead_strides.mean() != pd.Timedelta("1 days") or forecast_lead_strides.std() != pd.Timedelta(
            "0 days"
        ):
            warnings.warn(
                "function `forecast_like_observations(forecast, obs_time)` expects "
                "equal daily stides in `forecast.lead_time`, "
                f"found strides {forecast_lead_strides} in {forecast.lead_time}"
            )
        obs_lead_init_tp = (obs_lead_init[["pr"]].cumsum("lead_time", keep_attrs=True, skipna=True)).rename(
            {"pr": "tp"}
        )
        # mask all NaNs - cannot do cumsum(skipna=False) because then all grid cells get NaNs (related to leap days?)
        obs_lead_init_tp["tp"] = obs_lead_init_tp["tp"].where(~obs_time["pr"].isnull().all("time"))
        # shift valid_time and lead_time one unit forward as
        # pr describes observed precipitation_flux at given date, e.g. Jan 01
        # tp describes observed precipitation_amount, e.g. Jan 01 00:00 to Jan 01 23:59
        # therefore labeled by the end of the period Jan 02
        shift = forecast_lead_strides.mean()
        obs_lead_init_tp = obs_lead_init_tp.assign_coords(valid_time=forecast.valid_time + shift).assign_coords(
            lead_time=forecast.lead_time + shift
        )
        del obs_lead_init["pr"]
        # lead_time 0 days tp stays all NaNs
        obs_lead_init["tp"] = obs_lead_init_tp["tp"]
        # add attrs
        obs_lead_init["tp"].attrs.update(
            {
                "units": "kg m-2",
                "standard_name": "precipitation_amount",
                "long_name": "total precipitation",
                "aggregation": "precipitation_flux `pr` is accumulated daily from "
                + "`forecast_time` up to the date of `valid_time` "
                + "(but not including the `valid_time` date) over `lead_time`",
            }
        )
    # add Dataset metadata
    obs_lead_init.attrs.update({"function": "climetlab_s2s_ai_challenge.extra.forecast_like_observations"})
    return obs_lead_init
