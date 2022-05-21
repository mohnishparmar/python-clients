if [ -z "${SERVER}" ]; then
  export SERVER="localhost:50051"
else
  export SERVER
fi
if [ ! -z "${SSL_CERT}" ]; then
  export SSL_CERT
fi
if [ ! -z "${USE_SSL}"] && [[ "${USE_SSL}" != "0" ]]; then
  export USE_SSL
fi