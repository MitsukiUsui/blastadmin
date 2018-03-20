# blastadmin

blastadmin is a command wrapper which enables users to run multiple similarity search softwares in the same interface.

## For Who?
* For those who are overwhelmed with thousands of similarity search commands which are slightly different each other.  
    -> blastadmin provides you a **simplified wrapped interface!**
* For those who are tired of remembering and specifying long filepath to the database every time you run a search.  
    -> blastadmin enables you to **specify database by a unique identifier you assign**, such as "nr"!
* For those who don't want to pay attention in avoiding a search with the same query-database pair, in order not to waste computer resources.  
    -> **blastadmin keeps track of the search history** and run a search only when needed!

## Installation
### Requirements
* Python3.*
* sqlite3

### Setup
```
git clone https://github.com/MitsukiUsui/blastadmin.git
cd blastadmin
sqlite3 blastadmin.sq3 < ./src/schema.sql
echo 'export PATH=$(pwd):$PATH' >> ~/.bash_profile
#echo 'export BLASTADMIN_DATA="/path/to/data/directory/you/want"' >> ~/.bash_profile
```

## Usage
blastadmin.py has 3 types of subcommands, that is `wget/cp`, `createdb`, and `search`. Here is a simple example below.

```
blastadmin.py wget ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz ecoli-genome
blastadmin.py createdb blastn ecoli-genome
blastadmin.py search blastn ./query.fna ecoli-genome ./result.tsv
```

First, you need to register FASTA file to blastadmin by wget/cp with unique identifier you provide. `wget` will automatically uncompress `.gz` file.
```
blastadmin.py wget <ftp address> <id>
blastadmin.py cp <local filepath> <id>
```

Second, you create a database using the FASTA you registered. This command will execute `./bin/<software>/createdb.sh` inside. Actually, you don't need to explicitly call this command because `search` will call `createdb` first if the database is yet to be created.
```
blastadmin.py createdb <software> <id>
```

Last, you run similarity search with the database you created. This command will execute `./bin/<software>/search.sh` inside.
```
blastadmin.py search <software> <query> <id> <result>
```
