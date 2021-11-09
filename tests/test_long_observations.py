import climetlab as cml

# import pytest


def test_observations_merged():
    cmlds = cml.load_dataset(
        "s2s-ai-challenge-observations",
        parameter=["pr", "t2m"],
    )
    ds = cmlds.to_xarray()
    print(ds)


def test_observations():
    for p in ["pr", "t2m"]:
        cmlds = cml.load_dataset(
            "s2s-ai-challenge-observations",
            parameter=p,
        )
        ds = cmlds.to_xarray()
        print(ds)


def test_observations_720x360():
    cmlds = cml.load_dataset("s2s-ai-challenge-observations", parameter="pr", grid="720x360")
    ds = cmlds.to_xarray()
    cmlds = cml.load_dataset("s2s-ai-challenge-observations", parameter="t2m", grid="720x360")
    ds = cmlds.to_xarray()
    print(ds)


# @pytest.mark.skipif(True, reason="Disabled because it needs a lot of memory")
def test_observations_720x360_merged_1():
    cmlds = cml.load_dataset("s2s-ai-challenge-observations", parameter=["pr", "t2m"], grid="720x360")
    ds = cmlds.to_xarray()
    print(ds)


# @pytest.mark.skipif(True, reason="Disabled because it needs a lot of memory")
def test_observations_720x360_merged_2():
    cmlds = cml.load_dataset("s2s-ai-challenge-observations", grid="720x360")
    ds = cmlds.to_xarray()
    print(ds)
