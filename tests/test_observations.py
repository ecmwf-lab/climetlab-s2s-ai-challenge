import os

import climetlab as cml
import numpy as np
import xarray as xr

if os.environ.get("TEST_FAST"):
    is_test = "-dev"  # short tests
else:
    is_test = ""  # long tests


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
        date=[20200102, 20200109],
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
        parameter="2t",
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


def test_create_lead_time_and_forecast_time_from_time():
    import pandas as pd

    from climetlab_s2s_ai_challenge.scripts import (
        create_lead_time_and_forecast_time_from_time,
        forecast_like_observations,
    )

    n_time = 100
    time = np.arange(n_time)
    time_coord = pd.date_range(start="2000", freq="1D", periods=n_time)
    ds_time = xr.DataArray(time, dims="time", coords={"time": time_coord})

    forecast = ds_time.rename({"time": "forecast_time"})[:10]
    i_time = 10
    init_coord = pd.date_range(start="2000", freq="W-THU", periods=i_time)
    inits = xr.DataArray(np.arange(i_time), dims="forecast_time", coords={"forecast_time": init_coord})

    leads = [pd.Timedelta(f"{d} d") for d in range(10)]
    valid_times = xr.concat(
        [
            xr.DataArray(
                inits.forecast_time + pd.Timedelta(f"{x} d"),
                dims="forecast_time",
                coords={"forecast_time": inits.forecast_time},
            )
            for x in range(len(leads))
        ],
        "lead_time",
    )

    assert "lead_time" in valid_times.dims
    assert "forecast_time" in valid_times.dims
    # print(valid_times)

    forecast = xr.DataArray(
        ds_time.values.reshape(10, 10),
        dims=["forecast_time", "lead_time"],
        coords={"forecast_time": valid_times.forecast_time, "lead_time": valid_times.lead_time},
    )
    forecast = forecast.assign_coords(valid_time=valid_times)

    # print(forecast.coords)
    # print(forecast.valid_time)
    # print(ds_time.coords)

    ds_lead_init = create_lead_time_and_forecast_time_from_time(forecast, ds_time)

    for d in ["lead_time", "forecast_time"]:
        assert d in ds_lead_init.dims

    obs_lead_init = forecast_like_observations(forecast.to_dataset(name="pr"), ds_time.to_dataset(name="pr"))
    assert "tp" in obs_lead_init.data_vars
    assert "pr" not in obs_lead_init.data_vars
