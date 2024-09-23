# standardize the following lines of code to use pip8 standards
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import langid
import openai
import os
from notion_client import Client



x1 = ['r', 'ggplot', 'data analyst', 'analytics engineer',
                'data scientist', 'pyspark', 'data visualization', 'data journalist',
                         'data engineer', 'Data Reporting','Big Data','Statistical Analyst',
                         'data pipeline', 'R Shiny','R Developer']
x2 = ['programm manager','HR','people operations',
                        'program coordinator',
                        'event coordinator','event manager','events',
                        'training', 'training coordinator',
                        'partnerships']

cities_to_filter = ['Den Haag','Amsterdam','Rotterdam','Delft','Utrecht','Leiden','Zuid-Holland','Werk van thuis, NL']
openai_key = os.getenv("OPENAI_KEY")
notion_key = os.getenv("notion-key")
parent_page_id = notion_key = os.getenv("parent_page_id")

client = openai.OpenAI(api_key=openai_key)
# Initialize a client
notion = Client(auth=notion_key)
pd.set_option('display.max_colwidth', None)
database_name = "jobs"

# Function to create a new page in Notion
def create_notion_page(parent_page_id, title):
    new_page = notion.pages.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        properties={
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    )
    return new_page
# Function to extract the city name (first part before any commas)
def extract_city_name(city):
    return city.split(',')[0].strip()  # Split by comma and take the first part, strip to remove any spaces

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


# Function to search if a database with a certain name exists
def search_database(database_name):
    search_results = notion.search(query=database_name)

    for result in search_results['results']:
        if result['object'] == 'database' and result['title'][0]['text']['content'] == database_name:
            return result['id']

    return None

# Function to create a new Notion database
def create_database(database_name, parent_page_id):
    database = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[
            {
                "type": "text",
                "text": {
                    "content": database_name
                }
            }
        ],
        properties={
            "title": {
                "title": {}
            },
            "description": {
                "rich_text": {}
            },
            "job_url": {
                "url": {}
            },
            "location": {
                "rich_text": {}
            },
            "company": {
                "rich_text": {}
            },
            "date_posted": {
                "date": {}
            }
        }
    )
    return database['id']

# Function to add rows to the Notion database
def add_row_to_notion(row, database_id):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": row["title"]
                        }
                    }
                ]
            },
            "description": {
                "rich_text": [
                    {
                        "text": {
                            "content": row["description"][:200]
                        }
                    }
                ]
            },
            "job_url": {
                "url": row["job_url"]
            },
            "location": {
                "rich_text": [
                    {
                        "text": {
                            "content": row["location"]
                        }
                    }
                ]
            },
            "company": {
                "rich_text": [
                    {
                        "text": {
                            "content": row["company"]
                        }
                    }
                ]
            },
            "date_posted": {
                "date": {
                    "start": row["date_posted"].strftime('%Y-%m-%d')  # Ensure this is a valid ISO 8601 date string (e.g., "2023-09-22")
                }
            }

        }
    )
def add_to_notion(df,database_id,database_name,parent_page_id):
    # If the database doesn't exist, create a new one
    if not database_id:
        print(f"Database '{database_name}' not found. Creating a new database...")
        database_id = create_database(database_name, parent_page_id)
        print(f"New database created with ID: {database_id}")
    else:
        print(f"Database '{database_name}' found with ID: {database_id}")

    # Add rows from the dataframe to the database
    add_row_to_notion(df, database_id)

    print("All rows added to Notion!")

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
    #st.write(filtered_df['location'].value_counts().index)
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
        #filtered_df['city_name'] = filtered_df['location'].apply(extract_city_name)

        #pattern = '|'.join(cities_to_filter)
        #st.write(list(filtered_df['city_name'].value_counts().index))
        # Filter the dataframe based on whether the city column contains any of the specified city names
        #dddf = filtered_df[filtered_df['location'].str.contains(pattern, case=False, regex=True)]
        #st.write(dddf.shape)
        #st.table(dddf.head(5))
        # Generate and display response for job description analysis
        job_description_prompt = f"""
        This is a job description in the field of data science.
        Your task is to summarize the job description and provide the following information in separate lines:
        1.Technologies required for this job,
        2.Minimum years of experience,
        3.Education requirement
        4. Salary (if provided)
        5. Contact person (if provided)
        6. Duration
        7. summarize the company profile, such as size, mission, culture, and values in 1 or 2 sentences
        
        Also based on the job description and the following list of tasks i've done in my current job compose a 3-paragraphs cover letter:
        /Tasks
    - Delivered comprehensive analysis and developed interactive  PowerBI  dashboards for key stakeholders, including the Customer Success and Robotics teams 
    - Designed and implemented robust data models to integrate data from new acquisitions, improving data consistency and accessibility across the organization 
    - Managed and monitored machine learning models for the Customer Intelligence team, ensuring optimal performance and timely updates 
    - Optimized data transformation processes, resulting in significant cost savings of thousands of euros through improved efficiency and resource utilization. 
    - Implemented data quality checks and validation processes 
    style the answer
         
        {selected_description}
        """


    if st.button("Generate summary/cover letter"):
        response = get_completion(job_description_prompt)
        st.write(response)

    if st.button("add to notion"):

        database_id = search_database(database_name)
        df = filtered_df.loc[selected_row_index,['title', 'company','description','date_posted', 'location', 'job_url']]
        add_to_notion(df, database_id, database_name, parent_page_id)
        st.write(df)

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