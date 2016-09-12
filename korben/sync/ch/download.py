from lxml import etree
import requests
from . import constants

def urls():
    resp = requests.get(constants.DOWNLOAD_URL)
    import ipdb;ipdb.set_trace()

