import logging
import traceback


class WebsocketMessageReceiver:
    def __init__(self, rest_client):
        self.client = rest_client

    def _handle_event_message(self, message):
        """
        Available events: tick (wip), offers_bids_response, matched_recommendations_response (wip)
        :param message:
        :return:
        """
        event = message.get("event")
        if event and hasattr(self.client, f"_on_{event}"):
            getattr(self.client, f"_on_{event}")(message)

    def received_message(self, message):
        try:
            self._handle_event_message(message)
            self.client.on_event_or_response(message)
        except Exception as e:
            logging.error(f"Error while processing incoming message {message}. Exception {e}.\n"
                          f"{traceback.format_exc()}")
