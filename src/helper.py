import sys
import sqlite3

class DbController:
    def __init__(self, dbFilepath):

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.dbFilepath = dbFilepath
        self.con = sqlite3.connect(self.dbFilepath)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.close()

    def execute(self, query, arg=None):
        try:
            if arg is None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, arg)
            self.con.commit()
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            print(e)
            return False
        return True

    def exist_fasta(self, _id):
        query = "SELECT EXISTS(SELECT 1 from fasta WHERE fasta_id=?)"
        success = self.execute(query, (_id,))
        if success:
            return list(self.cur.fetchone().values())[0]
        else:
            print("ERROR: failed to execute exist_fasta()", file=sys.stderr)
            sys.exit(1)

    def insert_fasta(self, _id, origin):
        query = "INSERT INTO fasta VALUES(?, ?, CURRENT_TIMESTAMP)"
        success = self.execute(query, (_id, origin))
        if not(success):
            print("ERROR: failed to execute insert_fasta()", file=sys.stderr)
            sys.exit(1)

    def delete_fasta(self, _id):
        query = "DELETE FROM fasta WHERE fasta_id=?"
        success = self.execute(query, (_id,))
        if not(success):
            print("ERROR: failed to execute delete_fasta()", file=sys.stderr)
            sys.exit(1)

    def get_timestamp_fasta(self, _id):
        query = "SELECT timestamp FROM fasta WHERE fasta_id=?"
        success = self.execute(query, (_id,))
        if success:
            ret = self.cur.fetchone()
            if ret is None:
                print("ERROR: {} is not exist in fasta table".format(_id), file=sys.stderr)
                sys.exit(1)
            return ret["timestamp"]
        else:
            print("ERROR: failed to execute get_timestamp_fasta()", file=sys.stderr)
            sys.exit(1)

    def insert_db(self, _id, software):
        query = "INSERT OR REPLACE INTO db VALUES(?, ?, CURRENT_TIMESTAMP)"
        success = self.execute(query, (_id, software))
        if not(success):
            print("ERROR: failed to execute insert_db()", file=sys.stderr)
            sys.exit(1)

    def get_timestamp_db(self, _id, software):
        query = "SELECT timestamp FROM db WHERE fasta_id=? and software=?"
        success = self.execute(query, (_id, software))
        if success:
            ret = self.cur.fetchone()
            if ret is None:
                print("ERROR: {} is not exist in fasta table".format(_id), file=sys.stderr)
                sys.exit(1)
            return ret["timestamp"]
        else:
            print("ERROR: failed to execute get_timestamp_db()", file=sys.stderr)
            sys.exit(1)

