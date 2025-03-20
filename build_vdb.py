import os
import json
import pickle

import voyageai

# Set api keys
with open('config/api_keys.json', 'r') as f:
    api_keys = json.load(f)
    os.environ["VOYAGE_API_KEY"] = api_keys["VOYAGE_API_KEY"]
    
# Set code directory, save file paths, chunk and overlap sizes
with open('config/general_config.json', 'r') as f:
    config = json.load(f)
    code_dir = config["code_dir"]
    storage_dir = config["storage_dir"]
    store_save_file = config["store_save_file"]
    chunk_size = config["chunk_size"]
    overlap = config["overlap"]

# Initialize the Voyage Client
vo = voyageai.Client()

tf_file_names = []
tf_file_code = []

# Chunk code snippets from the given code_dir
for filename in os.listdir(code_dir):
    if '.tf' in filename:
        with open(os.path.join(code_dir, filename), 'r') as f:
            dat = f.read()
        if dat!='':
            # Chunk and save code chunks with filename
            chunks = []
            i = 0
            while i<len(dat):
                tf_file_names.append(filename)
                tf_file_code.append(dat[i:i+chunk_size])
                i += chunk_size - overlap

# Embed code snippets
tf_file_code_embed = [embed for embed in vo.embed(tf_file_code, model="voyage-code-3", input_type="document").embeddings]


# Store code snippets, vector embeddings and source filenames
store = list(zip(tf_file_code_embed, tf_file_names, tf_file_code)) 

if not os.path.isdir(storage_dir):
    os.mkdir(storage_dir)

with open(os.path.join(storage_dir, store_save_file), 'wb') as f:
    pickle.dump(store, f)
