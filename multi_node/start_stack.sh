#!/bin/bash

docker network inspect swarm_network >/dev/null || docker network create --attachable --driver overlay swarm_network
docker stack deploy -c docker-compose-kafka.yml news_pipeline_stack
docker service scale news_pipeline_stack_kafka=3