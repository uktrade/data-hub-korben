import io
import os
import urllib
import zipfile

from lxml import etree
import requests

from korben.services import redis_bytes
from . import constants
from .. import utils as sync_utils


def filenames():
    'Get currently offered filenames from CH'
    resp = requests.get(constants.DOWNLOAD_URL)
    parser = etree.HTMLParser()
    root = etree.parse(io.BytesIO(resp.content), parser).getroot()
    retval = []
    for anchor in root.cssselect('.omega a'):
        retval.append(anchor.attrib['href'])
    return retval


def zips(names):
    'Download zip files from CH with caching'
    base_url = urllib.parse.urlparse(constants.DOWNLOAD_URL)
    retval = []
    for name in names:
        cache_path = sync_utils.file_leaf(
            constants.CACHE_PATH, 'ch', 'zip', name
        )
        if zipfile.is_zipfile(cache_path):
            retval.append(cache_path)
            continue
        zip_url = "{0.scheme}://{0.hostname}/{1}".format(base_url, name)
        zip_resp = requests.get(zip_url)
        redis_bytes.set(cache_path, zip_resp.content)
        retval.append(cache_path)
    return retval


def extract(zip_paths):
    'Extract first file from each of the passed paths (to zip files)'
    csv_paths = []
    for zip_path in zip_paths:
        downloaded_file = io.BytesIO(redis_bytes.get(zip_path))
        with zipfile.ZipFile(downloaded_file) as zf_cache_check:
            name = zf_cache_check.filelist[0].filename
        csv_path = sync_utils.file_leaf(
            constants.CACHE_PATH, 'ch', 'csv', name
        )
        if redis_bytes.get(csv_path):  # assume that if it exists all is well
            csv_paths.append(csv_path)
            continue
        with zipfile.ZipFile(downloaded_file) as zf_extract:
            file_bytes = zf_extract.read(name)
            redis_bytes.set(csv_path, file_bytes)
            csv_paths.append(csv_path)
    return csv_paths
