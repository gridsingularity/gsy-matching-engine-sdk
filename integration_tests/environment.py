from os import system


def before_all(context):
    for container_name in ["redis.container", "gsye-myco-tests.container"]:
        system(f"docker stop {container_name} && docker rm {container_name}")
    system("docker network create integtestnet")
    system("bash integration_tests/build_test_containers.sh")


def after_all(context):
    system("docker network rm integtestnet")


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    system("docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)")
