# Kindle-Reading-Stats

## Overview

This project analyzes personal reading data from both Goodreads and Amazon Kindle to explore reading habits, book genres, and overall reading activity. The project combines data cleaning, API requests, data manipulation, statistical summaries, and visualization to generate insights about books read and reading behaviour.

The project uses Goodreads data to identify books and their genres, while Kindle data is used to analyze reading sessions, reading time, pages read, and reading patterns throughout the day.

## Data Sources

The project uses three datasets:

- Goodreads Library Export – contains information about books, including titles, authors, reading status, dates read, and number of pages.
- Kindle Reading Session Data – contains individual Kindle reading sessions and their timestamps, reading duration, and page flips.
- Kindle Reading Insights Data – contains book-specific reading sessions and reading duration.

Book genre information is retrieved from the OpenLibrary API using ISBN, title, and author information.

## Analysis

### 1. Goodreads Genre Analysis

The genre analysis:

1. Loads and cleans the Goodreads library export.
2. Extracts book titles and ISBN information.
3. Uses the OpenLibrary API to retrieve information about each book.
4. Extracts subjects associated with each book.
5. Identifies common genres and keywords from the subjects.
6. Organizes the genres into a DataFrame.
7. Creates a visualization showing the distribution of genres among books read.

### 2. Kindle Reading Analysis

The Kindle analysis examines personal reading habits by:

1. Loading and cleaning Kindle reading session data.
2. Converting timestamps to the local Vancouver timezone.
3. Calculating total reading time per day.
4. Calculating overall reading time.
5. Examining average reading time by day of the week.
6. Comparing the shortest and longest reading times for completed books.
7. Calculating the number of physical and Kindle pages read.
8. Counting books completed during the year.
9. Identifying the authors with the most books read.
10. Analyzing the times of day when reading sessions occur.

## Visualizations

The project generates visualizations including:

- Genre Distribution – shows the frequency of different genres among books read.
- Average Reading Time per Day – compares average reading time across days of the week.
- Hourly Reading Sessions – visualizes when reading sessions occur throughout the day.

Generated graphs are saved in the graphs/ directory.

## Technologies Used

- Python
- Pandas – data cleaning and manipulation
- Seaborn – statistical visualizations
- Matplotlib – plotting and graph customization
- Requests – accessing the OpenLibrary API
- Python datetime – date and time processing
- Collections / Counter – identifying common genre terms

## Project Structure
```text
.
├── datasets/                           # Local datasets (not included in repo)
│   ├── goodreads_library_export.csv
│   ├── Kindle.reading-insights-sessions_with_adjustments.csv
│   └── Kindle.Devices.ReadingSession.csv
│
├── graphs/
│   ├── genre_distribution.png
│   ├── weekly_avg_reading.png
│   └── hourly_stats.png
│
├── bookGenres.py
├── reading-stats.py
└── README.md
```

## Purpose

This project was created to explore my personal reading behaviour using real-world data. It combines data from multiple sources to answer questions such as what genres are being read most often, how much time is spent reading, when reading occurs, how many books are completed, and which authors are read most frequently.