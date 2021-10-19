import climetlab as cml
import numpy as np
import xarray as xr


def test_test_get_rain_obs():

    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date=20200312,
        parameter="tp",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_test_get_rain_obs_2():

    cmlds = cml.load_dataset(
        "s2s-ai-challenge-training-output-reference",
        date=[20200102, 20200312],
        parameter="tp",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_train_get_rain_obs():
    cmlds = cml.load_dataset(
        "s2s-ai-challenge-training-output-reference",
        date=20200312,
        parameter="tp",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_test_get_t2m_obs():

    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date=20200312,
        parameter="t2m",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_test_get_t2m_obs_2():
    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date=20200312,
        parameter="t2m",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_test_get_t2m_obs_3():
    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date="2020-03-12",
        parameter="t2m",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_train_get_t2m_obs():
    cmlds = cml.load_dataset(
        "s2s-ai-challenge-training-output-reference",
        date=20200312,
        parameter="t2m",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_get_obs():

    cmlds = cml.load_dataset(
        "s2s-ai-challenge-test-output-reference",
        date=20200312,
        parameter="t2m",
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_forecast_like_observations_script():
    """Create synthetic observations object with time dim
    and forecast object with lead_time and forecast_time,
    to create observation with forecast_time and lead_time
    while accumulating pr to tp.
    """
    import pandas as pd

    from climetlab_s2s_ai_challenge.extra import (
        create_lead_time_and_forecast_time_from_time,
        create_valid_time_from_forecast_time_and_lead_time,
        forecast_like_observations,
    )

    # create obs with time dimension
    n_time = 100
    time = np.arange(n_time)
    time_coord = pd.date_range(start="2000", freq="1D", periods=n_time)
    ds_time = xr.DataArray(time, dims="time", coords={"time": time_coord})

    # create valid_time
    i_time = 10
    init_coord = pd.date_range(start="2000", freq="W-THU", periods=i_time)
    inits = xr.DataArray(np.arange(i_time), dims="forecast_time", coords={"forecast_time": init_coord})
    leads = [pd.Timedelta(f"{d} d") for d in range(10)]
    valid_times = create_valid_time_from_forecast_time_and_lead_time(inits.forecast_time, leads)
    assert "lead_time" in valid_times.dims
    assert "forecast_time" in valid_times.dims

    # create a forecast with 10 forecast_time and 10 lead_time and add valid_time
    forecast = xr.DataArray(
        ds_time.values.reshape(10, 10),
        dims=["forecast_time", "lead_time"],
        coords={"forecast_time": valid_times.forecast_time, "lead_time": valid_times.lead_time},
    )
    forecast = forecast.assign_coords(valid_time=valid_times)

    # add dimensions lead_time and forecast_time from dim time
    ds_lead_init = create_lead_time_and_forecast_time_from_time(forecast, ds_time)

    for d in ["lead_time", "forecast_time"]:
        assert d in ds_lead_init.dims

    # promote to dataset
    forecast = forecast.to_dataset(name="pr")
    forecast["t2m"] = forecast["pr"]
    ds_time = ds_time.to_dataset(name="pr")
    ds_time["t2m"] = ds_time["pr"]

    # testing forecast_like_observations
    obs_lead_init = forecast_like_observations(forecast, ds_time)
    assert "tp" in obs_lead_init.data_vars
    assert "pr" not in obs_lead_init.data_vars
    assert not obs_lead_init["tp"].identical(obs_lead_init["t2m"])
    assert obs_lead_init["tp"].attrs["standard_name"] == "precipitation_amount"
