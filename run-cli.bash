export POSTGRES_HOST=localhost
export POSTGRES_USER=healthcare
export POSTGRES_PASSWORD=sushrut
export POSTGRES_DB=healthcare
export POSTGRES_PORT=5432
export ORCHESTRATOR_HOST=localhost
export ORCHESTRATOR_PORT=12345
export REDIS_HOST=localhost
export REDIS_PORT=6379

echo 'Starting healthcare-Integration-Engine Command Line Interface...'
docker-compose -f cli/docker-compose.yml run cli bash

