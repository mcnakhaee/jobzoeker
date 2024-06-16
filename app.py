import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import langid
import openai
import os
import os
from secret import *
openai_key = get_openai_key()
openai_key = get_openai_key()
client = openai.OpenAI(api_key=openai_key)

pd.set_option('display.max_colwidth', None)
# Function to format URLs as clickable links
def format_url(url):
    return f'<a href="{url}" target="_blank">{url}</a>'

# Function to truncate text in the 'Description' column
def truncate_text(text, max_length=30):
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    else:
        return text


def detect_language(text):
    lang, _ = langid.classify(text)
    return lang == 'en'


def detect_lang(x):
    try:
        lang, _ = langid.classify(x)
        return lang
    except:
        return 'not_detected'


def get_data():
    df = pd.read_csv('jobs.csv')
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    df = df.sort_values(by='date_posted', ascending=False)
    df = df[~df['title'].str.contains('Intern', case=False, na=False)]
    # Apply the function to filter English rows
    df['lang'] = df['description'].apply(lambda x: detect_lang(x))
    df = df[df['lang'] == 'en']
    return df

# Function to filter DataFrame based on user input
def filter_dataframe(data_frame, column, keyword):
    if keyword:
        return data_frame[data_frame[column].str.contains(keyword, case=False)]
    else:
        return data_frame

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def main():
    st.title('Job Zoeker')

    # Load sample data
    df = get_data()

    # date_column = st.sidebar.selectbox('Choose a Date Column', df.select_dtypes(include='datetime64').columns)
    st.sidebar.header('Select Date')
    end_date = st.sidebar.date_input("End date", max(df['date_posted']))
    # Calculate the start and end date for the last month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    filtered_df = df[(df['date_posted'] >= start_date)
                     & (df['date_posted'] <= end_date)]

    cols = filtered_df.columns.tolist()
    cols_st = st.sidebar.multiselect(
        "Cols",
        cols,
        ['title', 'date_posted', 'search_term', 'company', 'job_url', 'site', 'description','lang'])
    filtered_df = filtered_df[cols_st]

    search_terms = filtered_df.search_term.unique().tolist()
    sterms = st.sidebar.multiselect(
        "Search Term",
        search_terms,
        search_terms[0:2])

    filtered_df = filtered_df[filtered_df['search_term'].isin(sterms)]

    sites = filtered_df.site.unique().tolist()
    site_st = st.sidebar.multiselect(
        "Site",
        sites,
        sites[0])
    filtered_df = filtered_df[filtered_df['site'].isin(site_st)]
    # language filter
    langs = filtered_df.site.unique().tolist()

    # Search bar
    filter_keyword = st.sidebar.text_input(f"Enter description Value to Filter")

    # Apply filter to DataFrame
    filtered_df = filter_dataframe(filtered_df, 'description', filter_keyword)

    selected_row_index = st.selectbox("Select a row", filtered_df.index)
    # Display the selected row's 'description' as a text field
    selected_description = filtered_df.loc[selected_row_index, 'description']
    description_input = st.text_area("Description", selected_description)
    st.write("**ID:**", "**" + filtered_df.loc[selected_row_index, 'title'] +
             ' at ' + filtered_df.loc[selected_row_index, 'company'] + "**")

    # ChatGPT
    prompt = f"""
    This is a job description in the field of data science,
    your task is to summarize the text into the technologies needed for this job, minimum years of experience, education requrement and write each of them them into a single sentence.
    if any of them is not provided please specify it as 'not provided'.
    Also summarize the profile of the ideal candidate for this job in 1 or 2 sentences.
    Also extract the responsibilities of the candidate in 1 or 2 sentences.
    based on the responsibilties provide a few resources/learning materials to get started with this job title 
    ```{selected_description}```
    """

    response = get_completion(prompt)
    st.write(response)
    # Display DataFrame with checkboxes for row selection
    selected_row_indices = st.multiselect("Select rows to delete", df.index)
    # Display a button to delete selected rows
    if st.button("Delete Selected Rows"):
        # Delete selected rows from the DataFrame
        df.drop(index=selected_row_indices, inplace=True)

        # Save the updated DataFrame to the source file (e.g., CSV)
        df.to_csv("jobs.csv", index=False)

        # Display a confirmation message
        st.success("Selected rows deleted successfully!")

    #st.dataframe(filtered_df)
    st.table(filtered_df.style.format({'description': truncate_text}))

if __name__ == '__main__':
    main()
