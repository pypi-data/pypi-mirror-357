import requests
import logging
from utils.config import FACEBOOK_GRAPH_API_VERSION, LENAAI_CHAT_ENDPOINT

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class WhatsApp:
    def send_whatsapp_message(self,to_number, message, credentials, albums=None, video_url=None):

        url = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}/{credentials['phone_number_id']}/messages"
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }

        # Ensure message is not empty before sending
        if not message.strip():
            logging.error("❌ Attempted to send an empty message. Skipping WhatsApp API call.")
            return

        # Send text message
        payload_text = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        logging.info(f"Sending text message to WhatsApp: {payload_text}")
        response_text = requests.post(url, json=payload_text, headers=headers)

        if response_text.status_code == 200:
            logging.info(f"✅ WhatsApp API Response (Text): {response_text.json()}")
        else:
            logging.error(f"❌ Failed to send text message to WhatsApp. Response: {response_text.status_code} - {response_text.text}")

        # Send images if available
        if albums:
            for unit, images in albums.items():
                for img_url in images[:3]:  # Max 3 images per message
                    payload_image = {
                        "messaging_product": "whatsapp",
                        "to": to_number,
                        "type": "image",
                        "image": {"link": img_url},
                        "text": {"body": unit}
                    }
                    logging.info(f"Sending image to WhatsApp for unit {unit}: {img_url}")
                    response_image = requests.post(url, json=payload_image, headers=headers)

                    if response_image.status_code == 200:
                        logging.info(f"✅ WhatsApp API Response (Image): {response_image.json()}")
                    else:
                        logging.error(f"❌ Failed to send image {img_url}. Response: {response_image.status_code} - {response_image.text}")

        # Send video if available
        if video_url:
            payload_video = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "video",
                "video": {
                    "link": video_url
                }
            }
            logging.info(f"Sending video to WhatsApp: {video_url}")
            response_video = requests.post(url, json=payload_video, headers=headers)

            if response_video.status_code == 200:
                logging.info(f"✅ WhatsApp API Response (Video): {response_video.json()}")
            else:
                logging.error(f"❌ Failed to send video. Response: {response_video.status_code} - {response_video.text}")

    # Function to forward messages to Lena AI
    def forward_to_lena_ai(self, phone_number, user_message, credentials):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "client_id": credentials['client_id'], 
            "phone_number": phone_number,
            "query": user_message
        }

        logging.info(f"Forwarding message to Lena AI: {payload}")

        response = requests.post(LENAAI_CHAT_ENDPOINT, json=payload, headers=headers)

        allowed_extensions = (".png", ".jpg")
        
        if response.status_code == 200:
            response_json = response.json()
            logging.info(f"✅ Lena AI Response: {response_json}")

            # Extract main text reply
            reply = response_json.get("message", "").strip()  # Ensure non-empty message

            # Extract properties and their images
            properties = response_json.get("properties") or []
            albums = {}

            for property in properties:
                unit_id = property.get("unit", "unknown_unit")  
                images = property.get("images", [])  
                filtered_images = [img for img in images if img.lower().endswith(allowed_extensions)]
                albums[unit_id] = filtered_images

            return reply or "I'm sorry, I couldn't understand your request.", albums

        else:
            logging.error(f"❌ Error communicating with Lena AI. Response: {response.status_code} - {response.text}")
            return "Sorry, there was an issue processing your request.", {}


whatsapp = WhatsApp()