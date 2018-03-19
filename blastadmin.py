#!/usr/bin/env python3

import sys
import os
import argparse
import subprocess

from src import helper

DB_FILEPATH = "{}/blastadmin.sq3".format(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = "{}/bin".format(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = "/home/mitsuki/sandbox/blastadmin/data"
SOFTWARES = [name for name in os.listdir(BIN_DIR) if os.path.isdir(os.path.join(BIN_DIR, name))]

dc = helper.DbController(DB_FILEPATH)

def get_fasta_filepath(_id):
    return "{}/fasta/{}.fasta".format(DATA_DIR, _id)

def get_db_filepath(_id, software):
    return "{}/{}/{}".format(DATA_DIR, software, _id)

def ask(message):
    while True:
        choice = input(message).lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

def clean_fastaid(_id):
    exist = dc.exist_fasta(_id)
    if exist == 1:  #if exists
        message = "{} is already used as id. Do you want to overwrite? [y/N]: ".format(_id)
        if ask(message):
            dc.delete_fasta(_id)
        else:
            exit(0)

def wget(args):
    clean_fastaid(args.id)
    fastafp = get_fasta_filepath(args.id)
    cmd = "{0}/wget.sh {1} {2}".format(BIN_DIR, args.ftp, fastafp)

    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_fasta(args.id, origin=args.ftp)
        print("DONE: register {}".format(args.id))
    else:
        print("ERROR: fail to wget {}".format(args.ftp), file=sys.stderr)
        exit(1)

def cp(args):
    clean_fastaid(args.id)
    fastafp = get_fasta_filepath(args.id)
    cmd = "cp {} {}".format(args.filepath, fastafp)

    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_fasta(args.id, origin=args.filepath)
        print("DONE: register {}".format(args.id))
    else:
        print("ERROR: fail to copy {}".format(args.filepath), file=sys.stderr)
        exit(1)

def createdb(args):
    exist = dc.exist_fasta(args.fasta)
    if exist == 0:
        print("ERROR: {} is not registered yet. Please register first by running wget/cp.".format(args.fasta), file=sys.stderr)
        exit(1)

    fastafp = get_fasta_filepath(args.fasta)
    dbfp = get_db_filepath(args.fasta, args.software)
    cmd = "{0}/{1}/createdb.sh {2} {3}".format(BIN_DIR, args.software, fastafp, dbfp)

    status = subprocess.call(cmd.split())
    if status == 0:
        dc.insert_db(args.fasta, args.software)
        print("DONE: create {}".format(dbfp))
    else:
        print("ERROR: fail to create database from {}".format(fastafp), file=sys.stderr)
        exit(1)

def search(args):
    dbfp = get_db_filepath(args.fasta, args.software)
    cmd = "{0}/{1}/search.sh {2} {3} {4}".format(BIN_DIR, args.software, args.query, dbfp, args.result)

    status = subprocess.call(cmd.split())
    if status == 0:
        print("DONE: output result to {}".format(args.result))
    else:
        print("ERROR: search fail", file=sys.stderr)
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_wget = subparsers.add_parser("wget", help="wget new FASTA.")
    parser_wget.add_argument("ftp", type=str, help="ftp address to wget FASTA from.")
    parser_wget.add_argument("id", type=str, help="unique id.")
    parser_wget.set_defaults(func=wget)

    parser_cp = subparsers.add_parser("cp", help="register new FASTA.")
    parser_cp.add_argument("filepath", type=str, help="filepath to copy FASTA from.")
    parser_cp.add_argument("id", type=str, help="unique id.")
    parser_cp.set_defaults(func=cp)

    parser_createdb = subparsers.add_parser("createdb", help="create new database.")
    parser_createdb.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_createdb.add_argument("fasta", type=str, help="FASTA to create database from (unique id).")
    parser_createdb.set_defaults(func=createdb)

    parser_search = subparsers.add_parser("search", help="search query against database.")
    parser_search.add_argument("software", type=str, choices=SOFTWARES, help="software to run")
    parser_search.add_argument("query", help="query filepath.")
    parser_search.add_argument("database", help="database to be searched (unique id).")
    parser_search.add_argument("result", help="result filepath.")
    parser_search.set_defaults(func=search)

    args = parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()
