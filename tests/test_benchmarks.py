import climetlab as cml

PARAMS = ["t2m", "tp"]


def test_benchmark_1():
    ds = cml.load_dataset("s2s-ai-challenge-test-output-benchmark", parameter=PARAMS)
    print(ds.to_xarray())


def test_benchmark_2():
    for p in PARAMS:
        ds = cml.load_dataset(
            "s2s-ai-challenge-test-output-benchmark",
            parameter=p,
        )
        print(ds.to_xarray())
