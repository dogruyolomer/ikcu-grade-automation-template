# IKCU Grade Automation Bot

A Python-based cloud automation tool designed to monitor the Katip Celebi University (IKCU) Student Information System. It automatically checks for newly published grades and sends an email notification when an update is detected.

## Overview

This project demonstrates the use of continuous integration (CI) pipelines and web scraping techniques to solve a real-world workflow problem. By utilizing GitHub Actions, the script runs entirely in the cloud, eliminating the need for a dedicated local server or constant manual checking.

## Key Features

* Automated Execution: Runs on a 30-minute interval using GitHub Actions cron scheduling.
* Advanced Authentication: Successfully authenticates by extracting dynamic request verification tokens and submitting POST requests directly to the login endpoint, overcoming standard cloud-traffic restrictions.
* Secure Configuration: All sensitive data (student credentials, app passwords, email addresses) are managed securely via GitHub Secrets.
* Delta Comparison: Stores the latest grade state in a JSON database and performs a delta check to ensure notifications are only sent for actual changes.

## Technical Stack

* Language: Python 3.10
* Core Libraries: Requests, BeautifulSoup4
* Automation & CI/CD: GitHub Actions
* Notification System: Built-in SMTP library

## How It Works

1. The GitHub Action workflow is triggered automatically based on the defined schedule.
2. The script establishes a secure session and fetches the initial token from the root directory.
3. The bot authenticates using a POST payload containing the extracted token and repository secrets.
4. It navigates to the grades endpoint and parses the HTML tables to extract current assessments.
5. The extracted data is compared against the stored `grades_data.json` file.
6. If a new entry or grade change is detected, an email alert is dispatched, and the JSON file is updated via an automated Git commit.

## Setup Requirements

To deploy this architecture, the following environmental variables must be configured in GitHub Secrets:
* `UBS_USERNAME`
* `UBS_PASSWORD`
* `EMAIL_USER`
* `EMAIL_PASS` (Application-specific password)
* `RECEIVER_EMAIL`

Additionally, the GitHub Actions runner requires "Read and write permissions" to update the local JSON database after a successful scan.

## Disclaimer

This project was developed strictly for educational purposes and portfolio demonstration. It interacts with the university system using standard HTTP requests and respects server load limits by running at extended 30-minute intervals.
