from goodreads.book_database import Database as BookDB
from goodreads.book_database import Book as Book
import glob

from typing import Dict, Tuple, Sequence


def is_book_ok(book: Book):
    return float(book.avgRating) > 4 and int(book.ratingCount) > 4000


def filter_books(all_entries: Dict[str, Book]):
    authors = []
    for key, value in all_entries.items():
        uid: str = key
        book: Book = value
        if is_book_ok(book):
            # print("Book ok: ", book.title)
            authors.append((book.author, book.uid))
    return authors


def get_all_local_epub_files():
    files = []
    import os
    for root, directories, filenames in os.walk('/home/patrick/Documents/books/A-Z/'):
        for directory in directories:
            os.path.join(root, directory)
        for filename in filenames:
            files.append(filename)
            os.path.join(root, filename)
    return files


def normalize_author_string(text: str):
    # Case insesetive
    text = text.lower()
    # Remove Whitespaces left and right
    text = text.lstrip()
    text = text.rstrip()


def get_all_local_authors(file_names) -> Tuple[str, str]:
    authors = []
    for file in file_names:
        parts = file.split('-')
        if len(parts) != 0:
            first_part = parts[0]
            authors.append((first_part, file))
    return authors


# Prüft, ob ein Author in der Lokalen autoren vorhanden ist
def is_local_author(local_authors, author: str):
    search_parts = author.split(" ")
    # Wir wollen keine leeren Suchen und Abkürzungen da oft wegelassen
    search_parts = [part for part in search_parts if len(part) > 0 and part[-1] != '.']
    # print(search_parts)
    for author_file in local_authors:
        author = author_file[0]
        error = False
        for part in search_parts:

            if part not in author:
                error = True
                break
        # Alle Parts wurden in einer Datei gefunden => match
        if not error:
            return (True, author_file[1])
    return (False, None)


def main():
    print("Dies ist ein Test")
    files = get_all_local_epub_files()
    local_authors = get_all_local_authors(files)
    # "J.R.R.Tolkien" sollte gefunden werden
    # print(local_authors)
    db = BookDB()

    # print("Tolkin is Lokcal auhtor: ",is_local_author(local_authors,'J.R.R. Tolkien'))

    filtered_books = filter_books(db.get_all_entries()["books"])
    for book in filtered_books:
        goodreads_author: str = book[0]
        book_uid: str = book[1]
        book_infos = db.read(book_uid)
        is_local, local_file = is_local_author(local_authors, goodreads_author)
        if is_local:
            print(" Ratings: ", book_infos.ratingCount," AvgRating: ", book_infos.avgRating," Autor: ", goodreads_author, ": \t\t", book_infos.title)
        # else:
        #   print(book_infos.author)
