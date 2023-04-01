from goodreads.book_database import Database as BookDB
from goodreads.book_database import Book as Book
import sys
import argparse
from pathlib import Path
import os
from typing import Tuple, List
import json

from db_viewer.local_author_filter import LocalAuthorFilter
from db_viewer.simple_book_filters import BlackListFilter, MinRatingFilter, RatingCountFilter, WhiteListFilter, \
    IgnoredAuthorsFilter


class Viewer:
    def order_books(self, b: Book):
        """The sort ordering for the output"""
        return float(b.avgRating) * 1000 + int(b.ratingCount)

    def __init__(self):
        parser = argparse.ArgumentParser()
        # Define Datebase file
        parser.add_argument('--auto_ignore_authors', choices=['on', 'off'], required=True,
                            help="By pressing Enter every author to the ignore list")
        parser.add_argument('--db', type=str, default="content/default.pickle", help="The database file which is used")
        parser.add_argument('--filter', type=str, default="custom/comparer_settings.json",
                            help="The settings file for filtering the output")
        # List all geres and list all lists
        parser.add_argument('--mode', dest='mode', choices=['compare', 'print-db-meta'],
                            help="The mode of the viewer")
        args = parser.parse_args()
        self.args = args
        if not os.path.isfile(args.db):
            print("Could not open database ", args.db)
            parser.print_help()
            sys.exit(0)
        print(args.filter)
        if not os.path.isfile(args.filter):
            print("Could not open filter definition file ", args.filter)
            parser.print_help()
            sys.exit(0)

        with open(args.filter) as settings_file:
            settings = json.load(settings_file)
        self.use_whitelist = settings["use_whitelist"]
        self.use_blacklist = settings["use_blacklist"]
        self.blacklist_genres = settings["blacklist"]
        self.white_genres = settings["whitelist"]
        self.min_book_avg_rating = settings["min_book_avg_rating"]
        self.min_book_rating_count = settings["min_book_rating_count"]
        self.whitelist = settings["whitelist"]
        self.ignored_authors = settings["ignore_authors"]
        self.path_to_local_epubs: str = settings["local_epub_dir"]
        self.settings = settings

        self.new_ignore_authors = []

    def run(self):
        self._print_infos()
        books, local_author_filter = self._apply_filters()
        self._start_prompt(books, local_author_filter)

    def _apply_filters(self) -> Tuple[LocalAuthorFilter, List[Book]]:
        print("Create Filters")
        # Create Book Filters
        filters = [MinRatingFilter(self.min_book_avg_rating), RatingCountFilter(self.min_book_rating_count),
                   IgnoredAuthorsFilter(self.ignored_authors)]
        if self.use_whitelist:
            filters.append(WhiteListFilter(set(self.white_genres)))

        if self.use_blacklist:
            filters.append(BlackListFilter(self.blacklist_genres))

        local_author_filter = LocalAuthorFilter(self.path_to_local_epubs)
        filters.append(local_author_filter)
        print("Read books from database")
        # Open database
        db = BookDB(self.args.db)
        # Get all books in database

        all_books: Tuple[Book] = db.get_all_entries()["books"]
        print("Apply filters")
        filtered_books = []
        # Apply filters
        for book_id in all_books:
            book: Book = all_books[book_id]
            filter_out: bool = False
            # Check the book against all filter
            for f in filters:
                if not f.filter(book):
                    filter_out = True
                    break

            if not filter_out:
                filtered_books.append(book)

        print("Sort Books ", len(filtered_books))

        filtered_books.sort(key=self.order_books, reverse=True)
        return filtered_books, local_author_filter

    def _print_infos(self):
        print("Current Settings")
        print("Local Epub Folder ", self.path_to_local_epubs)
        print("Use Whitelist: ", self.use_whitelist)
        print("Use Blacklist", self.use_blacklist)
        if self.use_blacklist:
            print("Backlist Tags", self.blacklist_genres)
        print("Ignored Authors: ", len(self.ignored_authors))
        print("Min average Rating: ", self.min_book_avg_rating)
        print("Min Rating Count: ", self.min_book_rating_count)
        print("End of Settings\n")

    def _start_prompt(self, books: List[Book], local_author_filter: LocalAuthorFilter):
        print("Starting prompt: \n\n")
        for b in books:
            if b.author in self.new_ignore_authors:
                continue
            print(b.title)
            print(b.author)
            print("Rating", b.avgRating, "Ratings Count: ", b.ratingCount)
            print("Genres: ", b.genres)
            print("Local Files")
            for file in local_author_filter.get_local_author_files(b.author):
                base_name: str = Path(file).stem
                print("\t", base_name)
            print("\n")
            print("Press Enter for next Book:")
            input()
            self.new_ignore_authors.append(b.author)

            # Ignore Author from now on

    def rewrite_settings(self):
        print("Rewrite Settings file")
        print("Added {} new ignored authors".format(len(self.new_ignore_authors)))
        if self.args.auto_ignore_authors == "on":
            for author in self.new_ignore_authors:
                self.settings["ignore_authors"].append(author)
        else:
            print("Ignored Authors not added to the filter def file: ", self.new_ignore_authors)
        self.new_ignore_authors = []
        data = json.dumps(self.settings, sort_keys=False, indent=4)
        text_file = open(self.args.filter, "w")
        text_file.write(data)
        text_file.close()


if __name__ == '__main__':
    try:
        viewer = Viewer()
        viewer.run()
        viewer.rewrite_settings()

    except KeyboardInterrupt:
        viewer.rewrite_settings()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
