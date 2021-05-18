import logging
import traceback


class WebsocketMessageReceiver:
    def __init__(self, rest_client):
        self.client = rest_client
        self.command_response_buffer = []

    def _handle_event_message(self, message):
        if "event" in message and message.get("event") == "offers_bids_response":
            self.client.on_bids_offers_response(message)

    def received_message(self, message):
        try:
            self._handle_event_message(message)
        except Exception as e:
            logging.error(f"Error while processing incoming message {message}. Exception {e}.\n"
                          f"{traceback.format_exc()}")
