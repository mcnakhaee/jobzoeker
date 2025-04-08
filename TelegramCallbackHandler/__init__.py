
import logging
import json
import os
import azure.functions as func
import requests
from datetime import datetime

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_to_telegram(message: str):
    """Send a message to Telegram"""
    url = f"<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage>"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logging.error(f"Error sending message to Telegram: {e}")
        return {"ok": False, "error": str(e)}

def answer_callback_query(callback_query_id):
    """Acknowledge the callback query"""
    url = f"<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery>"
    data = {"callback_query_id": callback_query_id}
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logging.error(f"Error answering callback query: {e}")
        return {"ok": False, "error": str(e)}

def process_callback(callback_data, user_id):
    """Process callback data from button press"""
    logging.info(f"Processing callback: {callback_data} from user {user_id}")

    try:
        # Split the callback data
        action, job_id = callback_data.split("_", 1)

        # Handle different actions
        if action == "save":
            send_to_telegram(f"✅ Job saved to your favorites")
            logging.info(f"User {user_id} saved job {job_id}")

        elif action == "interested":
            send_to_telegram(f"👍 You've marked this job as interesting")
            logging.info(f"User {user_id} marked interest in job {job_id}")

        elif action == "applied":
            send_to_telegram(f"🚀 You've marked this job as applied")
            logging.info(f"User {user_id} marked job {job_id} as applied")

        # You would store this action in a database or storage
        # Azure Table Storage, Cosmos DB, or Blob Storage would be good options

    except Exception as e:
        logging.error(f"Error processing callback: {e}")
        send_to_telegram(f"Error processing action: {str(e)}")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Telegram webhook triggered')

    try:
        # Get the update from Telegram
        body = req.get_json()
        logging.info(f"Received update: {json.dumps(body)}")

        # Handle callback query (button presses)
        if "callback_query" in body:
            callback_query = body["callback_query"]
            callback_data = callback_query["data"]
            user_id = callback_query["from"]["id"]

            # Process the callback
            process_callback(callback_data, user_id)

            # Answer callback query
            answer_callback_query(callback_query["id"])

        return func.HttpResponse(
            json.dumps({"ok": True}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return func.HttpResponse(
            json.dumps({"ok": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
