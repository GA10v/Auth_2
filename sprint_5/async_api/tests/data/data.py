import random

from utils import DefaultModel

from models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class FakeData(DefaultModel):
    _range: int = 10

    def get_data(self) -> dict:
        """
        Получение фейковых данных для psql.

        Returns:
            dict: Словарь с фейковыми данными.
        """
        films = self._get_fw()
        persons = self._get_persons()
        genres = self._get_genre()
        person_fw = []
        genre_fw = []
        for film in films:
            for person in random.sample(persons, 5):  # noqa: DUO102
                person_fw.append(
                    GenreFilmWork(
                        **self._person_fw(
                            fw=film,
                            person=person,
                            role=random.choice(['actor', 'director', 'writer']),  # noqa: DUO102
                        ),
                    ),
                )
            for genre in random.sample(genres, 3):  # noqa: DUO102
                genre_fw.append(
                    PersonFilmWork(
                        **self._genre_fw(
                            fw=film,
                            genre=genre,
                        ),
                    ),
                )

        return {
            'films': films,
            'persons': persons,
            'genres': genres,
            'person_fw': person_fw,
            'genre_fw': genre_fw,
        }

    def _get_fw(self) -> list[FilmWork]:
        """Получениу списка объектов FilmWork."""
        return [FilmWork(**self._film_work()) for _ in range(self._range)]

    def _get_persons(self) -> list[Person]:
        """Получениу списка объектов Person."""
        return [Person(**self._person()) for _ in range(self._range)]

    def _get_genre(self) -> list[Genre]:
        """Получениу списка объектов Genre."""
        return [Genre(**self._genre()) for _ in range(self._range)]
