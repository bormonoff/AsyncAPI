import json
import os
import uuid


def create_movies(filename):
    "Use this function to generate the initial movie data."
    data = list()
    for i in range(50):
        film_body = {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.9,
            "title": "The star",
            "description": "A film about a star",
            "type": "movie",
            "genres_names": ["action", "drama"],
            "directors_names": ["Angela Turner"],
            "actors_names": ["Gilby Clarke", "Barbara Church"],
            "writers_names": ["Bernard Baur"],
            "genres": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "action"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "drama"
                }
            ],
            "directors": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Angela Turner"
                }
            ],
            "actors": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Gilby Clarke"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Barbara Church"
                }
            ],
            "writers": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Bernard Baur"
                },
            ]
        }

        film_doc = {
            "_index": "movies",
            "_id": film_body["id"],
            "_source": film_body
        }
        data.append(film_doc)
    with open(f"{os.path.dirname(__file__)}/{filename}.json", "w") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    # Initially creates movies with random UUID and the same data
    # After creation, manually change some fields as you need for testing
    create_movies("movies_data")