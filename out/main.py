from goodreads.web_crawler import WebCrawler as Goodreads
from goodreads.book_database import Database as BookDB
from tools.fill_best_books import main as FillFunc
from tools.compare_goodreads_wiht_local_books import main as CompareWithLocal

def main():
    crawler = Goodreads()
    #crawler.thread_count_during_batch = 100
    books_lists = crawler.get_genre_book_list("world-history", 1, 20)
    print("Pages Loaded")
    print(books_lists)
    for books in books_lists:
        #print(books)
        book_infos = crawler.get_books_infos(books)
        for i in book_infos:
            print(i)


def main2():
    books = [{'author': 'Daniel J. Boorstin', 'title': "The Discoverers: A History of Man's Search to Know His World and Himself", 'ratingCount': '10699', 'avgRating': '4.11', 'genres': {'Nonfiction', 'Science', 'World History', 'History'}, 'uid': '/book/show/714380.The_Discoverers'}]

    db = BookDB()
    for b in books:
        db.write(b)

if __name__ == '__main__':
    try:
        CompareWithLocal()
    except KeyboardInterrupt:
        print("You've decided to close the program")
