from typing import Iterable

from etl.models import FilmWork


class FilmWorkTransformer:
    """Обрабатывает сырые данные из PostgreSQL и преобразовывает их в формат, пригодный для записи Elasticsearch."""

    @staticmethod
    def transform(data: Iterable):
        results = []
        for item in data:
            for field in ("genres", "directors", "actors", "writers"):
                item[f"{field}_names"] = [g["name"] for g in item[field]]
            results.append(FilmWork(**item))

        return results
