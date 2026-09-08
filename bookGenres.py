import pandas as pd
import requests
from urllib.parse import urlencode
from collections import Counter
import re
import seaborn as sns
import matplotlib.pyplot as plt


"""
Cleans Goodreads library data and analyzes the genres of read books.

Steps:
1. Load and clean the Goodreads CSV data.
2. Retrieve book information from the OpenLibrary API using ISBN or title and author.
3. Extract subject information and identify common genres.
4. Organize the genres for each book into a DataFrame.
5. Visualize the distribution of genres among the books read.
"""

def clean_goodreads():
    """
    Read and clean GoodReads Export .csv file to get book information
    """
    grLibrary = 'datasets/goodreads_library_export.csv'
    goodreads = pd.read_csv(grLibrary)
    
    goodreads = goodreads.iloc[:, list(range(16)) + [18]]
    goodreads.rename(columns={'Title': 'Title And Series'}, inplace=True)
    goodreads['Title'] = goodreads['Title And Series'].str.split("(").str[0].str.strip()
    goodreads['ISBN'] = goodreads['ISBN'].str.extract(r'(\d+)')
    goodreads['ISBN13'] = goodreads['ISBN13'].str.extract(r'(\d+)')

    return goodreads


def fetchBookData(bookname):
    """
    Retrieves genre/topics of books using OpenLibrary API
    """
    books_df = clean_goodreads()
    #books_df = books_df[books_df['Date Read'].notna()]
    isbn = books_df[books_df['Title'] == bookname]['ISBN'].iloc[0]
    author = books_df[books_df['Title'] == bookname]['Author'].iloc[0]

    # prioritize using isbn to search for book
    if pd.isna(isbn) == False:
        url = f'https://openlibrary.org/isbn/{isbn}.json'
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()

    # if isbn is missing or request failed, search using title and author
    url = 'https://openlibrary.org/search.json'
    params = {
        'title': bookname,
        'author': author,
        'limit': 1
    }
    response = requests.get(url, params=params, timeout=10)

    #print(url)
    if response.status_code == 200:
        return response.json()

    return None
    

def subjectList(record):
    """
    Returns a list of subjects (genres)
    """ 
    if not record:
        return None

    # Retrieve works key
    works_key = None
    if 'docs' in record and record['docs']:
        works_key = record['docs'][0].get('key')
    elif 'works' in record and record['works']:
        works_key = record['works'][0].get('key')

    if not works_key:
        return None

    url = f'https://openlibrary.org{works_key}.json'
    response = requests.get(url, timeout=10)

    #print(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('subjects', None)
    else:
        return None


def simpleGenres(subjects):
    """
    Extracts the most frequent words from a list of book subjects.
    """
    common_genres = ['fantasy', 'romance', 'fiction', 'thriller', 'mystery', 'horror', 'dystopian', 'drama', 'historical']
    multi_genres = ['fantasy fiction', 'science fiction', 'historical romance', 'mystery thriller', 'young adult', 'enemies to lovers', 'new york times bestseller', 'american literature']
    stopwords = {'and', 'to', 'in', 'of', 'the', 'for', 'on', 'with', 'by', 'a', 'an', 'at', 'from', 'as', 'is', 'it', 'its'}

    phrases_found = []
    word_counter = Counter()

    for s in subjects:
        s = s.lower()

        for phrase in multi_genres:
            if phrase in s:
                phrases_found.append(phrase)
                s = s.replace(phrase, '')

        tokens = re.findall(r'[a-z]+', s)
        tokens = [t for t in tokens if t not in stopwords and len(t) > 2]

        word_counter.update(tokens)

    result = {}

    # --- phrases ---
    for p, c in Counter(phrases_found).items():
        result[p] = c

    # --- common genres ---
    for g in common_genres:
        if word_counter[g] > 0:
            result[g] = word_counter[g]

    # --- top words ---
    for w, c in word_counter.most_common(1):
        result[w] = c

    return result

############################
def genre():
    books_read = clean_goodreads()
    #books_read = books_read[books_read['Date Read'].notna()]
    books_read = books_read[books_read['Exclusive Shelf'] == 'read']
    book_list = books_read['Title'].tolist()

    bookGenres = []
    
    for book in book_list:
        record = fetchBookData(book)
        subjects = subjectList(record)
        if not subjects: # no subject list found
            continue
        else:
            genres = simpleGenres(subjects)
            #print(genres)
            if not genres: # no top genres found
                continue
            else:
                new_row = {"Book" : book, "Genre" : list(genres.keys())}
                bookGenres.append(new_row)
    
    df = pd.DataFrame(bookGenres)
    books = df.explode("Genre")
    return books


def main():
    books = genre()
    plt.figure(figsize=(12,8))
    sns.set_theme()
    sns.set_palette(sns.color_palette("husl", 8))
    sns.countplot(data=books, x='Genre', order=books['Genre'].value_counts().index)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('graphs/genre_distribution.png')


if __name__ == "__main__":
    main()