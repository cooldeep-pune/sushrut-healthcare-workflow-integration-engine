echo 'Stopping healthcare-workflow-integration-engine...'

echo 'Stopping healthcare-workflow-integration-engine WebUI...'

docker-compose -f webui/docker-compose.yml down

echo 'Stopping healthcare-workflow-integration-engine Orchestrator...'

docker-compose -f orchestrator/docker-compose.yml down
echo 'Stopping healthcare-workflow-integration-engine queue manager...'

docker-compose -f queue_manager/docker-compose-redis-only.yml down

echo 'Stopping healthcare-workflow-integration-engine database...'

docker-compose -f db/docker-compose.yml down



