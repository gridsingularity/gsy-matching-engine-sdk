import asyncio
import logging
import threading
import traceback
import websockets
import json
from time import time
from myko_api_client.utils import retrieve_jwt_key_from_server
from myko_api_client.constants import (
    WEBSOCKET_ERROR_THRESHOLD_SECONDS,
    WEBSOCKET_MAX_CONNECTION_RETRIES,
    WEBSOCKET_WAIT_BEFORE_RETRY_SECONDS)


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


class WebsocketAsyncConnection:

    def __init__(self, websocket_uri, http_domain_name, message_dispatcher):
        self._message_dispatcher = message_dispatcher
        self._websocket_uri = websocket_uri
        self._http_domain_name = http_domain_name

    async def _connection_loop_coroutine(self, websocket_headers):
        websocket = await websockets.connect(self._websocket_uri, extra_headers=websocket_headers)
        while True:
            try:
                message = await websocket.recv()
                logging.debug(f"Websocket received message {message}")
                self._message_dispatcher.received_message(json.loads(message.decode('utf-8')))
            except Exception as e:
                await websocket.close()
                await websocket.wait_closed()
                raise Exception(f"Error while receiving message: {str(e)}, "
                                f"traceback:{traceback.format_exc()}")

    def _generate_websocket_connection_headers(self):
        return {
            "Authorization": f"JWT {retrieve_jwt_key_from_server(self._http_domain_name)}"
        }

    async def run_coroutine(self, retry_count=0):
        websocket_headers = self._generate_websocket_connection_headers()
        ws_connect_time = time()
        try:
            await self._connection_loop_coroutine(websocket_headers)
        except Exception as e:
            logging.warning(f"Connection failed, trying to reconnect.")
            ws_error_time = time()
            if ws_error_time - ws_connect_time > WEBSOCKET_ERROR_THRESHOLD_SECONDS:
                retry_count = 0
            await asyncio.sleep(WEBSOCKET_WAIT_BEFORE_RETRY_SECONDS)
            if retry_count >= WEBSOCKET_MAX_CONNECTION_RETRIES:
                raise e
            await self.run_coroutine(retry_count=retry_count+1)


class WebsocketThread(threading.Thread):

    def __init__(self, sim_id, websocket_domain_name, http_domain_name, dispatcher, *args, **kwargs):
        self.message_dispatcher = dispatcher
        self.domain_name = websocket_domain_name
        self.http_domain_name = http_domain_name
        self.sim_id = sim_id
        super().__init__(*args, **kwargs, daemon=True)

    def run(self):
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        websocket_uri = f"{self.domain_name}/{self.sim_id}/"
        event_loop.run_until_complete(
            WebsocketAsyncConnection(websocket_uri, self.http_domain_name,
                                     self.message_dispatcher).run_coroutine()
        )
        event_loop.close()
