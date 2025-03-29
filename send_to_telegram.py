import streamlit as st
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import httpx
import time
import random
import os
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response.json()

def send_to_telegram_df(df):
    for _, row in df.iterrows():
        message = f"{row['title']}\nPrice: **{row['price']}**\n{row['product_url']}"
        send_to_telegram(message)

def search_and_send_to_telegram(search_terms, cat_1=31, cat_2=480):
    try:
        last_items = pd.read_csv('items_today.csv')
    except FileNotFoundError:
        last_items = pd.DataFrame(columns=['item'])

    results = []
    last_item_ids = set(last_items['item'].values)
    for term in search_terms:
        items = get_items(term, cat_1, cat_2)
        filtered_items = [item for item in items if
                          term.lower() in item['title'].lower() and item['itemId'] not in last_item_ids]
        results.extend(filtered_items)
        time.sleep(random.uniform(10, 25))

    latest_items = get_item_title(results)
    latest_items = latest_items[latest_items['dates'] == 'Vandaag']
    send_to_telegram_df(latest_items)
    df_items = pd.concat([latest_items, last_items])
    df_items.to_csv('items_today.csv', index=False)
    return df_items