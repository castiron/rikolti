from typing import Union

from .oai_mapper import OaiRecord, OaiVernacular

class ChapmanOaiDcRecord(OaiRecord):

    class ChapmanOaiDcWorking(whatever):
        def working_identifier(self):
            if "identifier" not in self.source_metadata:
                return

            return [i for i in self.source_metadata.get('identifier') if "context" not in i]


    def map_is_shown_at(self) -> Union[str, None]:
        identifier: list[str] = self.working_metadata.get("identifier")
        return identifier[0] if identifier else None

    def map_is_shown_by(self) -> Union[str, None]:
        if "type" not in self.working_metadata: # Need to implement this dictionary interface
            return

        if self.source_metadata.get("type", [])[0].lower() == "image":
            base_url: str = self.working_metadata.get("identifier")[0]
            return f"{base_url.replace('items', 'thumbs')}?gallery=preview"

    def map_description(self):
        if 'description' not in self.working_metadata:
            return

        descriptions = self.working_metadata.get('description')
        return [d for d in descriptions if 'thumbnail' not in d]


class ChapmanOaiDcVernacular(OaiVernacular):
    record_cls = ChapmanOaiDcRecord