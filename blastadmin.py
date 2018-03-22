#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess
import shutil
import functools
from hashlib import md5

from src import helper

DB_FILEPATH = "{}/blastadmin.sq3".format(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = "{}/bin".format(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ["BLASTADMIN_DATA"]
SOFTWARES = [name for name in os.listdir(BIN_DIR) if os.path.isdir(os.path.join(BIN_DIR, name))]

dc = helper.DbController(DB_FILEPATH)
print = functools.partial(print, flush=True)

def issue_filepath_fasta(_id):
    fp = "{}/fasta/{}.fasta".format(DATA_DIR, _id)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def issue_filepath_db(_id, software):
    fp = "{}/{}/{}".format(DATA_DIR, software, _id)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def ask(message):
    while True:
        choice = input(message).lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

def clean_row_fasta(_id):
    exist = dc.exist_row_fasta(_id)
    if exist == 1:  #if exists
        message = "{} is already used as id. Do you want to overwrite? [y/N]: ".format(_id)
        if ask(message):
            dc.delete_row_fasta(_id)
        else:
            sys.exit(0)

def calc_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            checksum = md5(f.read()).hexdigest()
        return checksum
    except FileNotFoundError:
        return None

def calc_hash_database(_id, software):
    return dc.select_column_db(_id, software, column="timestamp")

def calc_hash_param(software):
    fp = "{}/{}/search.sh".format(BIN_DIR, software)
    return calc_hash(fp)

def insert_row_history(software, query, _id, result):
   	dc.insert_row_history(software, query, _id, result,
        calc_hash_param(software), calc_hash(query), calc_hash_database(_id, software), calc_hash(result))

def check_history(software, query, _id, result):
    row_lst = dc.select_rows_history(software, query, _id,
        calc_hash_param(software), calc_hash(query), calc_hash_database(_id, software))
    ret = None
    for row in row_lst:
        if row["hash_result"] == calc_hash(row["result"]):
            ret = row["result"]
            if ret == result: #prioritize result at the same filepath
                break
    return ret

def wget(args):
    clean_row_fasta(args._id)
    fastafp = issue_filepath_fasta(args._id)
    cmd = "{0}/wget.sh {1} {2}".format(BIN_DIR, args.ftp, fastafp)

    print("START: wget from {} to {}".format(args.ftp, fastafp))
    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_row_fasta(args._id, filepath=fastafp, origin=args.ftp)
        print("DONE: register {}".format(args._id))
    else:
        print("ERROR: fail to wget {}".format(args.ftp), file=sys.stderr)
        sys.exit(1)

def cp(args):
    clean_row_fasta(args._id)
    args.filepath = os.path.abspath(args.filepath)
    fastafp = issue_filepath_fasta(args._id)
    if args.subcommand == "cp":
        cmd = "cp --remove-destination {} {}".format(args.filepath, fastafp)
    elif args.subcommand == "ln":
        cmd = "ln -sf {} {}".format(args.filepath, fastafp)

    print("START: {0} from {1} to {2}".format(args.subcommand, args.filepath, fastafp))
    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_row_fasta(args._id, filepath=fastafp, origin=args.filepath)
        print("DONE: register {}".format(args._id))
    else:
        print("ERROR: fail to {} {}".format(args.subcommand, args.filepath), file=sys.stderr)
        sys.exit(1)

def createdb(args):
    fastafp = dc.select_column_fasta(args._id, column="filepath")
    if fastafp is None:
        print("ERROR: {} is not registered yet. Please register FASTA first by running wget/cp.".format(args._id), file=sys.stderr)
        sys.exit(1)

    dbfp = issue_filepath_db(args._id, args.software)
    cmd = "{0}/{1}/createdb.sh {2} {3}".format(BIN_DIR, args.software, fastafp, dbfp)

    print("START: create {} database for {}".format(args.software, args._id))
    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_row_db(args._id, args.software, filepath=dbfp)
        print("DONE: create {}".format(dbfp))
    else:
        print("ERROR: fail to create database from {}".format(fastafp), file=sys.stderr)
        sys.exit(1)

def search(args):
    #update database if necessary
    timestamp_fasta = dc.select_column_fasta(args._id, column="timestamp")
    timestamp_db = dc.select_column_db(args._id, args.software, column="timestamp")
    if (timestamp_db is None) or ( (timestamp_fasta is not None) and (timestamp_db < timestamp_fasta) ): #not exist or outdataed
        createdb(args)
        print()

    args.query = os.path.abspath(args.query)
    args.result = os.path.abspath(args.result)

    #check history and reuse result when possible
    result = check_history(args.software, args.query, args._id, args.result)
    if result is not None:
        print("DONE: found chached result in {}".format(result))
        if result != args.result:
            shutil.copy(result, args.result)
            insert_row_history(args.software, args.query, args._id, args.result)
            print("DONE: copy to {}".format(args.result))
        sys.exit(0)

    #need to run search
    dbfp = dc.select_column_db(args._id, args.software, column="filepath")
    cmd = "{0}/{1}/search.sh {2} {3} {4}".format(BIN_DIR, args.software, args.query, dbfp, args.result)

    print("START: search {} against {}".format(args.query, args._id))
    status = subprocess.call(cmd.split())
    if status == 0:
        insert_row_history(args.software, args.query, args._id, args.result)
        print("DONE: output result to {}".format(args.result))
    else:
        print("ERROR: search fail", file=sys.stderr)
        sys.exit(1)

def rm(args):
    # remove FASTA
    fastafp = dc.select_column_fasta(args._id, column="filepath")
    if fastafp is not None:  #if exists
        cmd = "rm {}".format(fastafp)
        status = subprocess.call(cmd.split())
        if status == 0:
            dc.delete_row_fasta(args._id)
            print("DONE: delete {}".format(fastafp))
        else:
            print("ERROR: fail to delete {}".format(fastafp), file=sys.stderr)
            sys.exit(1)

    # remove databases
    for software in SOFTWARES:
        dbfp = dc.select_column_db(args._id, software, column="filepath")
        if dbfp is not None:  #if exists
            cmd = "{}/{}/rm.sh {}".format(BIN_DIR, software, dbfp)
            status = subprocess.call(cmd.split())
            if status == 0:
                dc.delete_row_db(args._id, software)
                print("DONE: delete {}".format(dbfp))
            else:
                print("ERROR: fail to delete {}".format(dbfp), file=sys.stderr)
                sys.exit(1)

    # remove history log
    dc.delete_row_history(args._id)
    print("DONE: delete records on {}".format(args._id))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_wget = subparsers.add_parser("wget", help="register new FASTA by wget.")
    parser_wget.add_argument("_id", metavar="id", type=str, help="unique id.")
    parser_wget.add_argument("ftp", type=str, help="ftp address to wget FASTA from.")
    parser_wget.set_defaults(func=wget)

    parser_cp = subparsers.add_parser("cp", help="register new FASTA by cp.", aliases=["ln"])
    parser_cp.add_argument("_id", metavar="id", type=str, help="unique id.")
    parser_cp.add_argument("filepath", type=str, help="filepath to cp FASTA from.")
    parser_cp.set_defaults(func=cp)

    parser_createdb = subparsers.add_parser("createdb", help="create new database.")
    parser_createdb.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_createdb.add_argument("_id", metavar="id", type=str, help="FASTA to create database from (unique id).")
    parser_createdb.set_defaults(func=createdb)

    parser_search = subparsers.add_parser("search", help="search query against database.")
    parser_search.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_search.add_argument("_id", metavar="id", help="database to be searched (unique id).")
    parser_search.add_argument("query", help="query filepath.")
    parser_search.add_argument("result", help="result filepath.")
    parser_search.set_defaults(func=search)

    parser_rm = subparsers.add_parser("rm", help="given id, remove all the relavent data.")
    parser_rm.add_argument("_id", metavar="id", type=str, help="unique id.")
    parser_rm.set_defaults(func=rm)

    args = parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()
