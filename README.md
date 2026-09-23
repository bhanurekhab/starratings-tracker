# Aged Care Star Ratings — Data Analysis

## Live Dashboard
[Click here to view the interactive dashboard](https://bhanurekhab.github.io/starratings-tracker/StarRatings_Dashboard.html)

## About This Project
The Australian Government publishes star ratings for residential aged care services every quarter on the GEN Aged Care Data website. The ratings cover overall quality, compliance, staffing, resident experience and quality measures. Each quarter the government releases a new CSV file but the column names, formats and structures change between releases which makes it difficult to track trends over time.

I wanted to see how aged care quality has changed across Australia so I built a data pipeline from scratch to solve this problem.

## What I Did
1. Downloaded 13 quarterly CSV files from the GEN Aged Care Data website covering May 2023 to May 2026
2. Each file had different column names and formats so I built a Python ETL pipeline that reads each file, standardises the column names, cleans the data and merges everything into one dataset
3. The pipeline checks for duplicates, missing values, incorrect formats and data inconsistencies and logs every issue it finds
4. I merged all 13 files into a single clean dataset of 34,000 rows across 2,590 aged care services
5. I built an interactive HTML dashboard with 3 pages so anyone can explore the data in a browser without installing anything
6. I also built a Power BI version of the dashboard with DAX measures and calculated columns

## Dashboard Pages
- **National Overview** — total services, national average rating, percentage at 4+ stars, rating distribution by quarter and average rating by state
- **Rating Movement** — how many services improved, declined or stayed steady compared to the previous quarter, and which services had the biggest changes
- **Watchlist** — services currently rated 3 stars or below that may need attention

## Key Findings (May 2026)
- 2,590 residential aged care services nationally
- National average overall rating: 3.83 stars
- 65.3% of services rated 4 stars or above
- Services rated 1-2 stars dropped from 121 (May 2023) to 1 (May 2026). Of the original 121 low-rated services, 84 genuinely improved their rating to 3 or 4 stars, 28 were closed or deregistered, and 9 currently have no rating
- NT has the highest average rating (4.00), SA the lowest (3.67)
- 485 services are currently rated 3 stars or below

## Tools Used
- Python (Pandas, NumPy) — data cleaning and ETL pipeline
- Power BI — dashboard with DAX measures and calculated columns
- HTML, CSS, JavaScript — standalone interactive dashboard
- SQL — data querying and validation

## Files
- `StarRatings_Dashboard.html` — Interactive dashboard (open in browser or use the live link above)
- `01_clean_star_ratings.py` — Python ETL pipeline
- `star_ratings_all_quarters.csv` — Clean merged dataset (34,000 rows)
- `star_ratings_latest.csv` — Latest quarter data only
- `star_ratings_watchlist.csv` — Services rated 2 stars or below
- `issues_log.txt` — Data quality issues found during cleaning
- `StarRatings_Portfolio.pdf` — Project summary

## How to Run the Pipeline
```bash
pip install pandas numpy
python 01_clean_star_ratings.py
```

## Data Source
Australian Government Department of Health and Aged Care — GEN Aged Care Data
https://www.gen-agedcaredata.gov.au/topics/quality-indicators
