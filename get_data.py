import time
from jobspy import scrape_jobs
import pandas as pd
import langid
from datetime import datetime, timedelta

search_terms = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist']
# Indeed
# Get today's date
today = datetime.today()

df_jobs = []
old_data = pd.read_csv('jobs.csv')


def detect_language(text):
    lang, _ = langid.classify(text)
    return lang == 'en'


def detect_lang(x):
    try:
        lang, _ = langid.classify(x)
        return lang
    except:
        return 'not_detected'

def collect_data():
    for search_term in search_terms:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=search_term,
            location="Netherlands",
            results_wanted=40,
            country_indeed='Netherlands'  # only needed for indeed / glassdoor
        )
        jobs['search_term'] = search_term
        df_jobs.append(jobs)
        time.sleep(60)

    # Linkedin
    for search_term in search_terms:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            location="Netherlands",
            results_wanted=40,
            country_indeed='Netherlands'  # only needed for indeed / glassdoor
        )
        jobs['search_term'] = search_term
        df_jobs.append(jobs)
        time.sleep(60)

    merged_df = pd.concat(df_jobs, ignore_index=True)
    all_jobs = pd.concat([old_data,merged_df], ignore_index=True)
    all_jobs =all_jobs.drop_duplicates()
    all_jobs['lang'] = all_jobs['description'].apply(lambda x: detect_lang(x))
    filtered_df = all_jobs[all_jobs['lang'] == 'en']
    filtered_df = filtered_df[filtered_df['description'].str.contains('Python', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['title'].str.contains('PhD', case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['title'].str.contains('Manager', case=False, na=False)]
    # Convert 'date' column to datetime
    filtered_df['date_posted'] = pd.to_datetime(filtered_df['date_posted'])
    # Calculate the first and last day of the last month
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    filtered_df = filtered_df[(filtered_df['date_posted'] >= first_day_last_month) & (filtered_df['date_posted'] <= last_day_last_month)]
    filtered_df.to_csv('jobs.csv', index=False)
    all_jobs.to_csv('all_jobs.csv', index=False)


def main():
    collect_data()


if __name__ == "__main__":
    main()
