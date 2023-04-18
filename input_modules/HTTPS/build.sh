rm ./keys/*
cp ../../keys/server/*  ./keys/
docker build -t healthcare-workflow/https-receiver .