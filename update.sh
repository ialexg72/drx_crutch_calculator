docker stop crutch-calc && \
docker rm crutch-calc && \
docker build -t crutch-calc . && \
docker run -v /home/vm-operator/logs:/app/logs -v /home/vm-operator/ready_calc:/app/ready_reports -v /home/vm-operator/tmp:/app/tmp -d -p 80:5000 --name crch-calc crutch-calc