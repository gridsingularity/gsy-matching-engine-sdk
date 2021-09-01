Feature: Myco Client

Scenario: Myco Client connects to simulation
      Given redis container is started
      And d3a is started using setup myco_setup.external_myco (-t 60s -s 60m -d 4h --slot-length-realtime 2s)
      When the myco client is started with redis_base_matcher_setup
      Then the myco client is connecting to the simulation until finished
      And the myco client does not report errors
      And all events handler are called

Scenario: Myco Client respects bids/offers attributes and requirements
      Given redis container is started
      And d3a is started using setup myco_setup.external_myco (-t 60s -s 60m -d 24h --slot-length-realtime 5s)
      And d3a-api-client is connected to simulation
      When the myco client is started with redis_base_matcher_setup
      Then the myco client is connecting to the simulation until finished
      And the myco client does not report errors
      And all events handler are called
      And the api client's bid's/offer's attributes/requirements weren't violated
