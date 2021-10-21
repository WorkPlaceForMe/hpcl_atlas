docker stop ffserver
docker rm ffserver
docker run -d --network host --restart always \
    -v /home/hpcl-videoanalytics/atlas2/src:/home/src \
    --name ffserver \
    -w /home/src/final4 \
    --entrypoint "/bin/bash" \
    hpcl \
    -c "bash run-vms-ffserver.sh"
