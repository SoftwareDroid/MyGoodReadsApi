#Dieses Tool kann verwendet werden, um unterschiedliche Bücher von Goodreads zu holen und mit Metadaten in einer Datei zu speichern

from goodreads.web_crawler import WebCrawler as Goodreads
from goodreads.book_database import Database as BookDB
from typing import Dict, Tuple, Sequence
import sys
import os
from content.input import get_genres
import argparse




def main():
    parser = argparse.ArgumentParser()
    # Define Datebase file
    parser.add_argument('--db', type=str, default="content/default.pickle", help="The database file which is used")
    parser.add_argument('--ddlists', type=str, default=False, help="Download lists twice")
    args = parser.parse_args()

    if not os.path.isfile(args.db):
        print("Could not open database ", args.db)
        parser.print_help()
        sys.exit(0)

    crawler = Goodreads()
    db = BookDB(args.db)
    for genre in get_genres():
        print("Download list {}".format(genre))
        uid_lists2 = crawler.get_genre_book_list(genre, 1, 1)

        # Do not crawl a list more than once
        if db.has_list(genre) and not args.ddlists:
            print("List already in db ")
            continue

        for uid_lists in uid_lists2:
            new_uids = [x for x in uid_lists if not db.has_book(x)]
            if len(new_uids) > 0:
                book_infos = crawler.get_books_infos(new_uids)
                for book in book_infos:
                    db.write(book)
            # Save list in database
            db.save_list(genre, [x for x in uid_lists])
        print("Save Database Entries: ", db.count_entries())
        db.save()
main()
