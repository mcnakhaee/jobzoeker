# standardize the following lines of code to use pip8 standards
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import langid
import openai
import os

x1 = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist',
                         'data engineer', 'Data Reporting','Big Data','Statistical Analyst',
                         'data pipeline', 'R Shiny','R Developer']
x2 = ['programm manager','HR','people operations',
                        'program coordinator',
                        'event coordinator','event manager','events',
                        'training', 'training coordinator',
                        'partnerships']

locations = ['Den Haag','Amsterdam','Rotterdam','Delft','Utrecht','Leiden','Zuid-Holland','Werk van thuis, NL']
openai_key = api_key = os.getenv("OPENAI_KEY")
client = openai.OpenAI(api_key=openai_key)

pd.set_option('display.max_colwidth', None)

# Function to truncate text in the 'Description' column
def truncate_text(text, max_length=30):
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    else:
        return text

def get_data():
    df = pd.read_csv('jobs.csv')
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    df = df.sort_values(by='date_posted', ascending=False)
    return df


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

# Function to filter dataframe based on description keywords
def filter_dataframe(df, column, keyword):
    if keyword:
        return df[df[column].str.contains(keyword, case=False, na=False)]
    return df

# Function to display filtered dataframe with interactive elements
def display_filtered_data(filtered_df):
    # Select columns to display
    cols = filtered_df.columns.tolist()
    cols_st = st.sidebar.multiselect(
        "Columns to Display",
        cols,
        default=['title', 'date_posted', 'search_term', 'company', 'location', 'job_url', 'site', 'description', 'lang']
    )
    filtered_df = filtered_df[cols_st]

    # Search term filter
    search_terms = filtered_df['search_term'].unique().tolist()
    selected_terms = st.sidebar.multiselect("Search Term", search_terms, default=search_terms)
    filtered_df = filtered_df[filtered_df['search_term'].isin(selected_terms)]

    # Location filter
    #locations = filtered_df['location'].unique().tolist()
    #selected_locations = st.sidebar.multiselect("Location", locations, default=locations)
    #filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]

    # Site filter
    sites = filtered_df['site'].unique().tolist()
    selected_sites = st.sidebar.multiselect("Site", sites, default=sites)
    filtered_df = filtered_df[filtered_df['site'].isin(selected_sites)]

    # Description filter
    filter_keyword = st.sidebar.text_input("Enter description keyword to filter")
    filtered_df = filter_dataframe(filtered_df, 'description', filter_keyword)

    # Select and display a row's details
    if not filtered_df.empty:
        selected_row_index = st.selectbox("Select a row", filtered_df.index)
        selected_description = filtered_df.loc[selected_row_index, 'description']
        st.text_area("Description", selected_description)
        job_title = filtered_df.loc[selected_row_index, 'title']
        company = filtered_df.loc[selected_row_index, 'company']
        st.write(f"**ID:** **{job_title} at {company}**")

        # Generate and display response for job description analysis
        job_description_prompt = f"""
        This is a job description in the field of data science.
        Your task is to summarize the text into the technologies needed for this job, minimum years of experience, education requirement, and write each of them into a single sentence. 
        If any of them is not provided, please specify it as 'not provided'. 
        Also, summarize the profile of the ideal candidate for this job in 1 or 2 sentences. 
        Extract the responsibilities of the candidate in 1 or 2 sentences. Based on the responsibilities, provide a few resources/learning materials to get started with this job title:
        {selected_description}
        """
        response = get_completion(job_description_prompt)
        st.write(response)

        # Generate and display response for company profile analysis
        company_prompt = f"""
        This is the name of the company that posted the job. Your task is to summarize the company profile, mission, culture, and values in 1 or 2 sentences:
        {company}
        """
        response = get_completion(company_prompt)
        st.write(response)

    # Option to delete selected rows
    selected_row_indices = st.multiselect("Select rows to delete", filtered_df.index)
    if st.button("Delete Selected Rows"):
        df.drop(index=selected_row_indices, inplace=True)
        df.to_csv("jobs.csv", index=False)
        st.success("Selected rows deleted successfully!")

    # Display the filtered dataframe
    st.table(filtered_df.style.format({'description': truncate_text}))

# Main function to handle page navigation and display
def main():
    st.title('Job Zoeker')

    # Fetch the data
    df = get_data()

    # Sidebar for date filter
    st.sidebar.header('Filters')
    end_date = st.sidebar.date_input("End date", datetime.now())
    start_date = end_date - timedelta(days=30)
    df['date_posted'] = pd.to_datetime(df['date_posted'])  # Ensure date_posted is in datetime format
    # Convert start_date and end_date to pandas datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = df[(df['date_posted'] >= start_date) & (df['date_posted'] <= end_date)]

    # Page navigation
    page = st.sidebar.selectbox("Select Page", ["Muhammad", "Andreea"])

    if page == "Muhammad":
        filtered_df_x1 = filtered_df[filtered_df['search_term'].isin(x1)]
        display_filtered_data(filtered_df_x1)
    elif page == "Andreea":
        filtered_df_x2 = filtered_df[filtered_df['search_term'].isin(x2)]
        display_filtered_data(filtered_df_x2)

# Run the app
if __name__ == "__main__":
    main()