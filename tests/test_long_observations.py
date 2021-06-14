import climetlab as cml


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
