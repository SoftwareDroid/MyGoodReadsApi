# Import Credentiels
import goodreads.credentials as credentials
from bs4 import BeautifulSoup as bs
import requests
# For type annoationen
from typing import Dict, Tuple, Sequence
# For batch processing (accelerate download webpages)
from multiprocessing import Pool


def parse_website(url: str, payload, cookies):
    result = requests.get(url, params=payload, cookies=cookies)
    return bs(result.text, 'html.parser')


def get_book_author(bookIdPage):
    tmp = bookIdPage.find('a', attrs={'class', 'authorName'})
    if tmp is None:
     return None
    return tmp.span.get_text()


def format_title(bookTitle):
    return ' '.join(bookTitle.split()).replace('&amp;', '&')


def get_book_title(bookIdPage):
    title = bookIdPage.find('h1', attrs={'id': 'bookTitle'})
    if title is None:
        return None
    title: str = title.get_text()
    return format_title(title)


def get_book_rating_count(bookIdPage):
    # <meta content="231566" itemprop="ratingCount">
    tmp = bookIdPage.find('meta', attrs={"itemprop": "ratingCount"})
    if tmp is None:
        return None
    return tmp["content"]


def get_average_rating(bookIdPage):
    tmp = bookIdPage.find('span', attrs={"itemprop": "ratingValue"})
    if tmp is None:
        return None
    return format_title(tmp.get_text())


def get_book_infos(bookId: str):
    BASE_URL = "https://www.goodreads.com/"
    url = BASE_URL + bookId
    # print("Access URL", url)
    # No Parameters and no cookies
    page = parse_website(url, {}, {})
    # Scrape Information about book
    author = get_book_author(page)
    title = get_book_title(page)
    rating_count = get_book_rating_count(page)
    avg_rating = get_average_rating(page)
    genres = get_genres(page)
    return {"author": author, "title": title, "ratingCount": rating_count, "avgRating": avg_rating, "genres": genres , "uid" : bookId}


def get_genres(bookIdPage):
    genres = bookIdPage.findAll("a", {"class": "actionLinkLite bookPageGenreLink"})
    return set(str(g.text) for g in genres)


def get_all_booktitles(soup):
    # Get all Titles and convert them into strings
    return [title["href"] for title in soup.find_all('a', attrs={'class': 'bookTitle'})]


def get_genre_book_list_private(arg: Tuple[str, int]):
    genre = arg[0]
    page = arg[1]
    """Get all bookdIds from a given genre on certain page """
    assert page >= 1, "Invalid Page"
    params = {}
    if page != 1:
        params = {"page": str(page)}
    # Accessing other pages as the first page works only if we are logged in
    # Example: https://www.goodreads.com/shelf/show/world-history
    BASE_URL = "https://www.goodreads.com/shelf/show/"
    url = BASE_URL + genre
    # print("URL: " + url)
    parsed_page = parse_website(url, params, credentials.cookies)
    # Retrieve Result
    return get_all_booktitles(parsed_page)


class WebCrawler:
    def __init__(self):
        # print("Create Web Crawler")
        # Clear cookies, so that we are not logged in
        self.__cookies = {}
        # For Saving and accepting cookies
        # self.session = requests.Session()
        # How many threads are used during batch processing?
        self.__threadcount = 15
        assert self.__threadcount <= 15, "To many threads!!! => IP Ban from Goodreads"

    @property
    def thread_count_during_batch(self):
        return self.__threadcount

    def get_genre_book_list(self, genre: str, first_page, lastpage):
        p = Pool( self.__threadcount)
        results = p.map(get_genre_book_list_private, [(genre, page) for page in range(first_page, lastpage +1)])
        p.close()
        return results

    def get_books_infos(self, list_of_books: Sequence[str]):
        """Fetch metadae for a sequence of books from goodreads"""
        # We don't need to be logged in here.
        p = Pool(self.__threadcount)
        results = p.map(get_book_infos, list_of_books)
        p.close()
        return results

    def __logout(self):
        self.__cookies = {}

    def __login(self):
        self.__cookies = credentials.cookies
