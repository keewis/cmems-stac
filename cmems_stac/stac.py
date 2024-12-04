from functools import singledispatch
from urllib.parse import urlsplit, urlunsplit

import pystac
import xarray as xr


def split_href(url):
    fragments = urlsplit(url)

    new_url = f"s3://{fragments.path.lstrip('/')}"
    endpoint_url = urlunsplit((fragments.scheme, fragments.netloc, "", "", ""))

    return new_url, endpoint_url


def detect_engine(asset):
    match asset.media_type:
        case "application/vnd+zarr":
            engine = "zarr"
        case "application/x-netcdf":
            engine = "h5netcdf"
        case _:
            raise ValueError(f"unknown media type: {asset.media_type}")

    return engine


def open_asset(asset, *, storage_options=None, **kwargs):
    if storage_options is None:
        storage_options = {}

    url, endpoint_url = split_href(asset.href)

    so = {"endpoint_url": endpoint_url, "anon": True} | storage_options

    additional_kwargs = asset.extra_fields.get("xarray:open_kwargs", {})
    open_kwargs = {"engine": detect_engine(asset)} | additional_kwargs

    return xr.open_dataset(url, storage_options=so, **open_kwargs, **kwargs)


@singledispatch
def open_stac(value, **kwargs):
    pass


@open_stac.register
def _(item: pystac.Item, name):
    asset = item.assets.get(name)
    if asset is None:
        raise ValueError(f"unknown asset: {name}")

    return open_asset(asset)


@open_stac.register
def _(asset: pystac.Asset):
    return open_asset(asset)
