import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
from tld import get_tld
from collections import OrderedDict
from requests.auth import HTTPBasicAuth


class URL:

    def __init__(self, url=None, login=None, password=None, offer_selector='offer', picture_selector='picture'):
        self._url = url
        self._login = login
        self._password = password
        self._offer_selector = offer_selector
        self._picture_selector = picture_selector

    @property
    def url(self):
        return self._url

    @property
    def offer_selector(self):
        return self._offer_selector

    @property
    def picture_selector(self):
        return self._picture_selector

    @property
    def login(self):
        return self._login

    @property
    def password(self):
        return self._password

    @property
    def auth_required(self):
        return not ((self._login is None) or (self.password is None))

    @property
    def auth(self):
        if self.auth_required:
            return HTTPBasicAuth(self._login, self._password)
        else:
            return None


def decode_content(raw_content):
    try:
        # CP1251
        return raw_content.decode('cp1251').encode('utf8').decode('utf8')
    except UnicodeDecodeError:
        # UTF-8
        try:
            return raw_content.decode('utf8')
        except UnicodeDecodeError:
            return raw_content.decode('latin-1').encode('utf-8')


def serialize_offer(el, picture_selector):
    instance = OrderedDict()
    instance.update(el.attrib)
    for node in el.getchildren():
        tag = node.tag
        if tag == 'param':
            column = ' '.join(list(node.attrib.values())[::-1])
            value = node.text
        elif tag == picture_selector:
            column = tag
            value = node.text
            if tag in instance.keys():
                old_value = instance[column]
                value = '{0}#{1}'.format(old_value, value)
        else:
            column = tag
            value = node.text
        instance[column] = value
    return instance


def get_content(url, auth=None):
    response = requests.get(url, auth=auth)
    content = decode_content(response.content)
    return content


def get_xlsx(url, output_dir='../data'):

    offer_selector = './/{0}'.format(url.offer_selector)
    picture_selector = url.picture_selector

    content = get_content(url.url, url.auth)
    root = ET.fromstring(content)
    offers = []
    for el in root.findall(offer_selector):
        offer = serialize_offer(el, picture_selector)
        offers.append(offer)
    df = pd.DataFrame(offers)
    sitename = get_tld(url.url)
    writer = pd.ExcelWriter('{0}/{1}.xlsx'.format(output_dir, sitename), options={'strings_to_urls': False})
    df.to_excel(writer, 'Sheet')
    writer.save()
