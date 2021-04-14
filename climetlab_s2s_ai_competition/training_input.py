from . import CLASSES, DATA_VERSION


def dataset(format="grib", origin="ecmwf", fctype="hindcast", version=DATA_VERSION):
    return CLASSES[format](
        origin=origin, version=version, dataset="training-input", fctype=fctype
    )
