#!/usr/bin/python3

from tree import newick_format, to_graph
from constants import *

import argparse
import math
import ncd
import os
import shutil
import sys
import tree_simplification as nj
import igraph as ig

# TODO: Apagar
import matplotlib.pyplot as plt
import seaborn as sns

def distance_matrix():
  return None

def clustering(directory, compression_name='ppmd', pairing_name='concat',
    is_parallel = True, **kwargs):
  sys.stderr.write('Performing NCD distance matrix calculation...\n')
  
  dist_matrix = ncd.distance_matrix_from_philip_format('./damicore-python/results/ncd-matrix.phylip')
  # dist_matrix = ncd.distance_matrix(directory, compression_name, pairing_name,
  #     is_parallel = is_parallel, **kwargs)

  # dist_matrix = distance_matrix()

  sys.stderr.write('\nSimplifying graph...\n')
  m, ids = ncd.to_matrix(dist_matrix)
  # print(m)
  
  tree = nj.neighbor_joining(m, ids)

  # input()

  sys.stderr.write('\nClustering elements...\n')
  g = to_graph(tree)

  node_output_filename = os.path.join(CLUSTER_OUTPUT_FILE)

  # Remover erros de precisao numerica
  for e in g.es:
    if e['length'] <= 0:
      e['length'] = 0.0
      print(e)

  # Show edge weights distribution
  # sns.displot(g.es['length'])
  # plt.title('Edge weights distribution (NEW FORMAT - 8)')
  # plt.show()

  # input('Press enter to write new cluster file...')

  fast_newman = g.community_fastgreedy(weights="length").as_clustering()
  with open(node_output_filename + "_fastgreedy" + ".txt", 'wt') as f:
    f.write(fast_newman.summary(verbosity=1))

  # Maps leaf ID to cluster number
  vertex_names = [v["name"] for v in g.vs]
  membership = {}
  for id_ in ids:
    membership[id_] = fast_newman.membership[ vertex_names.index(id_) ]

  return {
      'ncd': dist_matrix,
      'tree': tree,
      'fnames': ids,
      'graph': g,
      'node_clustering': fast_newman,
      'fname_cluster': membership,
  }

def calc_weights(lengths, min_length=1):
  n = len(lengths)
  mean = float(sum(lengths)) / n
  var = sum((l - mean)**2 for l in lengths) / n
  stddev = math.sqrt(var)
  scores = [(l - mean)/stddev for l in lengths]
  min_score = min(scores)
  norm_length = [min_length + (score - min_score) for score in scores]
  return norm_length

if __name__ == '__main__':
  parser = argparse.ArgumentParser(add_help=False, parents=[ncd.cli_parser()])
  parser.add_argument('--ncd-output', help='File to output NCD result')
  parser.add_argument('--tree-output', help='File to output tree result')
  parser.add_argument('--graph-image', help='File to output graph image')
  a = parser.parse_args()

  # TODO: Testar isso aqui
  sys.setrecursionlimit(5000)

  ## TODO(brunokim): The following is copied from ncd.py, refactor to extract to
  # a single place.
  #
  verbose = 0 if a.no_verbose else a.verbose
  if verbose != 1:
    sys.stderr.write('Note: verbosity level not implemented yet\n')

  if not os.path.exists(TMP_DIRECTORY) or not os.path.isdir(TMP_DIRECTORY):
    os.mkdir(TMP_DIRECTORY)
  if a.compressor == 'ppmd' and (
      not os.path.exists(PPMD_TMP_DIRECTORY) or not os.path.isdir(PPMD_TMP_DIRECTORY)):
    os.mkdir(PPMD_TMP_DIRECTORY)
 
  kwargs = {
      'pair_dir': TMP_DIRECTORY,
      'ppmd_tmp_dir': PPMD_TMP_DIRECTORY,
      'slowness': a.slowness,
      'model_order': a.model_order,
      'memory': a.memory,
      'block_size': a.block_size,
  }
  #
  ## end copied section ##

  d = clustering(a.directory,
      compression_name = a.compressor, pairing_name = a.pairing,
      is_parallel = True, **kwargs)
  
  print(d['node_clustering'].__getitem__(0))  

  # Outputs NCD step
  if a.ncd_output is not None:
    ncd_results = d['ncd']
    if a.format == 'phylip':
      ncd_out = ncd.phylip_format(ncd_results)
    else:
      ncd_out = ncd.csv_format(ncd_results)
    with open(a.ncd_output, 'wt') as f:
      f.write(ncd_out)

  # Outputs tree in Newick format
  if a.tree_output is not None:
    tree = d['tree']
    with open(a.tree_output, 'wt') as f:
      f.write(newick_format(tree))

  # Output cluster membership
  out = 'filename,cluster\n'
  for fname, cluster in d['fname_cluster'].items():
    out += '%s,%d\n' % (fname, cluster)

  if a.output is None:
    print(out)
  else:
    with open(a.output, 'wt') as f:
      f.write(out)
  
  # Remove tmp/
  if os.path.exists(TMP_DIRECTORY):
    shutil.rmtree(TMP_DIRECTORY)

