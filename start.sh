docker build -t crutch-calc . && \
docker run -d -p 80:5000 --name crutch-calc crutch-calc