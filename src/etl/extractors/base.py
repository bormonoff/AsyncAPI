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
        self.tables = ['film_work', 'genre', 'person']

    @backoff(psycopg2.DatabaseError)
    def fetch_all(self, query):
        cursor = self._connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def _produce(self) -> dict[str, list]:
        extracted_data = {}
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
        ids = tuple([i["id"] for i in data])
        if ids:
            if self.MAIN_TABLE:
                extracted_data[self.TABLE_NAME] = data
                self.tables.remove(self.TABLE_NAME)
                for table in self.tables:
                    query = """
                        SELECT DISTINCT i.id
                        FROM {schema}.{table} as i
                        LEFT JOIN {schema}.{table}_film_work as ifw ON i.id = ifw.{table}_id
                        WHERE ifw.film_work_id IN {ids};         
                    """.format(schema=self.schema, table=table, ids=ids)
                    extracted_data[table] = tuple([i["id"] for i in self.fetch_all(query)])
            else:
                query = """
                    SELECT fw.id, i.updated_at
                    FROM {schema}.film_work fw
                    LEFT JOIN {schema}.{table}_film_work ifw ON ifw.film_work_id = fw.id
                    LEFT JOIN {schema}.{table} i ON i.id = ifw.{table}_id
                    WHERE i.id IN {ids}
                    ORDER BY i.updated_at;
                """.format(schema=self.schema, table=self.TABLE_NAME, ids=ids)
                extracted_data['film_work'] = self.fetch_all(query)
                extracted_data[self.TABLE_NAME] = ids
        return extracted_data

    def _enrich_film_work(self, ids: tuple) -> list:
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

    def _enrich_genre(self, ids: tuple) -> list:
        query = """
            SELECT DISTINCT id, name
            FROM {schema}.genre
            WHERE genre.id IN {ids};
        """.format(schema=self.schema, ids=ids)
        return self.fetch_all(query)

    def _enrich_person(self, ids: tuple) -> list:
        query = """
                SELECT id, full_name as name, 
                COALESCE(json_agg(DISTINCT jsonb_build_object('id', film_work_id, 'roles', roles))) as films 
                FROM (SELECT p.id, p.full_name, pfw.film_work_id, array_agg(DISTINCT pfw.role) as roles 
                FROM {schema}.person as p
                LEFT JOIN {schema}.person_film_work as pfw on p.id = pfw.person_id
                WHERE p.id in {ids}
                GROUP BY p.id, pfw.film_work_id) as temp_persons
                GROUP BY id, full_name;
            """.format(schema=self.schema, ids=ids)

        return self.fetch_all(query)

    def extract(self) -> tuple[dict, str]:
        extracted_data = self._produce()

        if data := extracted_data.get('film_work'):
            self.updated_at = str(data[-1]["updated_at"])
            extracted_data['film_work'] = self._enrich_film_work(tuple([i["id"] for i in data]))
        if data := extracted_data.get('genre'):
            extracted_data['genre'] = self._enrich_genre(tuple(data))
        if data := extracted_data.get('person'):
            extracted_data['person'] = self._enrich_person(tuple(data))
        return extracted_data, self.updated_at
