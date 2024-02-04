from typing import Iterable

from etl import models


class PersonTransformer:
    """Обрабатывает сырые данные из PostgreSQL и преобразовывает их в формат, пригодный для записи Elasticsearch."""

    @staticmethod
    def transform(data: Iterable):
        results = []
        for item in data:
            results.append(models.ExtendedPerson(**item))
        return results
