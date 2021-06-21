import logging
import traceback


class WebsocketMessageReceiver:
    def __init__(self, rest_client):
        self.client = rest_client

    def _handle_event_message(self, message):
        """Available events: market, tick, finish, offers_bids_response, matched_recommendations_response.

        Args:
            message: Received websocket message

        Returns: None

        """
        event = message.get("event")
        if event and hasattr(self.client, f"_on_{event}"):
            getattr(self.client, f"_on_{event}")(message)

    def received_message(self, message):
        try:
            self._handle_event_message(message)
            self.client.on_event_or_response(message)
        except Exception:
            logging.exception("Error while processing incoming message %s.", message)
