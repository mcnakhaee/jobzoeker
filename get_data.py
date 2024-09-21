# refactor the following code to use pip8 standards

import time
from jobspy import scrape_jobs
import pandas as pd
import langid
from datetime import datetime, timedelta


search_terms_muhammad = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist',
                         'data engineer', 'Data Reporting','Big Data','Statistical Analyst',
                         'data pipeline', 'R Shiny','R Developer']
search_terms_andreea = ['NGO','programm manager','HR','people operations',
                        'program coordinator',
                        'event coordinator','event manager',
                         'training coordinator',
                        'partnerships']

search_terms = search_terms_muhammad #+ search_terms_andreea
# Indeed
# Get today's date
today = datetime.today()

df_jobs = []
merged_df = pd.read_csv('jobs.csv')


def detect_language(text):
    """
    Detects the language of a given text.

    Args:
        text (str): The text to detect the language of.

    Returns:
        bool: True if the language is English, False otherwise.
    """
    lang, _ = langid.classify(text)
    return lang == 'en'


def detect_lang(x):
    """
    Detects the language of a given text.

    Args:
        x (str): The text to detect the language of.

    Returns:
        str: The detected language or 'not_detected' if detection fails.
    """
    try:
        lang, _ = langid.classify(x)
        return lang
    except:
        return 'not_detected'


def collect_data(merged_df):
    """
    Collects job data from different sources and filters the results.

    This function scrapes job data from Indeed and LinkedIn for each search term in the `search_terms` list.
    It then merges the scraped data with the existing data from the 'jobs.csv' file.
    The function filters the merged data based on language, keyword, and job title.
    Finally, it saves the filtered data to 'jobs.csv' and saves all the data (including duplicates) to 'all_jobs.csv'.
    """
    for search_term in search_terms:
        for site in ["indeed", "glassdoor", "linkedin"]:
            jobs = scrape_jobs(
                site_name=site,
                search_term=search_term,
                location="Netherlands",
                results_wanted=40,
                hours_old=24*7,
                linkedin_fetch_description=True,
                country_indeed='Netherlands'  # only needed for indeed / glassdoor
            )
            jobs['search_term'] = search_term
            merged_df = pd.concat([merged_df,jobs], ignore_index=True)
            time.sleep(5)


    all_jobs = merged_df.drop_duplicates(subset=['title', 'company','description'], inplace=True)
    all_jobs['lang'] = all_jobs['description'].apply(lambda x: detect_lang(x))
    filtered_df = all_jobs[all_jobs['lang'] == 'en']
    #filtered_df = filtered_df[filtered_df['description'].str.contains('Python', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['title'].str.contains('PhD', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['title'].str.contains('Manager', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['title'].str.contains('Intern', case=False, na=False)]

    # Convert 'date' column to datetime
    filtered_df['date_posted'] = pd.to_datetime(filtered_df['date_posted'])
    # Filter the dataframe for the last 21 days
    last_21_days = today - timedelta(days=21)
    filtered_df = filtered_df[filtered_df['date_posted'] >= last_21_days]

    # Calculate the first and last day of the last month
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    filtered_df = filtered_df[(filtered_df['date_posted'] >= first_day_last_month)]
    filtered_df.drop_duplicates(subset=['title', 'company'], inplace=True)
    filtered_df.to_csv('jobs.csv', index=False)
    all_jobs.to_csv('all_jobs.csv', index=False)


def main():
    """
    Entry point of the script.

    Calls the `collect_data()` function to collect and filter job data.
    """

    collect_data(merged_df)


if __name__ == "__main__":
    main()
