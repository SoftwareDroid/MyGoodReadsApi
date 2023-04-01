#Dieses Tool kann verwendet werden, um unterschiedliche Bücher von Goodreads zu holen und mit Metadaten in einer Datei zu sepichern

from goodreads.web_crawler import WebCrawler as Goodreads
from goodreads.book_database import Database as BookDB
from typing import Dict, Tuple, Sequence
import sys

def get_genres():
    return set(["science",
                 "non-fiction",
                 "nature",
                 "plants",
                 "biology",
                 "physics",
                 "computer-science",
                 "popular-science",
                 "mathematics",
                 "engineering",
                 "natural-history",
                 "astronomy",
                 "chemistry",
                 "philosophy",
                 "history",
                 "environment",
                 "animals",
                 "anthropology",
                 "cultural",
                 "asia",
                 "humor",
                 "historical",
                 "ancient-history",
                 "technology",
                 "sociology",
                 "adventure",
                 "biography",
                 "travel",
                 "buddhism",
                 "evolution",
                 "india",
                 "adventurers",
                 "ancient",
                 "ancient-history",
                 "archaeology",
                 "artificial-intelligence",
                 "chemistry"])



def main():
    crawler = Goodreads()
    db = BookDB()
    for genre in get_genres():
        print(genre)
        print(sys.getsizeof(db))
        # print("Genre: ",genre)
        # Get the first 20 pages of the genres
        # print("Crawl...")
        uid_lists2 = crawler.get_genre_book_list(genre, 1, 2)
        # rint("End Crawl ")
        for uid_lists in uid_lists2:
            print("Found Books ",uid_lists)
            # Get all UID which are not in the db
            #for b in uid_lists:
            #    print("In DB: ",db.has_book(b)," ",b)
            new_uids = [x for x in uid_lists if not db.has_book(x)]
            #print("New Books: ",new_uids)
            if len(new_uids) > 0:
                #print("Crawl Book Infos")
                book_infos = crawler.get_books_infos(new_uids)
                for book in book_infos:
                    #print("Save Book: ",book)
                    db.write(book)
