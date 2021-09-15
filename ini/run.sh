pkill -f ffmpeg -9
pkill -f ffserver -9

cd /home/src/final2/ini
ffserver -f server.conf
