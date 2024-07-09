from pathlib import Path

import lmdb
import pickle as pkl
import numpy as np
import json

from torch.utils.data import Dataset

class LMDBDataset(Dataset):

    def __init__(self,
                 data_file: str,
                 in_memory: bool = False):

        data_file = Path(data_file)
        if not data_file.exists():
            raise FileNotFoundError(data_file)

        env = lmdb.open(str(data_file), max_readers=1, readonly=True,
                        lock=False, readahead=False, meminit=False)

        with env.begin(write=False) as txn:
            num_examples = pkl.loads(txn.get(b'num_examples'))

        if in_memory:
            cache = [None] * num_examples
            self._cache = cache

        self._env = env
        self._in_memory = in_memory
        self._num_examples = num_examples


    def __len__(self) -> int:
        return self._num_examples


    def __getitem__(self, index: int):
        if not 0 <= index < self._num_examples:
            raise IndexError(index)

        if self._in_memory and self._cache[index] is not None:
            item = self._cache[index]
        else:
            with self._env.begin(write=False) as txn:
                item = pkl.loads(txn.get(str(index).encode()))
                if 'id' not in item:
                    item['id'] = str(index)
                if self._in_memory:
                    self._cache[index] = item
        return item


def type2normal(x):
    if type(x) is str:
        return x
    elif type(x) is bytes:
        return x.decode("utf-8")
    elif type(x) is np.ndarray:
        return x.tolist()
    return x


def convert_lmdb2json(lmdb_path: str, json_path: str):
    lmdb_data = LMDBDataset(lmdb_path)
    json_data = []
    for item in lmdb_data:
        item = dict({ k:type2normal(v) for k,v in item.items()})
        json_data.append(item)

    with open(json_path, "w") as fw:
        json.dump(json_data, fw)

    print("convert json finish.")
