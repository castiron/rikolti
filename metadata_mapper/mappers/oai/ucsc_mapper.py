from .oai_mapper import OaiRecord, OaiVernacular


class UcscRecord(OaiRecord):

    def UCLDC_map(self):
        return {
            'is_shown_at': self.source_metadata.get('isShownAt'),
            'is_shown_by': self.source_metadata.get('isShownBy')
        }


class UcscVernacular(OaiVernacular):
    record_cls = UcscRecord
