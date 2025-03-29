"""
Telegram webhook handler for processing button callbacks
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from dotenv import load_dotenv

# Import your Telegram functions
from send_to_telegram import send_to_telegram, save_sent_jobs, load_sent_jobs

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "7648195076:AAFPUt4uz7NGtn3kwA8Xfud5-vPxHDNPXt0"
TELEGRAM_CHAT_ID = "-1002431687268"

# Flask app
app = Flask(__name__)

# Store job actions
job_actions = {}  # To store user actions on jobs


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle webhook callbacks from Telegram"""
    update = request.get_json()
    logger.info(f"Received update: {json.dumps(update)}")

    # Handle callback query (button clicks)
    if "callback_query" in update:
        callback_query = update["callback_query"]
        callback_data = callback_query["data"]
        user_id = callback_query["from"]["id"]
        message_id = callback_query["message"]["message_id"]
        
        # Process the callback data
        process_callback(callback_data, user_id, message_id)
        
        # Answer callback query to remove loading state
        answer_callback_query(callback_query["id"])
        
    return jsonify({"ok": True})


def process_callback(callback_data, user_id, message_id):
    """Process button callback data"""
    logger.info(f"Processing callback: {callback_data} from user {user_id}")
    
    try:
        # Split the callback data (format: action_jobid)
        action, job_id = callback_data.split("_", 1)
        
        # Track this action
        if job_id not in job_actions:
            job_actions[job_id] = []
        
        job_actions[job_id].append({
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
        
        # Handle different actions
        if action == "save":
            # Logic for saving the job
            message = f"✅ Job saved to your favorites"
            send_to_telegram(message)
            logger.info(f"User {user_id} saved job {job_id}")
            
        elif action == "interested":
            # Logic for marking as interested
            message = f"👍 You've marked this job as interesting"
            send_to_telegram(message)
            logger.info(f"User {user_id} marked interest in job {job_id}")
            
        elif action == "applied":
            # Logic for marking as applied
            message = f"🚀 You've marked this job as applied"
            send_to_telegram(message)
            logger.info(f"User {user_id} marked job {job_id} as applied")
            
        # Save actions to a file
        save_job_actions()
        
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        send_to_telegram(f"Error processing action: {str(e)}")


def answer_callback_query(callback_query_id):
    """Acknowledge the callback query to stop the loading state"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    data = {"callback_query_id": callback_query_id}
    try:
        requests.post(url, json=data)
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")


def save_job_actions():
    """Save job actions to a file"""
    try:
        with open("job_actions.json", "w") as f:
            json.dump(job_actions, f)
        logger.info("Saved job actions to file")
    except Exception as e:
        logger.error(f"Error saving job actions: {e}")


def setup_webhook(url):
    """Set up the Telegram webhook to the provided URL"""
    webhook_url = f"{url}/webhook"
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(set_webhook_url, json=data)
        result = response.json()
        
        if result.get("ok"):
            logger.info(f"Webhook set up successfully at {webhook_url}")
            return True
        else:
            logger.error(f"Failed to set webhook: {result.get('description')}")
            return False
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return False


def main():
    """Start the Flask app with ngrok tunnel"""
    # Start ngrok tunnel
    ngrok_auth_token = "2uzpN4izC803G5X1DNMrjj5psjT_67RqgLret2EbGGqr743EL"
    if ngrok_auth_token:
        ngrok.set_auth_token(ngrok_auth_token)
    
    # Open an HTTP tunnel on the default port 5000
    public_url = ngrok.connect(5000).public_url
    logger.info(f"ngrok tunnel established at: {public_url}")
    
    # Set up the webhook
    if setup_webhook(public_url):
        logger.info("Webhook is active! Waiting for callbacks...")
    else:
        logger.error("Failed to set up webhook. Exiting.")
        return
    
    # Run the Flask app
    app.run(port=5000)


if __name__ == "__main__":
    main()