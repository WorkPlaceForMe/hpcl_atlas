cd /home/src/final

python3 manage_camDB.py

pkill -f flask2.py
python3 -u flask2.py &
sleep 5

pkill -f flask_server.py
python3 -u flask_server.py
sleep 5

