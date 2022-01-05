docker stop hpcl
docker rm hpcl

docker run -d \
    --network host \
    -e MYSQL_DB=$2 \
    -v /home/hpcl-videoanalytics/atlas2/src/final4:/home/src/final \
    --name hpcl \
    -w /home/src/final \
    --entrypoint "/bin/bash" \
    hpcl \
    -c "bash /home/src/final/run.sh"
