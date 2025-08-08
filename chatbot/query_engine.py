import os.path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.pprint_utils import pprint_response, pprint, pprint_metadata, pprint_source_node
from TraCR.settings import BASE_DIR
import openai

from dotenv import load_dotenv

# Create your views here.
load_dotenv()  # loads variables from .env into environment
openai_api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = openai_api_key
client = openai.OpenAI()


data_folder = BASE_DIR / 'Current Cybersecurity Law/'
PERSIST_DIR = BASE_DIR / f'Vector_Storage_Context/'

import glob

def get_pdfs(root_folder):
    pdf_files = []
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.pdf'):
                pdf_files.append(os.path.join(foldername, filename))
    return pdf_files

def get_query_engine():
    print('Getting query engine')
    if not os.path.exists(PERSIST_DIR):
        print('Creating indexes for query engine')

        # creating the index from the documents
        os.mkdir(PERSIST_DIR)

        pdf_files = get_pdfs(data_folder)
        documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
        index = VectorStoreIndex.from_documents(documents=documents)

        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print('Loading indexes for query engine')

        # retrieving a storage context from already exixting contex and loading the index
        storage_contex = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context=storage_contex)


    retriever = VectorIndexRetriever(index=index, similarity_top_k=2)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.80)

    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])
    print('Query engine created')

    return query_engine

query_engine = get_query_engine()