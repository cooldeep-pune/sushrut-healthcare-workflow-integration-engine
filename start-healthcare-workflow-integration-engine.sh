echo 'Initializing environment...'

export POSTGRES_HOST=localhost
export POSTGRES_USER=healthcare
export POSTGRES_PASSWORD=sushrut
export POSTGRES_DB=healthcare
export POSTGRES_PORT=5432
export ORCHESTRATOR_HOST=localhost
export ORCHESTRATOR_PORT=12345
export REDIS_HOST=localhost
export REDIS_PORT=6379

echo 'Starting healthcare-workflow-integration-engine...'

echo 'Starting healthcare-workflow-integration-engine database...'

docker-compose -f db/docker-compose.yml up -d postgres

echo 'Creating healthcare-workflow-integration-engine database...'

docker-compose -f db/docker-compose.yml exec -it postgres sh '/sql/create_tables.sh'

echo 'Starting healthcare-workflow-integration-engine queue manager...'

docker-compose -f queue_manager/docker-compose-redis-only.yml up -d cache

echo 'Starting healthcare-workflow-integration-engine Orchestrator...'

docker-compose -f orchestrator/docker-compose.yml up -d orchestrator

echo 'Starting healthcare-workflow-integration-engine WebUI...'

docker-compose -f webui/docker-compose.yml up -d healthcare-workflow-webui

