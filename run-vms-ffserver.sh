while true;do
    echo Huawei12#$ | sudo -S pkill -f "ffserver -f vms-server.conf" -9
    ffserver -f vms-server.conf
done
