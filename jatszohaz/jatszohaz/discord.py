import json

import requests
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def send_message(message: str):
    """
    Sends a single message to the configured Discord channel using the configured token.
    :param message:
    """

    url = settings.DISCORD_WEBHOOK_URL

    if not url:
        logger.warning("Discord url is not set! Skipping notification.")
        return

    logger.info(f"Sending message to Discord: {message[:50]}...")
    resp = requests.post(
        url,
        data=json.dumps({'content': message}),
        headers={'Content-Type': 'application/json'}
    )

    if resp.status_code not in (200, 204):
        logger.warning(f"Sending message failed! Response: {resp.status_code} - {resp.text}")
