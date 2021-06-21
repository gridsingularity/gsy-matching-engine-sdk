from os import system
import os


def before_all(context):
    system("docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)")
    system("docker network create integtestnet")
    system("bash integration_tests/build_test_containers.sh")


def after_all(context):
    system("docker network rm integtestnet")


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    system("docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)")
