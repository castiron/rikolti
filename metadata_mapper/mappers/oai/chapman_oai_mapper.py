from typing import Union

from .oai_mapper import OaiRecord, OaiVernacular

class ChapmanOaiDcRecord(OaiRecord):
    cache = {}

    def map_is_shown_at(self) -> Union[str, None]:
        identifier: list[str] = self.source_metadata.get("identifier")
        return identifier[0] if identifier else None

    def map_is_shown_by(self) -> Union[str, None]:
        if "type" not in self.source_metadata:
            return

        if self.source_metadata.get("type", [])[0].lower() == "image":
            base_url: str = self.source_metadata.get("identifier")[0]
            return f"{base_url.replace('items', 'thumbs')}?gallery=preview"

    def map_identifier(self):
        return self.cached_identifier()

    def map_description(self):
        if 'description' in self.provider_data_source:
            descs = getprop(self.provider_data_source, 'description')
            descs_srcRes = []
            for d in descs:
                if 'thumbnail' not in d:
                    descs_srcRes.append(d)
        if descs_srcRes:
            self.update_source_resource({'description': descs_srcRes})

    def cached_identifier(self):
        if hasattr(self.cache, "identifier"):
            return self.cache["identifier"]

        if "identifier" not in self.source_metadata:
            return

        identifiers = self.source_metadata.get('identifier')
        filtered_identifiers = [i for i in identifiers if "context" not in i]

        if filtered_identifiers:
            self.cache["identifier"] = filtered_identifiers
            return filtered_identifiers

class ChapmanOaiDcVernacular(OaiVernacular):
    record_cls = ChapmanOaiDcRecord