import pandas as pd
import requests
from urllib.parse import urlencode
from collections import Counter
import re


"""
Read and clean GoodReads Export .csv file to get book information
"""
def clean_goodreads():
    gdLibrary = 'goodreads_library_export.csv'
    goodreads = pd.read_csv(gdLibrary)
    
    goodreads = goodreads.iloc[:, 0:16]
    goodreads.rename(columns={'Title': 'Title And Series'}, inplace=True)
    goodreads['Title'] = goodreads['Title And Series'].str.split("(").str[0].str.strip()
    goodreads['ISBN'] = goodreads['ISBN'].str.extract(r'(\d+)')
    goodreads['ISBN13'] = goodreads['ISBN13'].str.extract(r'(\d+)')

    return goodreads


"""
Retrieves genre/topics of books using OpenLibrary API
"""
def fetchBookData(bookname):
    books_df = clean_goodreads()
    #books_df = books_df[books_df['Date Read'].notna()]
    isbn = books_df[books_df['Title'] == bookname]['ISBN'].iloc[0]
    author = books_df[books_df['Title'] == bookname]['Author'].iloc[0]

    # prioritize using isbn to search for book
    if pd.isna(isbn) == False:
        url = f'https://openlibrary.org/isbn/{isbn}.json'
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()

    # if isbn is missing or request failed, search using title and author
    url = 'https://openlibrary.org/search.json'
    params = {
        'title': bookname,
        'author': author,
        'limit': 1
    }
    response = requests.get(url, params=params)

    #print(url)
    if response.status_code == 200:
        return response.json()

    return None
    

"""
Returns a list of subjects (genres)
""" 
def subjectList(record):
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
    response = requests.get(url)

    #print(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('subjects', None)
    else:
        return None


"""
Extracts the most frequent words from a list of book subjects.
"""
def simpleGenres(subjects):
    common_genres = ['fantasy', 'romance', 'fiction', 'thriller', 'mystery', 'horror', 'dystopian', 'drama', 'historical']
    multi_genres = ['fantasy fiction', 'science fiction', 'historical romance', 'mystery thriller', 'young adult', 'enemies to lovers']
    stopwords = {'and', 'to', 'in', 'of', 'the', 'for', 'on', 'with', 'by', 'a', 'an', 'at', 'from', 'as', 'is', 'it', 'its'}


    words = []
    phrases = []
    for s in subjects:
        s = s.lower()

        for phrase in multi_genres:
            if phrase in s:
                phrases.append(phrase)

        tokens = re.findall(r'[a-z]+', s)
        words.extend(tokens)

    words = [w for w in words if w not in stopwords and len(w) > 2]
    counter = Counter(words)
    phrase_counter = Counter(phrases)
    counter.update(phrase_counter)
    #top_genres = {word: count for word, count in counter.items() if count >= 3}
    top_genres = dict(counter.most_common(5))

    for genre in common_genres:
        if genre in counter and genre not in top_genres:
            top_genres[genre] = counter[genre]

    return top_genres

############################
def main():
    books_read = clean_goodreads()
    books_read = books_read[books_read['Date Read'].notna()]
    book_list = books_read['Title'].tolist()

    bookGenres = {}
    
    for book in book_list:
        record = fetchBookData(book)
        subjects = subjectList(record)
        if not subjects: # no subject list found
            bookGenres[book] = None
        else:
            genres = simpleGenres(subjects)
            if not genres: # no top genres found
                bookGenres[book] = None
            else:
                bookGenres[book] = list(genres.keys())
    
    for key, val in bookGenres.items():
        print(f'{key}: {val}')
    
    #print(bookGenres)

    genre_counts = Counter()
    for genre in bookGenres.values():
        genre_counts.update(genre)

    print(genre_counts)
    top5 = genre_counts.most_common(5)
    print(top5)


if __name__ == "__main__":
    main()