import os
import argparse
import numpy as np
from scipy.spatial.distance import cosine

# Paralell libraries
import multiprocessing as mp

def create_dist_matrix(directory):
    """
        Creates a distance matrix from a directory of files using Cosine Distance
        directory: Directory containing files to compare 2 by 2
        return: Distance matrix and order of files used
    """

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    dist_matrix = np.zeros((len(files), len(files)))
    


    for i in range(0, len(files) - 1):
        print(f"Processing {i} / {len(files)}", end='\r')
        
        fname1 = os.path.join(directory, files[i])
        f1 = open(fname1, 'rb').read()
        f1 = np.fromiter(map(int, list(f1.decode())), dtype=np.uint32)

        num_cpus = mp.cpu_count()
        pool = mp.Pool(num_cpus)
        manager = mp.Manager()
        queue = manager.Queue()

        for j in range(i + 1, len(files)):
            pool.apply_async(calculate_cosine_distance, args=(f1, os.path.join(directory, files[j]), j, queue))

        pool.close()
        pool.join()

        while not queue.empty():
            result = queue.get()
            dist_matrix[i][result[0]] = result[1]
            dist_matrix[result[0]][i] = result[1]

    print()

    return dist_matrix, files

def calculate_cosine_distance(f1, fname2, j, queue):
    f2 = open(fname2, 'rb').read()
    f2 = np.fromiter(map(int, list(f2.decode())), dtype=np.uint32)
    dist = cosine(f1, f2)
    queue.put((j, dist))


def export_phylip_file(dist_matrix, filename_order, output_file):
    """
        Export distance matrix to a phylip file
        dist_matrix: Distance matrix
        filename_order: Order of files used to create the distance matrix
        output_file: File to output the result
    """

    with open(output_file, 'wt') as f:
        f.write(str(len(filename_order)) + "\n")
        for i in range(0, len(filename_order)):
            f.write(filename_order[i] + " ")
            for j in range(0, len(filename_order)):
                f.write(str(dist_matrix[i][j]) + " ")
            f.write("\n")

def create_phylip_coss_distance(directory, output_file):
    dist_matrix, filename_order = create_dist_matrix(directory)
    export_phylip_file(dist_matrix, filename_order, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='File to output NCD result', required=True)
    parser.add_argument('-o', '--phylip-output', help='File to output tree result', default="./ncd-matrix.phylip")
    args = parser.parse_args()

    dist_matrix, filename_order = create_dist_matrix(args.directory)

    export_phylip_file(dist_matrix, filename_order, args.phylip_output)



if __name__ == '__main__':
    main()