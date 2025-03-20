# Terraform Code Generator
This repository contains code to auto-generate new Terraform Code that modifies an existing codoe base using an LLM and RAG-pipeline. 

As a default functionality, scripts search for a VPC module within a given terraform code directory update existing files by adding security configurations.


### Requirements

```
pip install anthropic
pip install numpy
pip install voyageai
```
### Usage

First run ```git clone https://github.com/terraform-aws-modules/terraform-aws-vpc.git``` to fetch the target terraform code repository.

Then Run:
* ```python build_vdb.py``` to build a small vector-store for all code in the specified code-repository (this may take a little time).
* ```python main.py``` to modify the existing code by adding security configurations to the VPC

The Default configuration modifies code for ```terraform-aws-vpc/examples/block-public-access```

Output files are written to the ```outputs``` directory along with descriptions of modifications made.

### You can cusom configure:
- API Keys in ```config/api_keys.json```.
- Target Code Directory, File Paths and chunking sizes for RAG in ```config/general_config.json```.
- Prompts by modifying files in the ```prompts``` directory.

### Code Structure
-  ```build_vdb.py``` chunks overlapping code snippets from each file in the provided code directory and embeds each code chunk as a vector using a voyageai embedding model. This vector-store is saved to a ```storage``` directory for future use
- A ```retriever``` module retrieves filenames from the store that contain code snippets matching a given query (RAG)
- The retrieved code is passed to an LLM along with system instructions and user instructions that instruct the LLM to modify code for each retrieved file and provide a description of its changes.
- Modified code and changes are saved to outputs.
