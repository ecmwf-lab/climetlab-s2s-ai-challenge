from . import CLASSES, DATA_VERSION


def dataset(format="grib", origin="ecmwf", fctype="forecast", version=DATA_VERSION):
    return CLASSES[format](
        origin=origin, version=version, dataset="forecast-input", fctype=fctype
    )
