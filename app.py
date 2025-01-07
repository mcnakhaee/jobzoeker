import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from notion_client import Client
import openai

# Fetch environment variables
openai_key = os.getenv("OPENAI_KEY")
notion_key = os.getenv("NOTION_KEY")
parent_page_id = os.getenv("PARENT_PAGE_ID")

# Initialize OpenAI and Notion clients
openai_client = openai.OpenAI(api_key=openai_key)
notion = Client(auth=notion_key)

pd.set_option('display.max_colwidth', None)
database_name = "jobs"

# Function to create a new page in Notion
def create_notion_page(parent_page_id, title):
    """Create a new page in Notion."""
    return notion.pages.create(
        parent={"page_id": parent_page_id},
        properties={"title": [{"text": {"content": title}}]}
    )

# Function to truncate text
def truncate_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length-3] + "..."

# Function to load data from CSV
def get_data():
    df = pd.read_csv('jobs.csv')
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df.sort_values(by='date_posted', ascending=False)

# Function to filter dataframe
def filter_dataframe(data_frame, column, keyword):
    return data_frame[data_frame[column].str.contains(keyword, case=False, na=False)]

# Function to get completion from OpenAI
def get_completion(prompt, model="gpt-3.5-turbo"):
    response = openai_client.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()

# Function to create a new Notion database
def create_database(database_name, parent_page_id):
    return notion.databases.create(
        parent={"page_id": parent_page_id},
        title=[{"text": {"content": database_name}}],
        properties={
            "title": {"title": {}},
            "description": {"rich_text": {}},
            "job_url": {"url": {}},
            "location": {"rich_text": {}},
            "company": {"rich_text": {}},
            "date_posted": {"date": {}}
        }
    )

# Main function to handle Streamlit app
def main():
    st.title('Job Zoeker')
    df = get_data()
    start_date = st.sidebar.date_input("Start date", datetime.now() - timedelta(days=30))
    end_date = st.sidebar.date_input("End date", datetime.now())
    filtered_df = df[(df['date_posted'] >= start_date) & (df['date_posted'] <= end_date)]
    search_keyword = st.sidebar.text_input("Search keyword")
    if search_keyword:
        filtered_df = filter_dataframe(filtered_df, 'description', search_keyword)

    st.table(filtered_df)

if __name__ == "__main__":
    main()
