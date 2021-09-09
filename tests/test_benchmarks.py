import os

import climetlab as cml

if os.environ.get("TEST_FAST"):
    is_test = "-dev"  # short tests
    PARAMS = ["t2m"]
else:
    is_test = ""  # long tests
    PARAMS = ["t2m", "tp"]


def test_benchmark_2():
    for p in PARAMS:
        cml.load_dataset(
            "s2s-ai-challenge-test-output-benchmark",
            parameter=p,
        ).to_xarray()
        cml.load_dataset("s2s-ai-challenge-test-output-benchmark", parameter=[p]).to_xarray()
