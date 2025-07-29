import asyncio
from datetime import datetime
import logging
from typing import Dict, List
import aiohttp


from src.message_handler.base_message_handler import BaseMessageHandler
from src.utils.config import FACEBOOK_GRAPH_API_VERSION, LENAAI_UPDATE_DB_ENDPOINT
from src.utils.status_enums import MessageSendStatus, VideoSendStatus
from src.utils.whats_video_format import convert_to_whatsapp_format


class WhatsAppMessageHandler(BaseMessageHandler):
    """
    A class to handle all WhatsApp messaging operations.
    """
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the WhatsApp message handler.
        
        Args:
            credentials: Dictionary containing 'phone_number_id' and 'access_token'
        """
        self.credentials = credentials
        self.base_url = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}/{credentials['phone_number_id']}/messages"
        self.headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        self.platform = "whatsapp"

    async def send_real_estate_intro_template(self, to_number: str):
        """
        Sends the Arabic real estate welcome template using WhatsApp Cloud API.
        This template contains only a fixed body message (no variables).
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": { "code": "en_US" },
                "components": []
                }
        }

        try:
            logging.info(f"🚀 Sending Arabic real estate intro template to {to_number}")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        logging.info(f"✅ Arabic template sent successfully. Response: {response_text}")
                        return MessageSendStatus.SUCCESS
                    else:
                        logging.error(f"❌ Failed to send template. Status: {response.status} | Body: {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
        except Exception as e:
            logging.error(f"❌ Exception while sending Arabic template: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND


    async def update_firestore_history(self, session, to_number: str, message: str):
        """
        Updates Firestore history with the bot's response.
        """
        bot_response_data = {
            "phone_number": to_number, # todo
            "client_id": self.credentials['client_id'],
            "bot_response": message,  # The message sent by the bot
            "platform": self.platform,
            "timestamp": datetime.utcnow().isoformat()
        }

        async with session.post(LENAAI_UPDATE_DB_ENDPOINT, json=bot_response_data) as history_response:
            if history_response.status == 200:
                logging.info("✅ Bot response saved in Firestore history")
            else:
                logging.error(f"❌ Failed to update Firestore history: {history_response.status} - {await history_response.text()}")

    async def send_free_text(self, to_number: str, message: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        try:
            logging.info(f"🚀 Sending free text message to {to_number}")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        logging.info(f"✅ Message sent successfully. Response: {response_text}")
                        return MessageSendStatus.SUCCESS
                    else:
                        logging.error(f"❌ Failed to send message. Status: {response.status} | Body: {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
        except Exception as e:
            logging.error(f"❌ Exception while sending message: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND

    
    async def send_text(self, to_number: str, message: str):
        """
        Sends a text message through WhatsApp asynchronously and updates Firestore history.
        """
        if not message.strip():
            logging.error("❌ Empty message provided")
            return MessageSendStatus.FAILED_TO_SEND

        try:
            # payload = {
            #         "messaging_product": "whatsapp",
            #         "to": to_number,
            #         "type": "template",
            #         "template": {
            #             "name": "hello_world",
            #             "language": { "code": "en_US" }
            #         }
            #     }
            payload = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "template",
                    "template": {
                        "name": "whatsapp_text_template_hx7f8bb4781e7d3df5a6b11293d67a4dd5",
                        "language": {
                        "code": "ar"
                        },
                        "components": []
                    }
                    }

            
            logging.info(f"Sending text message to WhatsApp: {payload}")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()  # <-- GET THIS
                    if response.status == 200:
                        logging.info(f"✅ Text message sent successfully. Response: {response_text}")
                        return MessageSendStatus.SUCCESS
                    else:
                        logging.error(f"❌ Failed to send message. Status: {response.status} | Body: {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending text message: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND
    
    async def send_image(self, to_number: str, image_url: str):
        """
        Sends a single image through WhatsApp asynchronously.
        
        Args:
            to_number: The recipient's phone number
            image_url: The URL of the image to send
            
        Returns:
            Status of the send operation
        """
        try:
            logging.info(f"🚀 Attempting to send image: {image_url} to {to_number}")
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "image",
                "image": {"link": image_url}
            }

            logging.info(f"📤 WhatsApp API Payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        logging.info(f"✅ Image sent successfully: {image_url}")
                        return {
                            "url": image_url,
                            "status": "success",
                            "message": "Image sent successfully"
                        }
                    else:
                        logging.error(f"❌ Failed to send image {image_url}. Response: {response.status} - {response_text}")
                        return {
                            "url": image_url,
                            "status": "failed",
                            "message": response_text
                        }
                    
        except Exception as e:
            logging.error(f"❌ Error sending image: {str(e)}")
            return {
                "url": image_url,
                "status": "failed",
                "message": str(e)
            }

    async def send_images(self, to_number: str, image_urls: List[str]):
        """
        Sends images through WhatsApp asynchronously.
        """
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for img_url in image_urls[:3]:  # WhatsApp allows up to 3 images at a time
                    logging.info(f"🚀 Attempting to send image: {img_url} to {to_number}")
                    
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": to_number,
                        "type": "image",
                        "image": {"link": img_url}
                    }

                    logging.info(f"📤 WhatsApp API Payload: {payload}")
                    
                    async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                        response_text = await response.text()
                        
                        if response.status == 200:
                            logging.info(f"✅ Image sent successfully: {img_url}")
                            
                            results.append({
                                "url": img_url,
                                "status": "success",
                                "message": "Image sent successfully"
                            })
                        else:
                            logging.error(f"❌ Failed to send image {img_url}. Response: {response.status} - {response_text}")
                            
                            results.append({
                                "url": img_url,
                                "status": "failed",
                                "message": response_text
                            })
                    
        except Exception as e:
            logging.error(f"❌ Error sending images: {str(e)}")
            
            results.append({
                "url": "unknown",
                "status": "failed",
                "message": str(e)
            })
        
        return results

    async def send_video(self, to_number: str, video_url: str) -> VideoSendStatus:
        """
        Sends a video through WhatsApp asynchronously.
        """
        try:
            # is_compatible, checks = check_whatsapp_video_format(video_url)
            is_compatible = True
            if not is_compatible:
                # logging.warning(f"Video format incompatible. Check results: {checks}")
                converted_url = convert_to_whatsapp_format(video_url)
                
                if not converted_url:
                    logging.error("❌ Failed to convert video to WhatsApp format")
                    return VideoSendStatus.FAILED_TO_CONVERT
                    
                video_url = converted_url
            
            # Prepare and send the video
            payload_video = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "video",
                "video": {"link": video_url}
            }
            
            logging.info(f"Sending video to WhatsApp: {video_url}")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload_video, headers=self.headers) as response:
                    if response.status == 200:
                        logging.info("✅ Video sent successfully")
                        return VideoSendStatus.SUCCESS
                    else:
                        response_text = await response.text()
                        logging.error(f"❌ Failed to send video. Response: {response.status} - {response_text}")
                        return VideoSendStatus.FAILED_TO_SEND
                
        except Exception as e:
            logging.error(f"❌ Error sending video: {str(e)}")
            return VideoSendStatus.FAILED_TO_SEND
# todo CHANGE NAME 
    async def send_message(self, to_number: str, message: str = None, albums: Dict = None, video_url: str = None):
        """
        Main function to send WhatsApp messages with optional media asynchronously.
        """
        status = {
            "text": None,
            "images": [],
            "video": None
        }
        
        # Send text if provided
        if message:
            text_status = await self.send_text(to_number, message)
            status["text"] = text_status.value
        
        # Send images if provided
        if albums:
            for description, images in albums.items():
                # First send the description text for this album
                if description:
                    desc_status = await self.send_text(to_number, description)
                    # Give WhatsApp API time to process the message
                    await asyncio.sleep(1)
                    
                # Then send the images for this album
                if images:
                    image_results = await self.send_images(to_number, images)
                    status["images"].extend(image_results)
                    # Add delay between albums
                    await asyncio.sleep(1)
        
        # Send video if provided
        if video_url:
            video_status = await self.send_video(to_number, video_url)
            status["video"] = video_status.value
        
        return status

    async def send_arabic_real_estate_template(self, to_number: str, video_url: str):
        """
        Sends the Arabic (Egyptian) version of the real estate chatbot introduction template via WhatsApp.
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": "leading_message",
                "language": {"code": "ar_EG"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "video",
                                "video": {
                                    "link": video_url  # Take video URL as input
                                }
                            }
                        ]
                    }
                ]
            }
        }

        try:
            logging.info(f"🚀 Sending Arabic Real Estate Chatbot Template to {to_number} with video {video_url}")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        logging.info(f"✅ Arabic template message sent successfully to {to_number}")
                        return MessageSendStatus.SUCCESS
                    else:
                        logging.error(f"❌ Failed to send Arabic template. Response: {response.status} - {response_text}")
                        return MessageSendStatus.FAILED_TO_SEND
        except Exception as e:
            logging.error(f"❌ Error sending Arabic template: {str(e)}")
            return MessageSendStatus.FAILED_TO_SEND