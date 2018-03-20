# blastadmin

blastadmin is a command wrapper which enables users to run multiple similarity search software in a same interface.

## For Who?
* For those who are overwhelmed with thousands of similarity search commands which are slightly different each other.  
    -> blastadmin provides you a **simple wrapped interface!**
* For those who are tired of remembering and specifying long filepath to the database every time you run a search.  
    -> blastadmin enables you to specify database by a **unique identifier you assign**, such as "nr"!
* For those who don't want to pay attention to avoiding a search with the same query-database pair, in order not to waste computer resources.  
    -> blastadmin keeps track of the **search history** and runs a search only when needed!

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
echo 'export BLASTADMIN_DATA="/path/to/data/directory/you/want"' >> ~/.bash_profile
```

## Usage
blastadmin.py has 3 types of subcommands, that is `wget/cp`, `createdb`, and `search`. Here is a simple example below.

### Example
```
blastadmin.py wget ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz ecoli-genome
blastadmin.py createdb blastn ecoli-genome
blastadmin.py search blastn ./demo/query.fna ecoli-genome ./result.tsv
```

### Detail
First, you need to register a FASTA file to blastadmin by `wget/cp` with a unique identifier you provide. `wget` will automatically uncompress `.gz` file.
```
blastadmin.py wget <ftp address> <id>
blastadmin.py cp <local filepath> <id>
```

Second, you create a database with the FASTA you registered. This command will execute `./bin/<software>/createdb.sh` inside. Actually, you don't need to explicitly call this command because `search` will call `createdb` first if the database is yet to be created or outdated.
```
blastadmin.py createdb <software> <id>
```

Last, you run similarity search with the database you created. This command will execute `./bin/<software>/search.sh` inside.
```
blastadmin.py search <software> <query> <id> <result>
```

