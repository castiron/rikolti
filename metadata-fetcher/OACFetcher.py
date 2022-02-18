import json
import requests
from xml.etree import ElementTree
import xmltodict


from Fetcher import Fetcher, FetchError

import os
TOKEN = os.environ['NUXEO']
CONTENT_SERVER = 'http://content.cdlib.org/'


class OACFetcher(Fetcher):
    # params['oac'] = {
    #     "url": "http://dsc.cdlib.org/search?facet=type-tab&style=cui&raw=1&relation=ark:/13030/kt28702559",
    #     "counts": {
    #         "total": 145,
    #         "image": 128,
    #         "text": 17,
    #         "harvested": 0,
    #         "harvested_image": 100,
    #         "harvested_text": 0
    #     },
    #     "current_group": "image"
    # }
    def __init__(self, params):
        super(OACFetcher, self).__init__(params)
        self.oac = params.get('oac')

        url = self.oac.get('url')
        counts = self.oac.get('counts')
        current_group = self.oac.get('current_group')

        if not counts and not current_group:
            response = requests.get(f'{url}&docsPerPage=0')
            response.raise_for_status()
            initial_response = ElementTree.fromstring(response.content)

            total = initial_response.find('facet')
            image_group = initial_response.find('facet/group[@value="image"]')
            text_group = initial_response.find('facet/group[@value="text"]')

            # https://stackoverflow.com/questions/20129996/why-does-boolxml-etree-elementtree-element-evaluate-to-false
            counts = {
                'total': total.attrib['totalDocs'] if total else 0,
                'image': int(image_group.attrib['totalDocs']) 
                if image_group is not None else 0,
                'text': int(text_group.attrib['totalDocs']) 
                if text_group is not None else 0,
                'harvested': 0,
                'harvested_image': 0,
                'harvested_text': 0
            }
            current_group = None
            if counts['image'] > 0:
                current_group = 'image'
            elif counts['text'] > 0:
                current_group = 'text'

            self.oac['counts'] = counts
            self.oac['current_group'] = current_group

    def build_fetch_request(self):
        url = self.oac.get('url')
        current_group = self.oac.get('current_group')
        harvested = self.oac.get('counts')[f'harvested_{current_group}']

        request = {"url": (
            f"{url}&docsPerPage=100"
            f"&startDoc={harvested+1}"
            f"&group={current_group}"
        )}
        print(
            f"Fetching page "
            f"at {request.get('url')}")

        return request

    def get_records(self, http_resp):
        response = ElementTree.fromstring(http_resp.content)
        doc_hits = (response.find('facet')
                            .findall('./group/docHit'))

        documents = []
        for doc_hit in doc_hits:
            doc_xml = doc_hit.find('meta')
            document = xmltodict.parse(
                ElementTree.tostring(doc_xml))['meta']
            document['calisphere-id'] = self.build_id(doc_xml)
            documents.append(document)

        return documents

    def build_id(self, document):
        '''Return the object's ark from the xml etree docHit'''
        ids = document.findall('identifier')
        ark = None
        for i in ids:
            if i.attrib.get('q', None) != 'local':
                try:
                    split = i.text.split('ark:')
                except AttributeError:
                    continue
                if len(split) > 1:
                    ark = ''.join(('ark:', split[1]))
        return f"{self.collection_id}--{ark}"

    def increment(self, http_resp):
        super(OACFetcher, self).increment(http_resp)

        response = ElementTree.fromstring(http_resp.content)
        current_group = self.oac.get('current_group')
        counts = self.oac.get('counts')

        group = response.find(f'facet/group[@value="{current_group}"]')
        counts[f'harvested_{current_group}'] = int(group.attrib['endDoc'])

        if counts[f'harvested_{current_group}'] >= counts[current_group]:
            if current_group == 'image':
                self.oac['current_group'] = 'text'
            else:
                self.oac['current_group'] = None

        return

    def json(self):
        if not self.oac.get('current_group'):
            return None

        return json.dumps({
            "harvest_type": self.harvest_type,
            "collection_id": self.collection_id,
            "write_page": self.write_page,
            "oac": self.oac
        })
