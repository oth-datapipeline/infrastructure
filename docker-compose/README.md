# Useful Infrastructure Commands


## Starting service stack

First things first. To start (and shutdown) the service stack, use these commands.

```
docker-compose -f <path-to-docker-compose.yml> up -d 	// starts up docker-compose service stack, -d = detached

docker-compose -f <path-to-docker-compose.yml> down	// shuts down docker-compose service stack
```

After starting up, you can check if all instances are running correctly using `docker ps`. 
There should be a container broker and zookeeper running.


## Creating kafka topics

It’s good practice to explicitly create them before using them, even if Kafka is configured to automagically create them when referenced. Run this command to create a new topic

```
docker exec -it broker bash
kafka-topics --bootstrap-server broker:9092 --create --topic <name-of-topic>
```

## Using Mongo Express

To manage MongoDB, we use Mongo Express, web-based MongoDB admin interface. 
Once your docker-compose service stack is up and running, you can use Mongo Express' UI.
Go to the browser of your choice and enter `http://localhost:8081/`. Et voila, there is your admin UI.
