# CodeToolkits

This is a codebase for self-use-purpose.

## Data Process
- convert_lmdb2json.py: read lmdb format data and change it to json format

## Bio Related Tools
- mapping_id_by_uniprot.py: fetch ids from json file and mapping it to specific database ids (use for getting ccds). Currently it supports uniprotkb2ccds & pdb2uniprot.

- download_fasta_from_ena.py: download ccds fasta format data from ENA database. It needs id2ccdsid preprocess which may get from mapping_id_by_uniprot.py

- matching_and_truncating.py: use Smith-waterman algorithm to match cds sequence and protein sequence. save the data item which the matching score is over than threshold.   

## linux scripts useful functions
- random_port.sh: random a port which is still not used