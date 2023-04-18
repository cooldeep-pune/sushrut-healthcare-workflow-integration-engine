rm ./keys/*
cp ../../keys/client/*  ./keys/
docker build -t healthcare-workflow/https-sender .