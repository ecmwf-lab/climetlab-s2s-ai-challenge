#!/usr/bin/env python
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import io
import os

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding="utf-8").read()


package_name = "climetlab-s2s-ai-challenge"

version = None
init_py = os.path.join(package_name.replace("-", "_"), "__init__.py")
for line in read(init_py).split("\n"):
    if line.startswith("__version__"):
        version = line.split("=")[-1].strip()[1:-1]
assert version


extras_require = {"zarr": ["zarr", "s3fs"]}

setuptools.setup(
    name=package_name,
    version=version,
    description="Climetlab external dataset plugin for the S2S AI competition organised by ECMWF",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="European Centre for Medium-Range Weather Forecasts (ECMWF)",
    author_email="software.support@ecmwf.int",
    license="Apache License Version 2.0",
    url="https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["climetlab<=0.7.4"],
    extras_require=extras_require,
    zip_safe=True,
    entry_points={
        "climetlab.datasets": [
            "s2s-ai-challenge-observations = climetlab_s2s_ai_challenge.observations:RawObservations",
            # Domain style
            "s2s-ai-challenge-hindcast-input = climetlab_s2s_ai_challenge.fields:hindcast_input",
            "s2s-ai-challenge-forecast-input = climetlab_s2s_ai_challenge.fields:forecast_input",
            "s2s-ai-challenge-hindcast-input-dev = climetlab_s2s_ai_challenge.fields:hindcast_input_dev",
            "s2s-ai-challenge-forecast-input-dev = climetlab_s2s_ai_challenge.fields:forecast_input_dev",
            "s2s-ai-challenge-hindcast-like-observations = climetlab_s2s_ai_challenge.observations:HindcastLikeObservations",
            "s2s-ai-challenge-forecast-like-observations = climetlab_s2s_ai_challenge.observations:ForecastLikeObservations",
            "s2s-ai-challenge-hindcast-benchmark = climetlab_s2s_ai_challenge.benchmark:HindcastBenchmark",
            "s2s-ai-challenge-forecast-benchmark = climetlab_s2s_ai_challenge.benchmark:ForecastBenchmark",
            # ML style
            "s2s-ai-challenge-training-input = climetlab_s2s_ai_challenge.fields:training_input",
            "s2s-ai-challenge-test-input = climetlab_s2s_ai_challenge.fields:test_input",
            "s2s-ai-challenge-training-input-dev = climetlab_s2s_ai_challenge.fields:training_input_dev",
            "s2s-ai-challenge-test-input-dev = climetlab_s2s_ai_challenge.fields:test_input_dev",
            "s2s-ai-challenge-training-output-reference = climetlab_s2s_ai_challenge.observations:TrainingOutputReference",  # noqa: E501
            "s2s-ai-challenge-training-output-benchmark = climetlab_s2s_ai_challenge.benchmark:TrainingOutputBenchmark",
            "s2s-ai-challenge-test-output-reference = climetlab_s2s_ai_challenge.observations:TestOutputReference",
            "s2s-ai-challenge-test-output-benchmark = climetlab_s2s_ai_challenge.benchmark:TestOutputBenchmark",
        ]
    },
    keywords="meteorology",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
