import os

import climetlab as cml

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
