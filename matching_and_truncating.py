import os
import json
import csv
import requests
import pandas as pd
import re
import sys
from tqdm import tqdm

from minineedle import needle, smith, core

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


def translate_cds_to_protein(cds_seq):
    cds_seq = cds_seq.replace('T', 'U')
    protein_seq = ''
    for idx in range(0, len(cds_seq)-2, 3):
        try:
            protein_seq += codon_mapping_dict[cds_seq[idx:idx+3]] 
        except:
            protein_seq += 'Z'
    return protein_seq


def SmithWaterman(protein_seq, translate_seq):
    alignment = smith.SmithWaterman(protein_seq, translate_seq)
    alignment.align()
    score = alignment.get_score()
    al1, al2 = alignment.get_aligned_sequences(core.AlignmentFormat.str)
    idx = translate_seq.find(al2)
    return score, idx, idx + len(al2)


# The Path where all download ccds files saved
CDS_ROOT = "outputs/ccds"

def match_and_truncate(protein_seq, uni_id):
    cds_seqs = []
    for id in uni_id:
        cds_path = os.path.join(CDS_ROOT, id+'.json')
        try:
            with open(cds_path, "r") as fr:
                cds_seqs += json.load(fr)
        except:
            print(cds_path)

    if len(cds_seqs) == 0:
        return False, None

    max_common_score, matching_cds_seq = 0, None
    for cds_seq in cds_seqs:
        if max_common_score / len(protein_seq) > 0.99:
            continue
        try:
            protein_bias_0 = translate_cds_to_protein(cds_seq) 
            max_score, st_idx, ed_idx = SmithWaterman(protein_seq, protein_bias_0)
            if max_score > max_common_score:
                max_common_score = max_score
                matching_cds_seq = cds_seq[st_idx*3: ed_idx*3]

            protein_bias_1 = translate_cds_to_protein(cds_seq[1:])
            max_score, st_idx, ed_idx = SmithWaterman(protein_seq, protein_bias_1)
            if max_score > max_common_score:
                max_common_score = max_score
                matching_cds_seq = cds_seq[st_idx*3+1: ed_idx*3+1]
            
            protein_bias_2 = translate_cds_to_protein(cds_seq[2:])
            max_score, st_idx, ed_idx = SmithWaterman(protein_seq, protein_bias_2)
            if max_score > max_common_score:
                max_common_score = max_score
                matching_cds_seq = cds_seq[st_idx*3+2: ed_idx*3+2]
        except:
            continue
    if max_common_score / len(protein_seq) > 0.9:
        return True, matching_cds_seq
    else:
        return False, None

# te path to save matching results
SAVE_ROOT = "outputs/csv"

def fetch_data_from_task(path):
    # Change according to task data format

    with open(json_path, "r") as fr:
        contents = json.load(fr)

    protein_seqs = {id2pdb[item['name']]: item['seq'] for item in contents}
    protein_label = {id2pdb[item['name']]: item['tertiary'] for item in contents}
    protein_mask = {id2pdb[item['name']]: item['valid_mask'] for item in contents}

    return [protein_seqs, protein_label, protein_mask]


def main():
    task_data_path = ""
    mapping_ids_path = ""
    save_name = ""

    task_data = fetch_data_from_task(task_data_path)

    with open(mapping_ids_path, "r") as fr:
        contents = json.load(fr)
     
    with open(os.path.join(SAVE_ROOT, save_name), "w") as fw:
        writer = csv.writer(fw)

        success_match_num = 0
        for i, key in enumerate(contents):
            print("matching {}/{} working!".format(i, len(contents)))
            sys.stdout.flush()
            status, matching_seqs = match_and_truncate(task_data[0][key], contents[key])
            
            if status is True:
                save_row = [key, matching_seqs]
                save_row += [item[key] for item in task_data]
                writer.writerow(save_row)
                success_match_num += 1

    print("success matching nums: ",  success_match_num)


if __name__ == "__main__":
    main()
