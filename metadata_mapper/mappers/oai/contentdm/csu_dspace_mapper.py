from ..contentdm_mapper import ContentdmRecord, ContentdmVernacular
import re
import urllib


class CsuDspaceRecord(ContentdmRecord):
    def UCLDC_map(self):
        return {
            'language': self.source_metadata.get('languageTerm'),
            'subject': self.source_metadata.get('topic'),
            'date': self.source_metadata.get('dateIssued'),
            'creator': self.source_metadata.get('namePart'),
            'type': self.collate_fields(['type', 'genre'])
        }

    def map_is_shown_by(self):
        filenames = [f.lower() for f in filter(None, self.source_metadata.get('originalName'))
                     if not any([x in f.lower() for x in ['.txt', '.doc', '.tif', '.wav', '.mp4']])]

        thumbnail_url = None
        for filename in filenames:
            url_parts = [self.get_baseurl(), self.get_handle() + '/bitstream/handle/',
                         '/', urllib.quote(filename)]

            if '.pdf' in filename:
                url_parts.append('.jpg')

            thumbnail_url = ''.join(url_parts)
        return thumbnail_url

    def map_is_shown_at(self):
        handle = self.get_handle()
        if not handle:
            return

        return ''.join((self.get_baseurl() + '/handle/', handle))

    def get_handle(self):
        values = [re.sub('https?:\/\/hdl\.handle\.net\/', '', h)
                  for h in filter(None, self.source_metadata.get('identifier'))
                  if 'hdl.handle.net' in h]

        if not values:
            return

        return values[-1]

    def get_baseurl(self):
        """
        TODO: try https://
        """
        return 'http://dspace.calstate.edu'


class CsuDspaceVernacular(ContentdmVernacular):
    record_cls = CsuDspaceRecord
