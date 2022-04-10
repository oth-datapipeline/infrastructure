# infrastructure
Repository for managing respective infrastructural elements such as database(s), message broker, etc.

## Project structure
.
├── .github/                            github related stuff, i.e. workflows
├── zookeper/                           folder for zookeeper, i.e. backups
├── kafka                               folder for kafka, i.e. backups
├── mongodb/                            mount folder for mongodb backups
│   ├── data/
├── docker-compose                      docker compose and related readme

## Getting started
This repository contains the dockerization and its runnable setup of the `oth-datapipeline` scraper, zookeeper, kafka and mongodb (and its UI mongo-express).
To run it, follow the instructions and cues in [docker-compose/README.md](docker-compose/README.md).
