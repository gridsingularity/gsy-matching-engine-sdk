# Myco API Client
## Table of Content
- [Myco API Client](#myco-api-client)
  * [Overview](#overview)
  * [Installation Instructions](#installation-instructions)
  * [How to use the Client](#how-to-use-the-client)
    + [Interacting via CLI](#interacting-via-cli)


## Overview

Myco API client is responsible for communicating with a running collaboration of D3A. The client uses 
the API of the D3A external connections in order to be able to dynamically connect to the simulated 
electrical grid, query the open bids/offers and post trading recommendations back to D3A.

For local test runs of D3A Redis (https://redis.io/) is used as communication protocol. 
In the following commands for the local test run are marked with `LOCAL`. 

For communication with collaborations or canary networks on https://d3a.io, a RESTful API is used.
In the following commands for the connection via the REST API are marked with `REST`. 

## Installation Instructions

Installation of myco-api-client using pip:

```
pip install git+https://github.com/gridsingularity/myco-api-client.git
```
---

## How to use the Client

### Interacting via CLI
In order to get help, please run:
```
myco run --help
```
The following parameters can be set via the CLI:
- `base-setup-path` --> Path where user's client script resides, otherwise `myco_api_client/setups` is used.
- `setup` --> Name of user's API client module/script.
- `username` --> Username of agent authorized to communicate with respective collaboration or Canary Network (CN).
- `password` --> Password of respective agent
- `domain-name` --> D3A domain URL
- `web-socket` --> D3A websocket URL
- `simulation-id` --> UUID of the collaboration or Canary Network (CN)
- `run-on-redis` --> This flag can be set for local testing of the API client, where no user authentication is required. 
  For that, a locally running redis server and d3a simulation are needed.

#### Examples
- For local testing of the API client:
  ```
  myco --log-level ERROR run --setup redis_base_matcher_setup --run-on-redis
  ```
- For testing your api client script on remote server hosting d3a's collaboration/CNs.
    - If user's client script resides on `myco_api_client/setups`
    ```
    myco run -u <username> -p <password> --setup base_matcher_setup -s <simulation-uuid> ...
    ```
    - If user's client script resides on a different directory, then its path needs to be set via `--base-setup-path`
    ```
    myco run -u <username> -p <password> --base-setup-path <absolute/relative-path-to-your-client-script> --setup <name-of-your-script> ...
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
    matching_client = BaseMatcher()
    ```
- `LOCAL`
    ``` 
    matching_client = RedisBaseMatcher()
    ```
---

#### Available methods

`Matcher` instances provide methods that can simplify specific operations. Below we have a demo:

- Fires a request to get all open bids/offers in the simulation: 
    ```python
  matching_client = BaseMatcher()
  matching_client.request_orders(filters={}) 
    ```
  The response can be received in the method named `on_offers_bids_response`, this one can be overridden to decide the recommendations algorithm

  
- Posts the trading bid/offer pairs recommendations back to d3a, can be called from the overridden on_offers_bids_response: 
    ```python
    def on_offers_bids_response(self, data):
      """
      Posted recommendations should be in the format: 
      [BidOfferMatch.serializable_dict(), BidOfferMatch.serializable_dict()]
      """
      recommendations = # Do something with the data
      self.submit_matches(recommended_matches=recommendations)
    ```
