#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess
import logging
import shutil
import functools
from hashlib import md5

from src import DbController


DB_FILEPATH = "{}/blastadmin.sq3".format(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = "{}/bin".format(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ["BLASTADMIN_DATA"]
SOFTWARES = [name for name in os.listdir(BIN_DIR) if os.path.isdir(os.path.join(BIN_DIR, name))]

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
dc = DbController(DB_FILEPATH)


def issue_filepath_fasta(id_):
    fp = "{}/fasta/{}.fasta".format(DATA_DIR, id_)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def issue_filepath_db(id_, software):
    fp = "{}/{}/{}".format(DATA_DIR, software, id_)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def ask(message):
    while True:
        choice = input(message).lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

def clean_row_fasta(id_):
    logging.debug("checking if \'{}\' is new id".format(id_))
    exist = dc.exist_row_fasta(id_)
    if exist == 1:  #if exists
        logging.debug("id already exists")
        message = "\'{}\' is already used as id. Do you want to overwrite? [y/N]: ".format(id_)
        if ask(message):
            logging.debug("deletion acceptted")
            dc.delete_row_fasta(id_)
        else:
            logging.debug("deletion not acceptted. aborting...")
            sys.exit(0)
    else:
        logging.debug("confirmed to be new id")

def calc_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            checksum = md5(f.read()).hexdigest()
        return checksum
    except FileNotFoundError:
        return None

def calc_hash_database(id_, software):
    return dc.select_column_db(id_, software, column="timestamp")

def calc_hash_param(software):
    fp = "{}/{}/search.sh".format(BIN_DIR, software)
    return calc_hash(fp)

def insert_row_history(software, query, id_, result):
    dc.insert_row_history(software, query, id_, result,
        calc_hash_param(software), calc_hash(query), calc_hash_database(id_, software), calc_hash(result))

def check_history(software, query, id_, result):
    row_lst = dc.select_rows_history(software, query, id_,
        calc_hash_param(software), calc_hash(query), calc_hash_database(id_, software))
    ret = None
    for row in row_lst:
        if row["hash_result"] == calc_hash(row["result"]):
            ret = row["result"]
            if ret == result: #prioritize result at the same filepath
                break
    return ret

def wget(args):
    logging.info("wget called with id={}, ftp={}".format(args.id_, args.ftp))

    clean_row_fasta(args.id_)
    fastafp = issue_filepath_fasta(args.id_)
    cmd = "{0}/wget.sh {1} {2}".format(BIN_DIR, args.ftp, fastafp)

    logging.debug("execute \'{}\'".format(cmd))
    status = subprocess.call(cmd.split())
    if status == 0:
        logging.debug("cmd succeeded")
        dc.insert_row_fasta(args.id_, filepath=fastafp, origin=args.ftp)
        logging.info("registered \'{}\'".format(args.id_))
    else:
        logging.error("cmd failed\nAborting...")
        sys.exit(1)

def cp(args):
    logging.info("{} called with id={}, filepath={}".format(args.subcommand, args.id_, args.filepath))

    clean_row_fasta(args.id_)
    args.filepath = os.path.abspath(args.filepath)
    fastafp = issue_filepath_fasta(args.id_)
    if args.subcommand == "cp":
        cmd = "cp --remove-destination {} {}".format(args.filepath, fastafp)
    elif args.subcommand == "ln":
        cmd = "ln -sf {} {}".format(args.filepath, fastafp)

    logging.debug("execute \'{}\'".format(cmd))
    status = subprocess.call(cmd.split())
    if status == 0:
        logging.debug("cmd succeeded")
        dc.insert_row_fasta(args.id_, filepath=fastafp, origin=args.filepath)
        logging.info("register \'{}\'".format(args.id_))
    else:
        logging.error("cmd failed\nAborting...")
        sys.exit(1)

def createdb(args):
    logging.info("createdb called with software={}, id={}".format(args.software, args.id_))

    fastafp = dc.select_column_fasta(args.id_, column="filepath")
    if fastafp is None:
        logging.warn("\'{}\' is not registered yet. Please register FASTA first by running wget/cp.\nAborting...".format(args.id_))
        sys.exit(1)
    dbfp = issue_filepath_db(args.id_, args.software)
    cmd = "{0}/{1}/createdb.sh {2} {3}".format(BIN_DIR, args.software, fastafp, dbfp)

    logging.debug("execute \'{}\'".format(cmd))
    status = subprocess.call(cmd.split())
    if status == 0:
        logging.debug("cmd succeeded")
        dc.insert_row_db(args.id_, args.software, filepath=dbfp)
        logging.info("createdb \'{}\'".format(args.id_))
    else:
        logging.error("cmd failed\nAborting...")
        sys.exit(1)

def search(args):
    logging.info("search called with software={}, id={}, query={}, result={}".format(args.software, args.id_, args.query, args.result))

    #update database if necessary
    timestamp_fasta = dc.select_column_fasta(args.id_, column="timestamp")
    timestamp_db = dc.select_column_db(args.id_, args.software, column="timestamp")
    if (timestamp_db is None) or ( (timestamp_fasta is not None) and (timestamp_db < timestamp_fasta) ): #not exist or outdataed
        logging.debug("call createdb first as timestamp_fasta = {} and timestamp_db = {}".format(timestamp_fasta, timestamp_db))
        createdb(args)

    args.query = os.path.abspath(args.query)
    args.result = os.path.abspath(args.result)

    #check history and reuse result when possible
    result = check_history(args.software, args.query, args.id_, args.result)
    if result is not None:
        logging.info("found chached result in {}".format(result))
        if result != args.result:
            logging.debug("cp {} to {}".format(result, args.result))
            shutil.copy(result, args.result)
            insert_row_history(args.software, args.query, args.id_, args.result)
        sys.exit(0)

    #need to run search
    dbfp = dc.select_column_db(args.id_, args.software, column="filepath")
    cmd = "{0}/{1}/search.sh {2} {3} {4}".format(BIN_DIR, args.software, args.query, dbfp, args.result)

    logging.debug("execute \'{}\'".format(cmd))
    status = subprocess.call(cmd.split())
    if status == 0:
        logging.debug("cmd succeeded")
        insert_row_history(args.software, args.query, args.id_, args.result)
        logging.info("output result to {}".format(args.result))
    else:
        logging.error("cmd failed\nAborting...")
        sys.exit(1)

def rm(args):
    logging.info("rm called with id={}".format(args.id_))

    # remove FASTA
    logging.debug("check FASTA")
    fastafp = dc.select_column_fasta(args.id_, column="filepath")
    if fastafp is not None:  #if exists
        cmd = "rm {}".format(fastafp)
        logging.debug("execute \'{}\'".format(cmd))
        status = subprocess.call(cmd.split())
        if status == 0:
            dc.delete_row_fasta(args.id_)
            logging.debug("removed FASTA")
        else:
            logging.error("cmd failed\nAborting...")
            sys.exit(1)

    # remove databases
    for software in SOFTWARES:
        logging.debug("check {}".format(software))
        dbfp = dc.select_column_db(args.id_, software, column="filepath")
        if dbfp is not None:  #if exists
            cmd = "{}/{}/rm.sh {}".format(BIN_DIR, software, dbfp)
            status = subprocess.call(cmd.split())
            logging.debug("execute \'{}\'".format(cmd))
            if status == 0:
                dc.delete_row_db(args.id_, software)
                logging.debug("removed {}".format(software))
            else:
                logging.error("cmd failed\nAborting...")
                sys.exit(1)

    # remove history log
    dc.delete_row_history(args.id_)
    logging.info("deleted all files and records about \'{}\'".format(args.id_))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_wget = subparsers.add_parser("wget", help="register new FASTA by wget.")
    parser_wget.add_argument("id_", metavar="id", type=str, help="unique id.")
    parser_wget.add_argument("ftp", type=str, help="ftp address to wget FASTA from.")
    parser_wget.set_defaults(func=wget)

    parser_cp = subparsers.add_parser("cp", help="register new FASTA by cp.", aliases=["ln"])
    parser_cp.add_argument("id_", metavar="id", type=str, help="unique id.")
    parser_cp.add_argument("filepath", type=str, help="filepath to cp FASTA from.")
    parser_cp.set_defaults(func=cp)

    parser_createdb = subparsers.add_parser("createdb", help="create new database.")
    parser_createdb.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_createdb.add_argument("id_", metavar="id", type=str, help="FASTA to create database from (unique id).")
    parser_createdb.set_defaults(func=createdb)

    parser_search = subparsers.add_parser("search", help="search query against database.")
    parser_search.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_search.add_argument("id_", metavar="id", help="database to be searched (unique id).")
    parser_search.add_argument("query", help="query filepath.")
    parser_search.add_argument("result", help="result filepath.")
    parser_search.set_defaults(func=search)

    parser_rm = subparsers.add_parser("rm", help="given id, remove all the relavent data.")
    parser_rm.add_argument("id_", metavar="id", type=str, help="unique id.")
    parser_rm.set_defaults(func=rm)

    args = parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()
