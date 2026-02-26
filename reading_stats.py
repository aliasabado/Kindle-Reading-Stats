import pandas as pd
from datetime import datetime
import seaborn as sns
import math

# READING DATASETS
all_books = pd.read_csv('DocumentMetadata.csv', parse_dates=['EntryCreationDate'])
days_read = pd.read_csv('ReadingInsightsDayUnits.csv', parse_dates=['reading_tracked_on_day'])
book_session = pd.read_csv('reading-insights-sessions.csv', parse_dates=['end_time', 'start_time'])
session = pd.read_csv('ReadingSession.csv', parse_dates=['start_timestamp', 'end_timestamp'])
completed_books = pd.read_csv('TitlesCompleted.csv')

def reading_totals():
    # TOTAL TIME PER DAY (FOR VISUALIZATION)
    session = session[session['total_reading_millis'].notna()].copy()
    session['start_date'] = pd.to_datetime(session['start_timestamp'])
    session['start_date'] = session['start_date'].dt.date

    session['end_date'] = pd.to_datetime(session['end_timestamp'])
    session['end_date'] = session['end_date'].dt.date

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






def main():
    pass

if __name__ == "__main__":
    main()