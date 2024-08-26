import os
import json
import csv
from datasets import load_from_disk


codon_mapping_dict = {
    "GCU": 'A', "GCC": 'A', "GCA": 'A', "GCG": 'A',
    "CGU": 'R', "CGC": 'R', "CGA": 'R', "CGG": 'R', "AGA": 'R', "AGG": 'R',
    "AAU": 'N', "AAC": "N",
    "GAU": "D", "GAC": "D",
    "UGU": "C", "UGC": "C",
    "GAA": "E", "GAG": "E",
    "CAA": "Q", "CAG": "Q",
    "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G",
    "CAU": "H", "CAC": "H",
    "AUU": "I", "AUC": "I", "AUA": "I",
    "UUA": "L", "UUG": "L", "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L",
    "AAA": "K", "AAG": "K",
    "AUG": "M",
    "UUU": "F", "UUC": "F",
    "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S", "AGU": "S", "AGC": "S",
    "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "UGG": "W", 
    "UAU": "Y", "UAC": "Y",
    "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V",
    "UAG": "Z", "UGA": "Z", "UAA": "Z"
}



def translate(cds_seq):
    cds_seq = cds_seq.replace('T', 'U')
    protein_seq = ''
    for idx in range(0, len(cds_seq)-2, 3):
        try:
            protein_seq += codon_mapping_dict[cds_seq[idx:idx+3]] 
        except:
            print(cds_seq[idx:idx+3])
            protein_seq += 'Z'
    return protein_seq

