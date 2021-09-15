import MySQLdb
import traceback
import time

class Mysql:
    def __init__(self, args):
        self.ip = args["ip"]
        self.user = args["user"]
        self.passwd = args["pwd"]
        self.db = args['db']
        self.table = args["table"]
        self.values = {}
        self.connect()

    def connect(self):
        self.database = MySQLdb.connect(self.ip, self.user, self.passwd, self.db)
        self.cursor = self.database.cursor()

    def run_fetch(self, cmd):
        try:
            self.cursor.execute(cmd)
            self.database.commit()
            result = self.cursor.fetchall()
            return result
        except Exception:
            #print(traceback.format_exc())
            time.sleep(1)
            self.close()
            self.connect()
            self.cursor.execute(cmd)
            self.database.commit()
            result = self.cursor.fetchall()
            return result

    def close(self):
        self.cursor.close()
        self.database.close()


if __name__ == '__main__':
    mysql_args = {
        "ip":'127.0.0.1',
        "user":'graymatics',
        "pwd":'graymatics',
        "db":'test0',
        "table":"test1",
        #"column": [
        #    #['c1','INT NOT NULL AUTO_INCREMENT, primary key(c1)'],
        #    ['c1','INT NOT NULL'],
        #    ['c2','varchar(40)']
        #    ]
        }

    mysql = Mysql(mysql_args)
    #for i in range(100):
    #    mysql.insert_fast([12345, 'abcde'])
    #mysql.commit_insert()
    t0 = time.time()
    for i in range(1):
        print(mysql.fetch(['c2,c1']))
    print(time.time() -t0)
