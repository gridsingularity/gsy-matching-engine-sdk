from os import system
from time import sleep

from behave import given, when, then

from integration_tests.test_redis_myco_matcher import TestRedisMycoMatcher


@given("redis container is started")
def step_impl(context):
    system("docker run -d -p 6379:6379 --name redis.container -h redis.container "
           "--net integtestnet redis:6.2.5")


@given("gsy-e is started using setup {setup_file} ({gsye_options})")
def step_impl(context, setup_file: str, gsye_options: str):
    """Run the gsy exchange container on a specific setup.

    Args:
        setup_file (str): the setup file for a simulation.
        gsye_options (str): options to be passed to the gsy_e run command. E.g.: "-t 1s -d 12h"
    """
    sleep(3)
    system("docker run -d --name gsye-myco-tests.container "
           "--env REDIS_URL=redis://redis.container:6379/ "
           f"--net integtestnet gsy-e-tests -l INFO run --setup {setup_file} "
           f"--no-export --seed 0 --enable-external-connection {gsye_options} ")


@when("the myco client is started with redis_base_matcher_setup")
def step_impl(context):
    sleep(5)
    context.matcher = TestRedisMycoMatcher()
    sleep(3)
    assert context.matcher.is_finished is False


@then("the myco client is connecting to the simulation until finished")
def step_impl(context):
    # Infinite loop in order to leave the client running on the background
    # placing bids and offers on every market cycle.
    # Should stop if an error occurs or if the simulation has finished
    counter = 0
    while context.matcher.errors == 0 and not context.matcher.is_finished and counter < 150:
        sleep(3)
        counter += 3


@then("all events handler are called")
def step_impl(context):
    assert context.matcher.called_events == {"market_cycle", "tick", "orders_response",
                                             "event_or_response", "match", "finish",
                                             "on_area_map_response"}


@then("the myco client does not report errors")
def step_impl(context):
    assert context.matcher.errors == 0
