import pandas as pd
from datetime import datetime, date
import seaborn as sns
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# FILNAMES
readingInsights = 'datasets/Kindle.reading-insights-sessions_with_adjustments.csv'
readingSession = 'datasets/Kindle.Devices.ReadingSession.csv'
grLibrary = 'datasets/goodreads_library_export.csv'

########################################################
################ READING ALL DATASETS ##################

def clean_session_file():
    """
    clean ReadingSession file from Amazon Kindle Data
    """
    session = pd.read_csv(readingSession, parse_dates=['start_timestamp', 'end_timestamp'])
    session = session[session['total_reading_millis'].notna()].copy()

    session['start_timestamp'] = pd.to_datetime(session['start_timestamp'])
    session['end_timestamp'] = pd.to_datetime(session['end_timestamp'])

    session['start_local'] = session['start_timestamp'].dt.tz_convert('America/Vancouver')
    session['end_local'] = session['end_timestamp'].dt.tz_convert('America/Vancouver')

    session['start_date'] = pd.to_datetime(session['start_local'].dt.date)
    session['end_date'] = pd.to_datetime(session['end_local'].dt.date)

    session['start_hour'] = session['start_local'].dt.strftime("%H:%M")
    session['start_hour_decimal'] = (
        session['start_local'].dt.hour +
        round(session['start_local'].dt.minute/60, 2)
    )

    return session


def clean_book_insights():
    """
    clean Reading Insights Session file from Amazon Kindle Data
    """
    book_session = pd.read_csv(readingInsights)
    book_session['start_time'] = pd.to_datetime(book_session["start_time"], format='mixed')
    book_session['end_time'] = pd.to_datetime(book_session["end_time"], format='mixed')
    book_session['start_local'] = book_session['start_time'].dt.tz_convert('America/Vancouver')
    book_session['end_local'] = book_session['end_time'].dt.tz_convert('America/Vancouver')

    book_session['start_date'] = pd.to_datetime(book_session['start_local'].dt.date)
    book_session['end_date'] = pd.to_datetime(book_session['end_local'].dt.date)
    book_session.rename(columns={'product_name' : 'book_title'}, inplace=True)

    return book_session

def clean_goodreads():
    """
    Clean GoodReads data 
    """
    goodreads = pd.read_csv(grLibrary)
    goodreads = goodreads.iloc[:, list(range(16)) + [18]]
#    goodreads = goodreads[goodreads['Date Read'].notna()]
    goodreads['Year Read'] = pd.to_datetime(goodreads['Date Read'], errors='coerce').dt.year.astype('Int64')
    goodreads['Month Read'] = pd.to_datetime(goodreads['Date Read'], errors='coerce').dt.month.astype('Int64')
    goodreads['Month Name'] = pd.to_datetime(goodreads['Date Read']).dt.month_name()
    goodreads.rename(columns={'Title': 'Title And Series'}, inplace=True)
    goodreads['Title'] = goodreads['Title And Series'].str.split("(").str[0].str.strip()

    return goodreads

#####################################################################
################## READING TIME ANALYSIS ############################

def reading_totals():
    session = clean_session_file()

    # TOTAL TIME PER DAY (FOR VISUALIZATION)
    read_per_day = session.groupby('start_date')['total_reading_millis'].sum().reset_index()
    read_per_day['total_minutes'] = (read_per_day['total_reading_millis']/60000).round(2)
    read_per_day['total_hours'] = (read_per_day['total_reading_millis']/3600000).round(2)

    read_per_day.sort_values(by='start_date', inplace=True)

    # CALCULATE TOTAL READING TIME SO FAR
    total_reading_sec = (session['total_reading_millis'].sum()/1000).round(2)
    total_sec = total_reading_sec
    days = int(total_reading_sec // (24 * 3600))
    total_reading_sec %= (24 * 3600)

    hours = int(total_reading_sec // 3600)
    total_reading_sec %= 3600

    minutes = int(total_reading_sec // 60)
    seconds = int(total_reading_sec % 60)

    overall_stat = (days, hours, minutes, seconds)

    return read_per_day, overall_stat, total_sec


# Visualize the average reading time for each day of the week
# TO DO: limit the rows to this year only, when there is enough data
def weekly_avg_time():

    read_per_day, _, _ = reading_totals()
    read_per_day['day_of_week'] = read_per_day['start_date'].dt.day_name()

    weekly = read_per_day.groupby('day_of_week')['total_minutes'].mean().reset_index()

    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    plt.figure(figsize=(8,5))
    sns.set_theme()
    sns.set_palette(sns.color_palette("husl", 8))
    g = sns.barplot(data=weekly, y='total_minutes', x='day_of_week', order=week_order)
    g.set(xlabel='Day of Week', ylabel='Minutes', title='Average Reading Time per Day')
    g.yaxis.set_major_locator(MultipleLocator(60))
    plt.tight_layout()
    plt.savefig('graphs/weekly_avg_reading.png')
    #plt.show()


# book that took the shortest and longest amount of time to complete
# GoodReads data is used to merge the completion date of a book
def shortest_longest_book():
    current_year = date.today().year

    insights = clean_book_insights()
    library = clean_goodreads()

    books_this_year = library[(library['Year Read'] == current_year)]
    date_read = books_this_year[['Title', 'Date Read']]

    completed_books = pd.merge(insights, date_read, how='left', left_on='book_title', right_on='Title')
    completed_books = completed_books[completed_books['Date Read'].notna()]
    completed_books = completed_books[completed_books['start_date'] <= completed_books['Date Read']]

    per_book = completed_books.groupby('book_title')['total_reading_milliseconds'].sum().reset_index()
    per_book['total_seconds'] = (per_book['total_reading_milliseconds']/1000).round(2)

    minidx = per_book['total_seconds'].idxmin()
    maxidx = per_book['total_seconds'].idxmax()

    shortest_book = per_book.loc[minidx, 'book_title']
    shortest_time = round(per_book.loc[minidx, 'total_seconds']/3600, 2)

    longest_book = per_book.loc[maxidx, 'book_title']
    longest_time = round(per_book.loc[maxidx, 'total_seconds']/3600, 2)

    print(f"Shortest: {shortest_book} - {shortest_time} hours.")
    print(f"Longest: {longest_book} - {longest_time} hours.")

    return


def totalPagesRead():
    current_year = date.today().year

    # number of physical pages read
    goodreads = clean_goodreads()
    completed_books = goodreads[goodreads['Exclusive Shelf'] == 'read']
    completed_books = completed_books[(completed_books['Year Read'] == current_year)]
    physical_pages = completed_books['Number of Pages'].sum()

    # number of kindle pages flipped
    session = clean_session_file()
    kindle_pages = int(session['number_of_page_flips'].sum())

    print(f"This year, you've completed the equivalent of {physical_pages:,} physical book pages and read {kindle_pages:,} pages on your Kindle.")

    return physical_pages, kindle_pages


def totalBooksRead():
    current_year = date.today().year

    library = clean_goodreads()
    books_this_year = library[library['Year Read'] == current_year]
    book_count = int(books_this_year['Date Read'].count())
    books = books_this_year[['Title', 'Date Read']]

    print(f'You completed {book_count} books this year!')

    print('You read the following books:')
    for i in range(book_count):
        print(f'{i+1}. {books_this_year['Title'].values[i]} on {books_this_year['Date Read'].values[i]}')

    return book_count, books


def sessionCount():
    session = clean_session_file()

    num_of_days = len(session['start_date'].unique())
    num_of_sessions = len(session)

    print(f'You picked up your kindle for {num_of_days} separate days and opened it {num_of_sessions} different times.')


def faveAuthors():
    goodreads = clean_goodreads()
    completed_books = goodreads[goodreads['Exclusive Shelf'] == 'read']

    author_count = completed_books.groupby(['Author'])['Title'].count().reset_index().sort_values(by='Title', ascending=False)

    print('Your all-time favourite authors are...')
    for i in range(10):
        print(f"{author_count['Author'].values[i]} with a total of {author_count['Title'].values[i]} books read.")
    
    return author_count

# Visualize hourly reading trend oer day
def hourlyReading():
    session = clean_session_file()
    session = session[['start_local', 'end_local', 'start_date', 'end_date', 'start_hour', 'start_hour_decimal']]

    plt.figure(figsize=(15,8))
    sns.set_theme()
    sns.set_palette("pastel")
    sns.set_context("paper", rc={'lines.linewidth': 1.5})
    sns.set_style("darkgrid", {"axes.facecolor": ".9"})
    g = sns.scatterplot(data=session, y='start_hour_decimal', x='start_date')
    g.set(xlabel='Date', ylabel='Hour', title='Hourly Reading Sessions')
    
    y_ticks = list(range(0,25))
    y_labels = ['Midnight','1 am','2 am','3 am','4 am','5 am','6 am','7 am','8 am','9 am','10 am','11 am',
                '12 pm','1 pm','2 pm','3 pm','4 pm','5 pm','6 pm','7 pm','8 pm','9 pm','10 pm','11 pm', '12 am']

    g.set_yticks(y_ticks)
    g.set_yticklabels(y_labels)

    months = session['start_date'].dt.to_period('M').drop_duplicates()

    for m in months:
        month_start = m.to_timestamp()
        plt.axvline(month_start, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)

    g.set_xticks([m.to_timestamp() for m in months])
    g.set_xticklabels([m.strftime('%b') for m in months])
    plt.tight_layout()
    plt.savefig("graphs/hourly_stats.png", dpi=300, bbox_inches='tight')


def main():
    # print reading stats
    print('~~~~~~~~~~~~~~~~~~~~~~~~ Kindle Reading Analysis For Alia ~~~~~~~~~~~~~~~~~~~~~~~~')
    _, stats, total_sec = reading_totals()
    print(f"Total Time Spent Reading: {int(stats[0])} days, {int(stats[1])} hours, {int(stats[2])} minutes, and {int(stats[3])} seconds.")

    print()
    weekly_avg_time()
    totalBooksRead()

    print()
    _, kindle_pgs = totalPagesRead()
    shortest_longest_book()
    avg_per_page = int(total_sec/kindle_pgs)
    print(f'That is roughly {avg_per_page} seconds per page on a Kindle.')

    print()
    sessionCount()

    print()
    faveAuthors()

    hourlyReading()


if __name__ == "__main__":
    main()