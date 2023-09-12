# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def s2s_availability_parser(v):
    # do not use date in availability because type='date-list' and availability are not yet implemented in climetlab
    # if "alldates" in v:
    #     dates = list(pd.date_range(**v["alldates"]))
    #     # v["date"] = dates
    #     # v["date"] = [d.strftime("%Y%m%d") for d in dates]

    #     # v["alldates"] = v["alldates"]["start"] + "/" + v["alldates"]["end"]

    if "number" in v:
        s, _, e = v["number"].split("/")
        v["number"] = [x for x in range(int(s), int(e) + 1)]

    if "param" in v:
        aliases = {"2t": "t2m", "ci": "siconc"}
        v["parameter"] = [aliases.get(p, p) for p in v["param"]] + ["ALL"]

    for remove in [
        "grid",
        "stream",
        "step",
        "stepintervals",
        "level",
        "levelbis",
        "param",
        "alldates",
    ]:
        v.pop(remove, None)

    return v
