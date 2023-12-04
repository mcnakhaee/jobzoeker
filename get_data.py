import time
from jobspy import scrape_jobs
import pandas as pd
search_terms = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist']
# Indeed
df_jobs = []
old_data = pd.read_csv('jobs.csv')


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
    all_jobs.to_csv('jobs.csv', index=False)


def main():
    collect_data()


if __name__ == "__main__":
    main()
