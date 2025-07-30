from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

import requests
from pydantic import BaseModel

from titan_mind.utils.app_specific.networking.titan_mind import TitanMindAPINetworking, HTTPMethod
from titan_mind.utils.general.date_time import get_date_time_to_utc_server_time_format_string


def get_conversations_from_the_last_day() -> Optional[Dict[str, Any]]:
    yesterday_datetime = datetime.now() - timedelta(days=1)
    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"msg/conversations/",
            success_message="last 24 hours conversations fetched.",
            method=HTTPMethod.GET,
            payload={
                "page": 1,
                "channel": "whatsapp",
                "last_message_at__gte": get_date_time_to_utc_server_time_format_string(yesterday_datetime)
            }
        )
    )


def get_the_conversation_messages(conversation_id: str) -> Optional[Dict[str, Any]]:
    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"msg/conversations/{conversation_id}/messages/",
            success_message="messages in a conversation fetched.",
            method=HTTPMethod.GET,
            payload={
            }
        )
    )


def send_whatsapp_message_to_a_conversation(conversation_id: str, message: str):
    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"msg/conversations/{conversation_id}/messages/whatsapp/send-message/",
            success_message="whatsapp message sent request created.",
            method=HTTPMethod.POST,
            payload={
                "recipient_type": "individual",
                "type": "text",
                "text": {
                    "body": message
                }
            }
        )
    )


def register_msg_template_for_approval(
        template_name: str, language: str, category: str, message_content_components: list[dict[str, Any]]
):
    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"whatsapp/template/",
            payload={
                "name": template_name,
                "language": language,
                "category": category,
                "components": message_content_components
            },
            success_message="whatsapp template registered for approval.",
            method=HTTPMethod.POST,
        )
    )


def get_the_templates(
        template_name: Optional[str]
):
    payload = {
        "channel": "whatsapp",
    }
    if template_name is not None:
        payload["name__icontains"] = template_name

    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"template/",
            payload=payload,
            success_message="templates fetched",
            method=HTTPMethod.GET,
        )
    )


class Contact(BaseModel):
    country_code_alpha: str
    country_code: str
    phone_without_country_code: str


def send_message_to_a_number_using_approved_template(
        template_id: int,
        contacts: list[Contact],
):
    return asdict(
        TitanMindAPINetworking().make_request(
            endpoint=f"whatsapp/message/send-template/",
            payload={
                "recipients": [contact.model_dump() for contact in contacts],
                "template": template_id,
            },
            success_message="message sent request created.",
            method=HTTPMethod.POST,
        )
    )
