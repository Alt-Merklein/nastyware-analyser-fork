import os
import sys
import argparse
import numpy as np
from scipy.spatial.distance import cosine
from export_new_format_import_files import delete_duplicates

# Paralell libraries
from multiprocessing import Pool


# Global variable to store vectors
vectors = None

def init_pool(v):
    """Initialize the pool with the global vectors."""
    global vectors
    vectors = v

def calculate_cosine(index_pair):
    """Calculate cosine distance between two vectors."""
    i, j = index_pair
    return (i, j, cosine(vectors[i], vectors[j]))

def load_vectors_from_files(directory, files):
    """Load vectors from files in the specified directory."""
    paths = [os.path.join(directory, f) for f in files]
    vectors = []

    for path in paths:
        with open(path, 'r') as f:
            content = f.read().strip()  # Ex: "010110"
            vector = np.fromiter(map(int, content), dtype=np.uint32)
            vectors.append(vector)

    return vectors

def extract_index_from_phylip(phylip_path):
    """Extracts index of a distance matrix from a phylip file"""
    with open(phylip_path, 'r') as f:
        lines = f.readlines()[1:] # Pula linha com quantidade de arquivos

    nomes = []
    matriz = []

    for line in lines:
        if line.strip():
            partes = line.strip().split()
            nome = partes[0]
            distancias = list(map(float, partes[1:]))

            nomes.append(nome)
            matriz.append(distancias)
    
    return nomes, np.array(matriz, dtype=np.float32)

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

def create_dist_matrix_from_zero(formated_directory, files):
    """
        Creates a new distance matrix from a directory of files using parallelized Cosine Distance
        directory: Directory containing files to compare 2 by 2
        return: Distance matrix and order of files used
    """

    vecs = load_vectors_from_files(formated_directory, files)
    n = len(vecs)
    indices = [(i, j) for i in range(n) for j in range(i + 1, n)]
    dist_matrix = np.zeros((n, n), dtype=np.float32)

    with Pool(initializer=init_pool, initargs=(vecs,)) as pool:
        results = pool.map(calculate_cosine, indices)

    for i, j, d in results:
        dist_matrix[i][j] = d
        dist_matrix[j][i] = d

    return dist_matrix, files

def update_existing_matrix(directory, old_files, old_matrix, new_files):
    """
        Updates an existing distance matrix with new files using parallelized Cosine Distance\n
        directory: Directory containing files to compare 2 by 2;
        old_files: List of files already processed;
        old_matrix: Distance matrix already calculated;
        new_files: List of new files to be added;
        return: Updated distance matrix and all files used.
    """
    all_files = old_files + new_files
    all_vectors = load_vectors_from_files(directory, all_files)

    n_old = len(old_files)
    n_new = len(new_files)
    n_total = len(all_files)

    updated_matrix = np.zeros((n_total, n_total), dtype=np.float32)
    updated_matrix[:n_old, :n_old] = old_matrix  # mantém as distâncias antigas

    # pares (novo vs novo) e (novo vs antigo)
    indices = []
    for i in range(n_old, n_total):
        for j in range(0, i):
            indices.append((i, j))

    with Pool(initializer=init_pool, initargs=(all_vectors,)) as pool:
        results = pool.map(calculate_cosine, indices)

    for i, j, d in results:
        updated_matrix[i][j] = d
        updated_matrix[j][i] = d

    return updated_matrix, all_files


def create_phylip_coss_distance(directory, input_file, output_file):
    """
        Creates a distance matrix from a directory of files using Cosine Distance;
        directory: Directory containing files to compare 2 by 2;
        output_file: File to output the result.
    """

    if os.path.exists(input_file):
        print("Matriz anterior encontrada. Carregando...")
        
        # Verifica se o arquivo é um arquivo phylip
        old_files, old_matrix = extract_index_from_phylip(input_file)

        # Lista arquivos da matriz e exclui arquivos duplicados
        preserve_set = set(old_files)
        delete_duplicates(directory, preserve_files=preserve_set)

        # Lista arquivos no diretório
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        # Identifica arquivos ainda não processados
        processed_files = set(old_files)
        new_files = [f for f in files if f not in processed_files]
        
        # Identifica arquivos que foram removidos
        actual_formated_files = set(files)
        removed_files = processed_files - actual_formated_files

        # Se arquivos foram removidos, não é possível atualizar a matriz
        if removed_files:
            print(f"Arquivos removidos: {removed_files}")
            print("\n \t ======= ERRO =======")
            print("\t Os arquivos listados foram removidos do diretório. A matriz não pode ser atualizada.")
            print("\t *** Soluções:")
            print("\t 1) Delete o arquivo da matriz antiga para recalcular uma matriz do zero; ou")
            print("\t 2) Adicione os vetores removidos ao diretório e execute novamente para atualizar a matriz existente.") 
            print("\t ====================")
            sys.exit(1)

        # Se não houver novos arquivos, não é necessário atualizar a matriz
        if not new_files:
            print("Nenhum novo arquivo encontrado. Nada a atualizar.")
            return

        # Se houver novos arquivos, atualiza e exporta a matriz
        print(f"Atualizando matriz com {len(new_files)} novos arquivos...")
        updated_matrix, all_files = update_existing_matrix(directory, old_files, old_matrix, new_files)
        export_phylip_file(updated_matrix, all_files, output_file)

    else:
        print("Nenhuma matriz existente. Iniciando do zero")
        
        # Remove arquivos duplicados
        delete_duplicates(directory)
        
        # Lista arquivos no diretório
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # Cria e exporta a matriz
        dist_matrix, filename_order = create_dist_matrix_from_zero(directory, files)
        export_phylip_file(dist_matrix, filename_order, output_file)

# ==========================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='Directory with the files to be vetorized', required=True)
    parser.add_argument('-o', '--phylip-output', help='File to output tree result', default="./ncd-matrix.phylip")
    args = parser.parse_args()

    create_phylip_coss_distance(args.directory, args.phylip_output)


if __name__ == '__main__':
    main()