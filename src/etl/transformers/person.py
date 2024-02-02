from typing import Iterable

from etl.models import ExtendedPerson


class PersonTransformer:
    """Обрабатывает сырые данные из PostgreSQL и преобразовывает их в формат, пригодный для записи Elasticsearch."""

    @staticmethod
    def transform(data: Iterable):
        results = []
        for item in data:
            results.append(ExtendedPerson(**item))
        return results
