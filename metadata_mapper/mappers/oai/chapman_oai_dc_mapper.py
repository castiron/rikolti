from typing import Union

from .oai_mapper import OaiRecord, OaiVernacular

class ChapmanOaiDcRecord(OaiRecord):
    @property
    def is_shown_at(self) -> Union[str, None]:
        return self.identifier_for_image

    @property
    def is_shown_by(self) -> Union[str, None]:
        if not self.is_image_type():
            return

        url: Union[str, None] = self.identifier_for_image

        return f"{url.replace('items', 'thumbs')}?gallery=preview" if url else None

    @property
    def description(self) -> Union[str, None]:
        if 'description' not in self.source_metadata:
            return

        return [d for d in self.source_metadata.get('description') if 'thumbnail' not in d]

    @property
    def identifier_for_image(self) -> Union[str, None]:
        if "identifier" not in self.source_metadata:
            return

        identifiers = [i for i in self.source_metadata.get('identifier') if "context" not in i]
        return identifiers[0] if identifiers else None

    def is_image_type(self) -> bool:
        if "type" not in self.source_metadata:
            return False

        type: list[str] = self.source_metadata.get("type", [])

        return type and type[0].lower() == "image"

class ChapmanOaiDcVernacular(OaiVernacular):
    record_cls = ChapmanOaiDcRecord