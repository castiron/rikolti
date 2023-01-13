from typing import Union

from .oai_mapper import OaiRecord, OaiVernacular


class CcaVaultRecord(OaiRecord):

    def UCLDC_map(self) -> dict:
        return {
            "subject": self.map_subject()
        }

    def map_is_shown_at(self) -> Union[str, None]:
        return self.transform_identifier()

    def map_is_shown_by(self) -> Union[str, None]:
        if "type" in self.source_metadata:
            if self.source_metadata.get("type", [])[0].lower() == "image":
                base_url: str = self.transform_identifier()
                return f"{base_url.replace('items', 'thumbs')}?gallery=preview"


    def transform_identifier(self) -> Union[str, None]:
        identifier: list[str] = self.source_metadata.get("identifier")
        return identifier[0] if identifier else None


class CcaVaultVernacular(OaiVernacular):
    record_cls = CcaVaultRecord
