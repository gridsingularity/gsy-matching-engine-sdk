import logging

from gsy_framework.client_connections.utils import log_market_progression


class WebsocketMessageReceiver:
    """WebsocketMessageReceiver"""

    def __init__(self, rest_client):
        self.client = rest_client

    def _handle_event_message(self, message):
        """Available events: market, tick, finish, offers_bids_response,
           matched_recommendations_response.

        Args:
            message: Received websocket message

        Returns: None

        """
        event = message.get("event")
        log_market_progression(message)
        if event and hasattr(self.client, f"_on_{event}"):
            getattr(self.client, f"_on_{event}")(message)

    def received_message(self, message):
        """Handle received message."""
        try:
            self._handle_event_message(message)
            self.client.on_event_or_response(message)
        except Exception:
            logging.exception("Error while processing incoming message %s.", message)
