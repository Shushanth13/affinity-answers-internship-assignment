# Affinity Answers - Full Stack Engineer Internship Assignment

This repository contains my solutions for all three questions in the assignment.

| Folder | Description |
|--------|-------------|
| `q1_scraper/` | Python scraper for mdcomputers.in (`scrape_mdcomputers.py`, README, and sample HTML used for testing) |
| `q2_sql/` | SQL queries for the Rfam database (`queries.sql` and README) |
| `q3_shell/` | Shell script for the S&P 500 dataset (`sp500_by_founding_year.sh`) |

Each folder includes a README explaining the approach and implementation.

## Notes

- **Q1:** The scraper was tested using a sample HTML file because the live mdcomputers.in website was not accessible from my current environment. A fallback parser is also included to handle small HTML structure changes.

- **Q2:** The SQL queries were written using the official Rfam schema and documentation. I couldn't execute them because the public Rfam MySQL server was not accessible from my current environment.

- **Q3:** The shell script was tested successfully against the live S&P 500 CSV file and produces the expected output.
