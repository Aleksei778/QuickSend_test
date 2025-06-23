# Создать директорию для сертификатов
mkdir -p ./certs

# Создать CA
openssl req -new -x509 -keyout ./certs/ca-key.pem -out ./certs/ca-cert.pem -days 365 \
  -subj "/CN=kafka-ca" -nodes

# Создать конфигурацию с SAN
cat > ./certs/server.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = kafka-cluster

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = kafka1
DNS.2 = kafka2
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

# Создать ключ и CSR для сервера
openssl req -newkey rsa:2048 -keyout ./certs/server-key.pem -out ./certs/server-req.pem \
  -config ./certs/server.conf -nodes

# Подписать сертификат
openssl x509 -req -in ./certs/server-req.pem -CA ./certs/ca-cert.pem \
  -CAkey ./certs/ca-key.pem -out ./certs/server-cert.pem -days 365 \
  -extensions v3_req -extfile ./certs/server.conf -CAcreateserial