import pickle
from typing import Dict, Tuple, Sequence, Set

FORMAT_VERSION = 1

import collections

class DictWrapper(collections.Mapping):

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
class Book:
    def __init__(self, book_as_dict):
        self.uid = book_as_dict["uid"]
        self.author = book_as_dict["author"]
        self.title = book_as_dict["title"]
        self.ratingCount = book_as_dict["ratingCount"]
        self.avgRating = book_as_dict["avgRating"]
        self.genres = book_as_dict["genres"]

    uid: str = ""
    author: str = ""
    title: str = ""
    ratingCount: int = 0
    avgRating: float = 0.1
    genres: Set[str] = set()

class Database:
    def __init__(self, path: str):
        print("Read Full DB")
        self.path = path
        self.load_from_file(self.path)

    def get_all_entries(self) -> Dict[str,Book]:
        return DictWrapper(self.__db)

    def count_entries(self) -> int:
        return len(self.__db["books"])

    def load_from_file(self, path):
        error = False
        try:
            pickle_in = open(path, "rb")
            self.__db = pickle.load(pickle_in)
            if self.__db["header"]["version"] != FORMAT_VERSION:
                error = True
        except (FileNotFoundError, IOError, EOFError):
            error = True
        # If file is not there, corroput or in the wrong format do not us it
        if error:
            self.__db = {"books": {}, "header": {"version": FORMAT_VERSION}}

    def save_in_file(self, path):
        pickle_out = open(path, "wb")
        pickle.dump(self.__db, pickle_out)
        pickle_out.close()

    #def __del__(self):
    #    self.save()

    def save_list(self, list_name,list):
        if "downloaded_lists" not in self.__db:
            self.__db["downloaded_lists"] = {}
        self.__db["downloaded_lists"][list_name] = list

    def get_all_lists(self):
        if "downloaded_lists" not in self.__db:
            self.__db["downloaded_lists"] = {}
        return self.__db["downloaded_lists"]

    def has_list(self,list_name: str):
        if "downloaded_lists" not in self.__db:
            self.__db["downloaded_lists"] = {}
        return list_name in self.__db["downloaded_lists"]

    def save(self):
        self.save_in_file(self.path)    

    def read(self, uid: str) -> Book:
        if uid in self.__db["books"]:
            return self.__db["books"][uid]
        else:
            return None

    def has_book(self, uid: str) -> bool:
        return uid in self.__db["books"]

    def write(self, book_as_dict) -> bool:
        # Create book from dict
        book = Book(book_as_dict)
        # We don't overwrite books in the db for compatibility
        if self.has_book(book.uid):
            return False
        else:
            # Save book in db
            self.__db["books"][book.uid] = book
            return True
