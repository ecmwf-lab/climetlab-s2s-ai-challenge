import pandas as pd
import xarray as xr

lm = 47
leads = [pd.Timedelta(f"{d} d") for d in range(lm)]


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


def create_lead_time_and_forecast_time_from_time(forecast, obs_time):
    if "valid_time" not in forecast.coords and "valid_time" not in forecast.dims:
        raise ValueError("expect valid_time coords and not as dim")
    if "time" not in obs_time.dims:
        raise ValueError("expect time as dim in obs_time")
    obs_lead_init = obs_time.rename({"time": "valid_time"}).sel(valid_time=forecast.valid_time)
    return obs_lead_init


def forecast_like_observations(forecast, obs_time):
    assert isinstance(forecast, xr.Dataset)
    assert isinstance(obs_time, xr.Dataset)
    obs_lead_init = create_lead_time_and_forecast_time_from_time(forecast, obs_time)
    if "pr" in obs_lead_init.data_vars:
        obs_lead_init["tp"] = (
            obs_lead_init["pr"]
            .cumsum("lead_time", keep_attrs=True, skipna=False)
            .assign_coords(lead_time=obs_lead_init.lead_time)
            .assign_coords(valid_time=obs_lead_init.valid_time)
        )
        del obs_lead_init["pr"]
        # add attrs
    return obs_lead_init
