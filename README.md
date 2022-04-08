# infrastructure
Repository for managing respective infrastructural elements such as database(s), message broker, etc.

## necessary folder structure
.
├── .github/                           github related stuff such as github actions
├── zookeper/                          mount folder for zookeeper backups
│   ├── data/ 
│   ├── logs/
├── kafka/	                       mount folder for kafka backups
│   ├── broker_data/
├── mongodb/                           mount folder for mongodb backups
│   ├── data/                          
├── docker-compose                     docker compose stuff and readme
