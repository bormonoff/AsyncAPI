from etl.extractors.base import BaseExtractor


class PersonExtractor(BaseExtractor):
    TABLE_NAME = "person"
    MAIN_TABLE = False
