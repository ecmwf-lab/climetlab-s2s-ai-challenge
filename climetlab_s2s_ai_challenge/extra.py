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
    """Create observation with dimensions forecast_time and lead_time and valid_time
    coordinate from observations with time dimension
    while accumulating precipitation_flux `pr` to precipitation_amount `tp`.

    Args:
        forecast (xr.Dataset): initialized forecast with `lead_time` and
            `forecast_time` dimension and `valid_time` coordinate
        obs_time (xr.Dataset): observations with `time` dimension and same variables as
            forecast

    Return:
        xr.Dataset: observations with `lead_time` and `forecast_time` dimension and
            `valid_time` coordinate

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
        >>> obs_ds = cml.load_dataset('s2s-ai-challenge-observations',
        ...     parameter=['pr', 't2m']).to_xarray()
        >>> obs_lead_time_forecast_time = forecast_like_observations(forecast, obs_ds)
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
    assert isinstance(forecast, xr.Dataset)
    assert isinstance(obs_time, xr.Dataset)

    obs_lead_init = create_lead_time_and_forecast_time_from_time(forecast, obs_time)

    # cumsum pr into tp
    if "pr" in obs_lead_init.data_vars:
        obs_lead_init["tp"] = (
            obs_lead_init["pr"]
            .cumsum("lead_time", keep_attrs=True, skipna=False)
            .assign_coords(lead_time=obs_lead_init.lead_time)
            .assign_coords(valid_time=obs_lead_init.valid_time)
        )
        del obs_lead_init["pr"]
        # add attrs
        obs_lead_init["tp"].attrs.update(
            {"units": "kg m-2", "standard_name": "precipitation_amount", "long_name": "total precipitation"}
        )
    # add Dataset metadata
    obs_lead_init.attrs.update({"script": "climetlab_s2s_ai_challenge.extra.forecast_like_observations"})
    return obs_lead_init
