import pickle
import json
from collections import OrderedDict
from itertools import chain
import torch
import numpy as np

def dedup_list(ls):
  return list(OrderedDict.fromkeys(ls))

def chunk_list(lst, k):
  return [lst[i:i + k] for i in range(0, len(lst), k)]

def concat(ls):
  return list(chain.from_iterable(ls))

def read_json(fn):
  with open(fn) as f:
    return json.load(f)

def write_json(obj, fn):
  with open(fn, 'w') as f:
    json.dump(obj, f, indent=2)

def read_pickle(fn):
  with open(fn, 'rb') as f:
    return pickle.load(f)

def write_pickle(r, fn):
  with open(fn, 'wb') as f:
    pickle.dump(r, f)

def cosine_sim(A, B):
  # Normalize A and B row-wise
  A_norm = A / A.norm(dim=1, keepdim=True)
  B_norm = B / B.norm(dim=1, keepdim=True)

  # Compute cosine similarity: A_norm @ B_norm.T
  cosine_sim = torch.mm(A_norm, B_norm.T)

  return cosine_sim

def split_inputs_by_interval(texts, num_partitions, partition):
  interval = len(texts) // num_partitions + 1
  start, end = partition * interval, (partition + 1) * interval
  return texts[start : end]

# format should be either json or npy or pkl
def merge(num_partitions: int, _fn: str, format: str):
  fn = f'{_fn}.{format}'

  results = []

  individuals = []
  for partition in range(num_partitions):
    if format == 'json':
      individuals.append(read_json(f'{_fn}_{partition}.json'))
    elif format == 'pkl':
      individuals.append(read_pickle(f'{_fn}_{partition}.pkl'))
    elif format == 'npy':
      individuals.append(np.load(f'{_fn}_{partition}.npy'))
    elif format in ['pt', 'pth']:
      individuals.append(torch.load(f'{_fn}_{partition}.{format}'))

  if format == 'json':
    for result in individuals:
      results += result
    write_json(results, fn)
  elif format == 'pkl':
    for result in individuals:
      results += result
    write_pickle(results, fn)
  elif format == 'npy':
    results = np.vstack(individuals)
    np.save(fn, results)
  elif format in ['pt', 'pth']:
    results = torch.vstack(individuals)
    torch.save(fn, results)
  
  print(len(results))