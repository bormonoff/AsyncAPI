import psycopg2
from psycopg2.extensions import connection as pg_connection

from etl.utils.backoff import backoff


class BaseExtractor:
    """Базовый экстрактор"""

    TABLE_NAME: str
    MAIN_TABLE: bool  # основная таблица или связанная с основной

    def __init__(
        self,
        connection: pg_connection,
        chunk_size: int,
        updated_at: str | None,
        schema: str = "content",
    ):
        self._connection: pg_connection = connection
        self.chunk_size = chunk_size
        self.schema = schema
        self.updated_at = updated_at

    @backoff(psycopg2.DatabaseError)
    def fetch_all(self, query):
        cursor = self._connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def _produce(self) -> list:
        where_str = self.updated_at and f"WHERE updated_at > '{self.updated_at}'" or ""

        query = """
                SELECT id, updated_at
                FROM {schema}.{table}
                {where_str}
                ORDER BY updated_at
                LIMIT {limit}; 
            """.format(
            schema=self.schema,
            table=self.TABLE_NAME,
            where_str=where_str,
            limit=self.chunk_size,
        )

        data = self.fetch_all(query)

        if self.MAIN_TABLE:
            return data
        ids = tuple([i["id"] for i in data])
        if not ids:
            return []

        query = """
            SELECT fw.id, i.updated_at
            FROM {schema}.film_work fw
            LEFT JOIN {schema}.{table}_film_work ifw ON ifw.film_work_id = fw.id
            LEFT JOIN {schema}.{table} i ON i.id = ifw.{table}_id
            WHERE i.id IN {ids}
            ORDER BY i.updated_at; 
        """.format(
            schema=self.schema, table=self.TABLE_NAME, ids=ids
        )

        return self.fetch_all(query)

    def _enrich(self, ids: tuple) -> list:
        query = """
            SELECT 
                fw.id,
                fw.title,
                fw.description,
                fw.rating,
                fw.type,
                fw.created_at,
                fw.updated_at,
                COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'id', g.id,
                           'name', g.name
                       )
                   ) FILTER (WHERE g.id is not null),
                   '[]'
                ) as genres,
                COALESCE(
                   json_agg(
                   DISTINCT jsonb_build_object(
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null AND pfw.role = 'director'),
                   '[]'
                ) as directors,
                COALESCE(
                   json_agg(
                   DISTINCT jsonb_build_object(
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null AND pfw.role = 'actor'),
                   '[]'
                ) as actors,
                COALESCE(
                   json_agg(
                   DISTINCT jsonb_build_object(
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null AND pfw.role = 'writer'),
                   '[]'
                ) as writers
            FROM {schema}.film_work fw
            LEFT JOIN {schema}.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN {schema}.person p ON p.id = pfw.person_id
            LEFT JOIN {schema}.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN {schema}.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN {ids}
            GROUP BY fw.id
            ORDER BY fw.updated_at;
        """.format(
            schema=self.schema, ids=ids
        )

        return self.fetch_all(query)

    def extract(self) -> tuple[list, str]:
        data = self._produce()

        if data:
            return self._enrich(tuple([i["id"] for i in data])), str(data[-1]["updated_at"])

        return data, self.updated_at
