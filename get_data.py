import time
from jobspy import scrape_jobs
import pandas as pd
search_terms = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist']
# Indeed
df_jobs = []


def collect_data():
    for search_term in search_terms:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=search_term,
            location="Netherlands",
            results_wanted=30,
            country_indeed='Netherlands'  # only needed for indeed / glassdoor
        )
        jobs['search_term'] = search_term
        df_jobs.append(jobs)
        time.sleep(40)

    # Linkedin
    for search_term in search_terms:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            location="Netherlands",
            results_wanted=30,
            country_indeed='Netherlands'  # only needed for indeed / glassdoor
        )
        jobs['search_term'] = search_term
        df_jobs.append(jobs)
        time.sleep(30)

    merged_df = pd.concat(df_jobs, ignore_index=True)
    merged_df.to_csv('jobs.csv', index=False)


def main():
    # collect_data()
    print('x')


if __name__ == "__main__":
    main()
