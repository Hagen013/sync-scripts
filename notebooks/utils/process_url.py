import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
from tld import get_tld
from collections import OrderedDict

def decode_content(raw_content):
    try:
        # CP1251
        return raw_content.decode('cp1251').encode('utf8').decode('utf8')
    except UnicodeDecodeError:
        # UTF-8
        return raw_content.decode('utf8')


def serialize_offer(el):
    instance = OrderedDict()
    instance.update(el.attrib)
    for node in el.getchildren():
        tag = node.tag
        if tag == 'param':
            column = ' '.join(list(node.attrib.values())[::-1])
            value = node.text
        else:
            column = tag
            value = node.text
        instance[column] = value
    return instance


def get_content(url):
    response = requests.get(url)
    content = decode_content(response.content)
    return content


def process_url(url, output_dir='../data'):
    content = get_content(url)
    root = ET.fromstring(content)
    offers = []
    for el in root.findall('.//offer'):
        offer = serialize_offer(el)
        offers.append(offer)
    df = pd.DataFrame(offers)
    sitename = get_tld(url)
    writer = pd.ExcelWriter('{0}/{1}.xlsx'.format(output_dir, sitename))
    df.to_excel(writer, 'Sheet')
    writer.save()