import os

import climetlab as cml

if os.environ.get("TEST_FAST"):
    is_test = "-dev"  # short tests
    PARAMS = ["2t", "t2m"]
else:
    is_test = ""  # long tests
    PARAMS = ["2t", "t2m", "tp"]

WEEKS = ["34", "56"]


def test_benchmark():
    cml.load_dataset(
        "s2s-ai-challenge-test-output-benchmark",
        parameter=PARAMS,
        weeks=WEEKS,
    ).to_xarray()


def test_benchmark_2():
    for p in PARAMS:
        for w in WEEKS:
            cml.load_dataset(
                "s2s-ai-challenge-test-output-benchmark",
                parameter=p,
                weeks=w,
            ).to_xarray()
            cml.load_dataset(
                "s2s-ai-challenge-test-output-benchmark",
                parameter=[p],
                weeks=[w],
            ).to_xarray()


# def test_benchmark_one_date():
#     for p in ['2t', 't2m', 'tp']:
#         for w in ['34','56']:
#             cml.load_dataset("s2s-ai-challenge-test-output-benchmark",
#                         parameter=p,
#                         weeks=w,
#                         date='20200102',
#                        ).to_xarray()
#
# def test_benchmark_two_dates():
#     for p in ['2t', 't2m', 'tp']:
#         for w in ['34','56']:
#             cml.load_dataset("s2s-ai-challenge-test-output-benchmark",
#                         parameter=p,
#                         weeks=w,
#                         date=['20200102','20200109']
#                        ).to_xarray()
