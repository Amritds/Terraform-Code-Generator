
import os
import json
import pickle

import numpy as np
from numpy.linalg import norm

import voyageai


# Set api keys
with open('config/api_keys.json','r') as f:
    api_keys = json.load(f)
    os.environ["VOYAGE_API_KEY"] = api_keys["VOYAGE_API_KEY"]

def get_sim_score(A, B):
    """Compute similairty between two embeddings"""
    A = np.array(A)
    B = np.array(B)
    sim = np.dot(A,B)/(norm(A)*norm(B))
    return sim

class FileRetriever():
    def __init__(self, store_load_file, threshold_retrival=0.65):
        """Intitialize parameters, and Embedding Client, Load code snippets, vector embeddings and source filenames"""
        # Set sim score for retrieval
        self.threshold_retrival = threshold_retrival
        self.store_load_file = store_load_file
        # Load the store
        with open(self.store_load_file, 'rb') as f:
            self.store = pickle.load(f)
    
        # Initialize the voyage client
        self.vo = voyageai.Client()
    
    def retrieve_files_from_query(self, query):
        """Search the store for matching code snippets and return corresponding filenames  (RAG)"""
        # Embed the query
        query_embeded = self.vo.embed([query], model="voyage-code-3", input_type="document").embeddings[0]

        # Search the store and return corresponding filenames
        retrival_files = []
        for elem in self.store:
            sim = get_sim_score(query_embeded, elem[0])
            if sim > self.threshold_retrival and elem[1] not in retrival_files:
                retrival_files.append(elem[1])
        
        return retrival_files
