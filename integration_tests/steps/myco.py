from os import system
from time import sleep

from behave import given, when, then

from myco_api_client.setups.redis_base_matcher_setup import RedisMycoMatcher


@given("redis container is started")
def step_impl(context):
    system(f"docker run -d -p 6379:6379 --name redis.container -h redis.container "
           "--net integtestnet gsyd3a/d3a:redis-staging")


@given("d3a is started using setup {setup_file} ({d3a_options})")
def step_impl(context, setup_file: str, d3a_options: str):
    """Run the d3a container on a specific setup.

    Args:
        setup_file (str): the setup file for a d3a simulation.
        d3a_options (str): options to be passed to the d3a run command. E.g.: "-t 1s -d 12h"
    """
    sleep(3)
    system(f"docker run -d --name d3a-tests1 --env REDIS_URL=redis://redis.container:6379/ "
           f"--net integtestnet d3a-tests -l INFO run --setup {setup_file} "
           f"--no-export --seed 0 --enable-external-connection {d3a_options} ")


@when("the myco client is started with redis_base_matcher_setup")
def step_impl(context):
    sleep(5)
    context.matcher = RedisMycoMatcher()
    sleep(3)
    assert context.matcher.is_finished is False


@then("the myco client is connecting to the simulation until finished")
def step_impl(context):
    # Infinite loop in order to leave the client running on the background
    # placing bids and offers on every market cycle.
    # Should stop if an error occurs or if the simulation has finished
    counter = 0  # Wait for five minutes at most
    while context.matcher.errors == 0 and context.matcher.is_finished is False and counter < 60:
        sleep(3)
        counter += 3


@then("the myco client does not report errors")
def step_impl(context):
    assert context.matcher.errors == 0
