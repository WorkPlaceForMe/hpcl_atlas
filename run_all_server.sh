#!/bin/bash

dir0="/home/hpcl-videoanalytics/atlas2/"
src="${dir0}src/final4/"
#dir0="/home/graymatics/dev/atlas/"
#src="${dir0}final4/"

dock="${dir0}docker/"
yolo="${dir0}src/General_Yolov3_upgrade/bin/"

MYSQL_DB=hpcl3

#cd $dock
#bash run-docker-ff.sh
#sleep 5

cd $src
echo Huawei12#$ | sudo -S pkill -f "run_objectdemo.py"
sudo python3 -u run_objectdemo.py --src $src --yolo $yolo --db $MYSQL_DB &
sleep 5
    
#cd $dock
#bash run-docker.sh $src $MYSQL_DB

while true;do
    sleep 9999
    #ffserver -f vms-server.conf
done
    



