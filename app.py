import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import langid
pd.set_option('display.max_colwidth', None)
# Function to identify language using langid


def detect_language(text):
    lang, _ = langid.classify(text)
    return lang == 'en'


def detect_lang(x):
    try:
        lang, _ = langid.classify(text)
        return lang
    except:
        return 'not_detected'


def get_data():
    df = pd.read_csv('jobs.csv')
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    df = df[['title', 'company', 'search_term', "job_url", 'date_posted', 'description',
             ]].sort_values(by='date_posted', ascending=False)
    df = df[~df['title'].str.contains('Intern', case=False, na=False)]
    # Apply the function to filter English rows
    df['lang'] = df['description'].apply(lambda x: detect_lang(x))
    return df


def main():
    st.title('Streamlit DataFrame App')

    # Load sample data
    df = get_data()

    # Display dataframe
    st.write('### DataFrame')
    # st.dataframe(df)

    # Sidebar - Date selection
    # date_column = st.sidebar.selectbox('Choose a Date Column', df.select_dtypes(include='datetime64').columns)
    st.sidebar.header('Select Date')

    # start_date = st.sidebar.date_input("Start date", min(df['date_posted']))
    end_date = st.date_input("End date", max(df['date_posted']))
    # Calculate the start and end date for the last month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=end_date.day)
    filtered_df = df[(df['date_posted'] >= start_date)
                     & (df['date_posted'] <= end_date)]

    # Sidebar - Categorical column selection
    # st.sidebar.header('Select Categorical Column')
    # cat_column = st.sidebar.selectbox(
    #    'Choose a Categorical Column', df.select_dtypes(include='object').columns)
    # st.sidebar.header('Select Categorical Column')
    langs = filtered_df.lang.unique().tolist()
    langs_st = st.sidebar.multiselect(
        "Lang",
        langs,
        langs[0])
    filtered_df = filtered_df[filtered_df['lang'].isin(langs_st)]
    search_terms = filtered_df.search_term.unique().tolist()
    sterms = st.sidebar.multiselect(
        "Search Term",
        search_terms,
        search_terms[0:2])

    filtered_df = filtered_df[filtered_df['search_term'].isin(sterms)]
    """titles = filtered_df.title.unique().tolist()
    st_titles = st.multiselect(
    "Job Titles",
    titles,
    titles)"""
    # Filter dataframe based on selections
    # filtered_df = df[[date_column, cat_column]]

    # filtered_df = filtered_df[filtered_df['title'].isin(st_titles)]
    # Display filtered dataframe
    st.write('### Filtered DataFrame')
    st.dataframe(filtered_df)
    # st.write(df.style.format({'job_url': lambda x: f'<a href="{x}" target="_blank">{x}</a>'}, escape='html'))


if __name__ == '__main__':
    main()
