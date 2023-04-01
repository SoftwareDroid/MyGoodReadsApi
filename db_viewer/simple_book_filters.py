from typing import List
from goodreads.book_database import Book


class MinRatingFilter:
    def __init__(self, min_rating: float):
        assert (0 <= min_rating <= 5)
        self.min_rating = min_rating

    def filter(self, book: Book) -> bool:
        if book.avgRating is None:
            return False
        else:
            return float(book.avgRating) >= self.min_rating


class RatingCountFilter:
    def __init__(self, rating_count: int):
        assert (rating_count >= 0)
        self.rating_count = rating_count

    def filter(self, book: Book) -> bool:
        if book.ratingCount is None:
            return False
        else:
            return int(book.ratingCount) >= self.rating_count


class WhiteListFilter:
    def __init__(self, white_list: List[str]):
        assert (white_list is not None)
        self.white_list = set(white_list)

    def filter(self, book: Book) -> bool:
        for g in self.white_list:
            if g not in book.genres:
                return False
        return True


class BlackListFilter:
    def __init__(self, black_list: List[str]):
        assert (black_list is not None)
        self.black_list = set(black_list)

    def filter(self, book: Book) -> bool:
        for g in self.black_list:
            if g in book.genres:
                return False
        return True

class IgnoredAuthorsFilter:
    def __init__(self, ignored_authors):
        self._ignored_authors = set(ignored_authors)

    def filter(self, book: Book) -> bool:
        return book.author not in self._ignored_authors