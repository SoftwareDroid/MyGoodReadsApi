import os
from typing import Tuple, List
from goodreads.book_database import Book


# path e.g. =
class LocalAuthorFilter:
    def __init__(self, path: str):
        self.folder = path
        self.files = []
        self.authors = []
        # Check if path exits
        if not os.path.isdir(path):
            raise Exception('Folder does not exist: {}'.format(path))

        self._get_all_local_epub_files()
        self._get_all_local_authors()
        # Release Memory
        del self.files[:]
        self._author_to_local_files = {}

    def _get_local_author_files(self, author: str) -> List[str]:
        """Returns all local file of a author."""
        local_files = []
        search_parts = author.split(" ")
        # We do not want empty searches and abbreviations as often omitted
        search_parts = [part for part in search_parts if len(part) > 0 and part[-1] != '.']

        for author_file in self.authors:
            author = author_file[0]
            error = False
            for part in search_parts:
                if part not in author:
                    error = True
                    break
            # All parts were found in one file => match
            if not error:
                local_files.append(author_file[1])
        # If we have not local file
        return local_files

    def get_local_author_files(self, author):
        assert len(self._author_to_local_files) > 0, "The the filter before on every book to get the correct results"
        assert author in self._author_to_local_files
        return self._author_to_local_files[author]

    def filter(self, book: Book) -> bool:
        author = book.author
        if author not in self._author_to_local_files:
            self._author_to_local_files[author] = self._get_local_author_files(author)
        return len(self._author_to_local_files[author]) > 0


    def _get_all_local_epub_files(self):
        """Find all epub files in the folder"""
        for root, directories, filenames in os.walk(self.folder):
            for directory in directories:
                os.path.join(root, directory)
            for filename in filenames:
                self.files.append(filename)
                os.path.join(root, filename)

    def _get_all_local_authors(self):
        """Extract all author form the epub files"""
        for file in self.files:
            parts = file.split('-')
            if len(parts) != 0:
                first_part = parts[0]
                self.authors.append((first_part, file))
