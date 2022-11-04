from enum import Enum


class GenreMessages(str, Enum):
    not_found = 'Genre not found'


class PersonMessages(str, Enum):
    not_found = 'Person not found'


class FilmMessages(str, Enum):
    not_found = 'Film not found'
