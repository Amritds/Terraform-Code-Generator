import os
import json
import anthropic
from retriever import FileRetriever


# Set api keys
with open('config/api_keys.json','r') as f:
    api_keys = json.load(f)
    os.environ["ANTHROPIC_API_KEY"] = api_keys["ANTHROPIC_API_KEY"]

# Set code directory, store load and output file paths
with open('config/general_config.json', 'r') as f:
    config = json.load(f)
    store_load_file = os.path.join(config["storage_dir"], config["store_save_file"])
    code_dir = config["code_dir"]
    output_dir = config["output_dir"]

# Initialize the LLM 
client = anthropic.Anthropic()

# Get the retrival query
with open('prompts/retrieval_query_template.txt', 'r') as f:
    retrieval_query = f.read()

def create_output_directories():
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(os.path.join(output_dir, 'modified_code')):
        os.mkdir(os.path.join(output_dir, 'modified_code'))
    if not os.path.isdir(os.path.join(output_dir, 'modification_descriptions')):
        os.mkdir(os.path.join(output_dir, 'modification_descriptions'))

# Load the retriever
ret = FileRetriever(store_load_file, threshold_retrival=0.65)

# Retrieve relevant file names
relevant_files = ret.retrieve_files_from_query(retrieval_query)

# Create a context of relevant file code
system_context = ''
for filename in relevant_files:
    # Get the Code File
    with open(os.path.join(code_dir, filename), 'r') as f:
        dat = f.read()
    
    # Get the system prompt and add the code file content
    with open("prompts/system_context_template.txt", 'r') as f:
        system_context += f.read().replace('<filename>', filename)
    system_context += dat +'\n\n'

# Create a user query for each file to be modified
messages_so_far = []
for filename in relevant_files:
    filepath_filename = os.path.join(code_dir, filename)
    print('Trying to Modify ', filepath_filename, '...')

    # Get the user instructions prompt
    with open("prompts/user_instructions_template.txt", 'r') as f:
        user_instructions = f.read().replace('<filename>', filename)

    messages_so_far.append({"role": "user", "content": user_instructions})

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4048,
        system = system_context,
        messages=messages_so_far)
    
    # Remember history for consistency in code modification
    messages_so_far.append({"role": "assistant", "content": response.content[0].text})
   
    try:
        # Split code changes and descriptioon
        modified_code, modification_descriptions = response.content[0].text.split('<--SEP-->')
        modified_code = modified_code.replace('`','')
        # Create Missing Output Directories
        create_output_directories()
        
        # Save modified code to outputs
        with open(os.path.join(output_dir, 'modified_code', filename), 'w') as f:
            f.write(modified_code)
        
        # Save modification descriptions to outputs
        with open(os.path.join(output_dir, 'modification_descriptions', filename.replace('.tf', '.txt')), 'w') as f:
            f.write(modification_descriptions)

        print('Modifications Made To ', filepath_filename)

    except:
        # Either no code modifications made or some other failure
        print('No Changes Made To ', filepath_filename)
        continue
print('Done...Code File Changes and Descriptions Saved to Outputs.')