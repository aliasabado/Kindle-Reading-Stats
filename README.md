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

## Results

Terminal output example for `reading-stats.py`

```text
~~~~~~~~~~~~~~~~~~~~~~~~ Kindle Reading Analysis For Alia ~~~~~~~~~~~~~~~~~~~~~~~~
Total Time Spent Reading: 4 days, 7 hours, 14 minutes, and 10 seconds.

You completed 3 books this year!
You read the following books:
1. Caraval on 2026/01/24
2. The Jasad Heir on 2026/02/11
3. The Jasad Crown on 2026/02/22

This year, you've completed the equivalent of 1,611 physical book pages and read 11,614 pages on your Kindle.
Shortest: Caraval - 11.62 hours.
Longest: The Jasad Crown - 29.07 hours.
That is roughly 32 seconds per page on a Kindle.

You picked up your kindle for 55 separate days and opened it 576 different times.

Your all-time favourite authors are...
Rick Riordan with a total of 10 books read.
J.K. Rowling with a total of 8 books read.
Mary E. Pearson with a total of 6 books read.
Holly Black with a total of 5 books read.
Leigh Bardugo with a total of 4 books read.
Suzanne Collins with a total of 4 books read.
Ali Hazelwood with a total of 2 books read.
Sara  Hashem with a total of 2 books read.
Emily Henry with a total of 2 books read.
Sarah Hogle with a total of 2 books read.
```

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
├── Kindle Reading Report.pbix
├── bookGenres.py
├── reading-stats.py
└── README.md
```

## Power BI Dashboard

In addition to the previous analysis, I created a Power BI dashboard to further visualize my reading habits over time and across individual books. The Power BI report is included as a downloadable .pbix file in this repository. 

The report contains three tabs: Total Reading Time, Reading Per Book, and Monthly Trend. It also includes Year/Month and Book Title slicers, allowing the user to filter the visualizations by a specific time period or book.

The raw data included in this report is from older reading data and has been limited to the first three months of the dataset to protect privacy.

### Report Breakdown

#### Total Reading Time
Visualizes total reading time over time. This page includes a line chart that can be drilled down into different time periods, as well as a stacked bar chart showing the total reading time for each book.

#### Reading Per Book
Uses a line chart to visualize reading activity for each book over time. Each book is represented separately using the chart legend, allowing reading patterns across different books to be compared.

#### Monthly Trend
Uses a line chart to show monthly reading trends, including the total number of books opened and the total hours read each month.

## Purpose

This project was created to explore my personal reading behaviour using real-world data. It combines data from multiple sources to answer questions such as what genres are being read most often, how much time is spent reading, when reading occurs, how many books are completed, and which authors are read most frequently.