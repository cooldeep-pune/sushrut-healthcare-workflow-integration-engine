rm ./keys/*
cp ../../keys/client/*  ./keys/
cp ../../keys/ca-cert.pem ./keys/
docker build -t healthcare-workflow/https-sender .