#!/usr/bin/env python3

import json
import time
from itertools import product

import pandas as pd
import requests

VERSION = "0.1.43"

URL = "https://storage.ecmwf.europeanweather.cloud"
DATA = "s2s-ai-competition/data"

PATTERN = (
    "{URL}/{DATA}/{dataset}-{fctype}-{origin}/{VERSION}/grib/{parameter}-{date}.grib"
)

DATASET = (
    "training-set",
    "reference-set",
)
ORIGIN = (
    "ecmf",
    "kwbc",
    "cwao",
)

FCTYPE = (
    "forecast",
    "hindcast",
)

PARAMETER = ("2t", "tp")

DATES = [
    d.strftime("%Y%m%d") for d in pd.date_range(start="2020-01-01", end="2020-12-31")
]

avail = []

for origin, dataset, fctype, parameter, date in product(
    ORIGIN, DATASET, FCTYPE, PARAMETER, DATES
):
    url = PATTERN.format(**locals())
    print(url)
    while True:
        try:
            r = requests.head(url)
            break
        except Exception as e:
            print(e)
            time.sleep(10)
    if r.status_code == 200:
        avail.append(
            dict(
                origin=origin,
                dataset=dataset,
                fctype=fctype,
                parameter=parameter,
                date=date,
            )
        )
        with open("availability.json", "wt") as f:
            print(json.dumps(avail, indent=4, sort_keys=True), file=f)
