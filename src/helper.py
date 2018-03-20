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

    def execute(self, sql, arg=None):
        try:
            if arg is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, arg)
            self.con.commit()
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            print(e)
            return False
        return True

    def exist_row_fasta(self, _id):
        sql = "SELECT EXISTS(SELECT 1 from fasta WHERE fasta_id=?)"
        success = self.execute(sql, (_id,))
        if success:
            return list(self.cur.fetchone().values())[0]
        else:
            print("ERROR: failed to execute exist_row_fasta()", file=sys.stderr)
            sys.exit(1)

    def insert_row_fasta(self, _id, origin):
        sql = "INSERT INTO fasta VALUES(?, ?, CURRENT_TIMESTAMP)"
        success = self.execute(sql, (_id, origin))
        if not(success):
            print("ERROR: failed to execute insert_row_fasta()", file=sys.stderr)
            sys.exit(1)

    def delete_row_fasta(self, _id):
        sql = "DELETE FROM fasta WHERE fasta_id=?"
        success = self.execute(sql, (_id,))
        if not(success):
            print("ERROR: failed to execute delete_row_fasta()", file=sys.stderr)
            sys.exit(1)

    def get_timestamp_fasta(self, _id):
        sql = "SELECT timestamp FROM fasta WHERE fasta_id=?"
        success = self.execute(sql, (_id,))
        if success:
            ret = self.cur.fetchone()
            if ret is None:
                return "-1"
            return ret["timestamp"]
        else:
            print("ERROR: failed to execute get_timestamp_fasta()", file=sys.stderr)
            sys.exit(1)

    def insert_row_db(self, _id, software):
        sql = "INSERT OR REPLACE INTO db VALUES(?, ?, CURRENT_TIMESTAMP)"
        success = self.execute(sql, (_id, software))
        if not(success):
            print("ERROR: failed to execute insert_row_db()", file=sys.stderr)
            sys.exit(1)

    def get_timestamp_db(self, _id, software):
        sql = "SELECT timestamp FROM db WHERE fasta_id=? and software=?"
        success = self.execute(sql, (_id, software))
        if success:
            ret = self.cur.fetchone()
            if ret is None:
                return "-1"
            return ret["timestamp"]
        else:
            print("ERROR: failed to execute get_timestamp_db()", file=sys.stderr)
            sys.exit(1)

    def insert_row_history(self, software, query, database, result, hash_param, hash_query, hash_database, hash_result):
        sql = "INSERT INTO history VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
        success = self.execute(sql, (software, query, database, result, hash_param, hash_query, hash_database, hash_result))
        if not(success):
            print("ERROR: failed to execute insert_row_history()", file=sys.stderr)
            sys.exit(1)

    def select_row_history(self, software, query, database,  hash_param, hash_query, hash_database):
        sql = "SELECT result, hash_result FROM history WHERE software=? and query=? and database=? and hash_param=? and hash_query=? and hash_database=?"
        success = self.execute(sql, (software, query, database, hash_param, hash_query, hash_database))
        if success:
            return self.cur.fetchall()
        else:
            print("ERROR: failed to execute select_row_history()", file=sys.stderr)
            sys.exit(1)

