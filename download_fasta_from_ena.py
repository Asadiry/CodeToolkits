import os
import json
import requests
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

ENA_WEB_API = "https://www.ebi.ac.uk/ena/browser/api/fasta/"

MAX_CALLS_PER_SECOND = 30

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def download_from_ena(results, save_root):
    request_failed_list = []
    headers = {
        'Connection':'close'
    }

    for name, ccds_ids in tqdm(results.items()):
        save_path = os.path.join(save_root, name + '.json')
        if os.path.exists(save_path):
            continue

        url = ENA_WEB_API + "%2C".join(ccds_ids[:15])
        try:
            response = requests.get(url, headers=headers)
            fasta_content = response.text    
        except:
            request_failed_list.append(name)
            print(f"request failed, status code: {response.status_code}")
            print("request text: ", response.text)
            continue

        fasta_content = fasta_content.split("\n")
        ccds_seqs, seq = [], ''
        for line in fasta_content:
            if len(line) == 0:
                continue
            if line[0] == '>':
                ccds_seqs.append(seq)
                seq = ''
                continue
            seq += line
        ccds_seqs.append(seq)
        ccds_seqs = ccds_seqs[1:]

    
        with open(save_path, "w") as fw:
            json.dump(ccds_seqs, fw)

    return request_failed_list


# Need to change according to different storage format
def fetch_ids_from_json(path):
   with open(ids_path, "r") as fr:
        contents = json.load(fr)
    ids = contents["results"]
    return ids


if __name__ == "__main__":
    ids_path = ""
    save_root = "outputs/ccds"

 
    ids = fetch_ids_from_json(ids_path)
    
    failed_ids = download_from_ena(ids, save_root)
    with open(os.path.join(save_root, "failed_ids.json"), "w") as fw:
        json.dump(failed_ids, fw)
        print("failed ids: ", failed_ids)
