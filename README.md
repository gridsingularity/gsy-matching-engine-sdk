# GSy Matching Engine SDK
## Table of Content
- [GSy Matching Engine SDK](#gsy-matching-engine-sdk)
  * [Overview](#overview)
  * [Installation Instructions](#installation-instructions)
  * [How to use the Client](#how-to-use-the-client)
    + [Interacting via CLI](#interacting-via-cli)
  * [Events](#events)
  * [Matching API](#matching-api)


## Overview

GSy Matching Engine SDK is responsible for communicating with a running collaboration of GSy Exchange. The client uses
the API of the GSy Exchange external connections in order to be able to dynamically connect to the simulated
electrical grid, query the open bids/offers and post trading recommendations back to GSy Exchange.

For local test runs of GSy Exchange Redis (https://redis.io/) is used as communication protocol.
In the following commands for the local test run are marked with `LOCAL`.

For communication with collaborations or canary networks on https://d3a.io, a RESTful API is used.
In the following commands for the connection via the REST API are marked with `REST`.

## Installation Instructions

Installation of gsy-matching-engine-sdk using pip:

```
pip install git+https://github.com/gridsingularity/gsy-matching-engine-sdk.git
```
---

## How to use the Client

### Interacting via CLI
In order to get help, please run:

```
gsy-matching-engine-sdk run --help
```

The following parameters can be set via the CLI:
- `base-setup-path` --> Path where user's client script resides, otherwise `gsy_matching_engine_sdk/setups` is used.
- `setup` --> Name of user's API client module/script.
- `username` --> Username of agent authorized to communicate with respective collaboration or Canary Network (CN).
- `password` --> Password of respective agent
- `domain-name` --> GSy Exchange domain URL
- `web-socket` --> GSy Exchange websocket URL
- `simulation-id` --> UUID of the collaboration or Canary Network (CN)
- `run-on-redis` --> This flag can be set for local testing of the API client, where no user authentication is required.
  For that, a locally running redis server and GSy Exchange simulation are needed.
#### Examples
- For local testing of the API client:
  ```
  gsy-matching-engine-sdk --log-level ERROR run --setup matching_engine_matcher --run-on-redis
  ```
- For testing your api client script on remote server hosting GSy Exchange's collaboration/CNs.
    - If user's client script resides on `gsy_matching_engine_sdk/setups`

  ```
    gsy-matching-engine-sdk run -u <username> -p <password> --setup matching_engine_matcher -s <simulation-uuid> ...
    ```

    - If user's client script resides on a different directory, then its path needs to be set via `--base-setup-path`

  ```
    gsy-matching-engine-sdk run -u <username> -p <password> --base-setup-path <absolute/relative-path-to-your-client-script> --setup <name-of-your-script> ...
    ```

---


### Events
In order to facilitate offer and bid management and scheduling,
the client will get notified via events.
It is possible to capture these events and perform operations as a reaction to them
by overriding the corresponding methods.
- when a new market cycle is triggered the `on_market_cycle` method is called
- when a new tick has started, the `on_tick` method is called
- when the simulation has finished, the `on_finish` method is called
- when any event arrives, the `on_event_or_response` method is called
- When the open offers/bids response is returned, the `on_offers_bids_response` method is called
- When the posted recommendations response is returned, the `on_matched_recommendations_response` method is called
---

### Matching API
#### How to create a connection to a collaboration
The constructor of the API class can connect and register automatically to a running collaboration:
- `REST`
    ```
    matching_client = RestBaseMatcher()
    ```
- `LOCAL`
    ```
    matching_client = RedisBaseMatcher()
    ```
---

### Available methods

`Matcher` instances provide methods that can simplify specific operations. Below we have a demo:

- Fire a request to get filtered open bids/offers in the simulation:

    ```python
    ```python
      from gsy_matching_engine_sdk.matchers.rest_base_matcher import RestBaseMatcher
      matching_client = RestBaseMatcher()
      matching_client.request_offers_bids(filters={})
      ```
    ```

    Supported filters include:
    - `markets`: list of market ids, only fetch bids/offers in these markets (If not provided, all markets are included).
    - `energy_type`: energy type of offers to be returned.

    The bids_offers response can be received in the method named `on_offers_bids_response`, this one can be overridden to decide the recommendations algorithm and fires a call to submit_matches()


- Posts the trading bid/offer pairs recommendations back to GSy Exchange, can be called from the overridden on_offers_bids_response:

    ```python
    def on_offers_bids_response(self, data):
      """
      Posted recommendations should be in the format:
      [BidOfferMatch.serializable_dict(), BidOfferMatch.serializable_dict()]
      """
      bids_offers = data.get("bids_offers")
      recommendations = my_custom_matching_algorithm(bids_offers)
      self.submit_matches(recommended_matches=recommendations)
    ```
