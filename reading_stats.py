import pandas as pd
from datetime import datetime, date
import seaborn as sns
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# READING DATASETS
# all_books = pd.read_csv('DocumentMetadata.csv', parse_dates=['EntryCreationDate'])
# days_read = pd.read_csv('ReadingInsightsDayUnits.csv', parse_dates=['reading_tracked_on_day'])
# book_session = pd.read_csv('reading-insights-sessions.csv', parse_dates=['end_time', 'start_time'])
# session = pd.read_csv('ReadingSession.csv', parse_dates=['start_timestamp', 'end_timestamp'])
completed_books = pd.read_csv('TitlesCompleted.csv')

# FILNAMES
readingInsights = 'Kindle.reading-insights-sessions_with_adjustments.csv'
readingSession = 'Kindle.Devices.ReadingSession.csv'
gdLibrary = 'goodreads_library_export.csv'

########################################################
############ READING ALL DATASETS ######################

def clean_session_file():
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

    book_session = pd.read_csv('Kindle.reading-insights-sessions_with_adjustments.csv')
    book_session['start_time'] = pd.to_datetime(book_session["start_time"], format='mixed')
    book_session['end_time'] = pd.to_datetime(book_session["end_time"], format='mixed')
    book_session['start_local'] = book_session['start_time'].dt.tz_convert('America/Vancouver')
    book_session['end_local'] = book_session['end_time'].dt.tz_convert('America/Vancouver')

    book_session['start_date'] = pd.to_datetime(book_session['start_local'].dt.date)
    book_session['end_date'] = pd.to_datetime(book_session['end_local'].dt.date)
    book_session.rename(columns={'product_name' : 'book_title'}, inplace=True)

    return book_session

def clean_goodreads():
    goodreads = pd.read_csv(gdLibrary)
    goodreads = goodreads.iloc[:, 0:16]
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
    session = clean_session_file(readingInsights)

    # TOTAL TIME PER DAY (FOR VISUALIZATION)
    read_per_day = session.groupby('start_date')['total_reading_millis'].sum().reset_index()
    read_per_day['total_minutes'] = (read_per_day['total_reading_millis']/60000).round(2)
    read_per_day['total_hours'] = (read_per_day['total_reading_millis']/3600000).round(2)

    read_per_day.sort_values(by='start_date', inplace=True)

    # CALCULATE TOTAL READING TIME SO FAR
    total_reading_sec = (session['total_reading_millis'].sum()/1000).round(2)
    days = int(total_reading_sec // (24 * 3600))
    total_reading_sec %= (24 * 3600)

    hours = int(total_reading_sec // 3600)
    total_reading_sec %= 3600

    minutes = int(total_reading_sec // 60)
    seconds = int(total_reading_sec % 60)

    overall_stat = (days, hours, minutes, seconds)

    #print(f"Total Time Spent Reading: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds.")
    
    return read_per_day, overall_stat


# visualize the average reading time for each day of the week
# todo: limit the rows to this year only, when there is enough data
def weekly_avg_time():

    read_per_day, _ = reading_totals()
    read_per_day['day_of_week'] = read_per_day['start_date'].dt.day_name()

    weekly = read_per_day.groupby('day_of_week')['total_minutes'].mean().reset_index()

    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    plt.figure(figsize=(8,4))
    sns.set_theme()
    sns.set_palette(sns.color_palette("husl", 8))
    g = sns.barplot(data=weekly, y='total_minutes', x='day_of_week', order=week_order)
    g.set(xlabel='Day of Week', ylabel='Minutes', title='Average Reading Time per Day')
    g.yaxis.set_major_locator(MultipleLocator(60))
    plt.show()


# book that took the shortest and longest amount of time to complete
# need goodreads data: only total rows that is before the completion date in goodreads dataset
def shortest_longest_book():
    insights = clean_book_insights()
    _, date_read = totalBooksRead()
    completed_books = pd.merge(insights, date_read, how='left', left_on='book_title', right_on='Title')
    completed_books = completed_books[completed_books['Date Read'].notna()]
    completed_books = completed_books[completed_books['start_date'] <= completed_books['Date Read']]
    #print(completed_books)

    per_book = completed_books.groupby('book_title')['total_reading_milliseconds'].sum().reset_index()
    per_book['total_seconds'] = (per_book['total_reading_milliseconds']/1000).round(2)
    #print(per_book)

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
    curr_year = date.today().year

    goodreads = clean_goodreads()
    completed_books = goodreads[goodreads['Date Read'].notna()]
    completed_books = completed_books[(completed_books['Year Read'] == 2025) | (completed_books['Year Read'] == 2026)]
    total_pages = completed_books['Number of Pages'].sum()

    return total_pages


def totalBooksRead():
    #current_year = date.today().year

    library = clean_goodreads()
    #books_this_year = library[library['Year Read'] == current_year]
    two_years = library[(library['Year Read'] == 2025) | (library['Year Read'] == 2026)]
    book_count = int(two_years['Date Read'].count())
    books = two_years[['Title', 'Date Read']]

    print(f'You completed {book_count} books in the last two years!')

    print('You read the following books:')
    for i in range(book_count):
        print(f'{i+1}. {two_years['Title'].values[i]} on {two_years['Date Read'].values[i]}')

    return book_count, books


# not done, multi-axis plot not showing
def bookByMonth():
    current_year = date.today().year
    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    library = clean_goodreads()

    books_this_year = library[(library['Year Read'] == current_year)]
    grouped_months = books_this_year.groupby('Month Name').agg({'Title': 'count', 'Number of Pages' : 'sum'})
    grouped_months = grouped_months.reindex(month_order, fill_value=0).reset_index()

    grouped_months['Month Name'] = pd.Categorical(
        grouped_months['Month Name'],
        categories=month_order,
        ordered=True
    )
    grouped_months = grouped_months.sort_values('Month Name')
    #print(grouped_months)

    # PLOTTING ...
    plt.figure(figsize=(15,6))

    sns.set_theme(style="darkgrid")
    sns.set_context("paper", rc={'lines.linewidth': 1.8})
    #sns.set_palette("pastel")
    pastel_colors = ["#A8DADC", "#FFCAD4"]

    fig, ax1 = plt.subplots(figsize=(15,6))

    sns.lineplot(
        data=grouped_months,
        x='Month Name',
        y='Title',
        marker='o',
        ax=ax1,
        label='Books Read',
        color=pastel_colors[0]
    )

    ax1.set_ylabel('Number of Books')
    #ax1.tick_params(axis='y')

    # 📖 Pages line (secondary axis)
    ax2 = ax1.twinx()

    sns.lineplot(
        data=grouped_months,
        x='Month Name',
        y='Number of Pages',
        marker='o',
        ax=ax2,
        label='Pages Read',
        color=pastel_colors[1]
    )

    ax2.set_ylabel('Number of Pages')
    #ax2.tick_params(axis='y', labelcolor='tab:red')

    # Combine legends
    lines = ax1.lines + ax2.lines
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.xticks(rotation=45)
    plt.title("Books and Pages Read Per Month")
    plt.xlabel('Month')
    plt.tight_layout()
    plt.show()


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

    plt.show()


def main():
    hourlyReading()



if __name__ == "__main__":
    main()