from email.utils import quote
import json
import openai 
import os
import datetime

import os.path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.pprint_utils import pprint_response, pprint, pprint_metadata, pprint_source_node

from llama_index.core import TreeIndex
from llama_index.core.retrievers import TreeRootRetriever

import time

import pandas as pd


from dotenv import load_dotenv
from openai import OpenAI

import glob

import PyPDF2

from urllib.parse import quote



load_dotenv()  # loads variables from .env into environment
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set!"
client = OpenAI()

# DATA_FOLDER = './Current Cybersecurity Law/'
DATA_FOLDER = './static/legislations/Current Cybersecurity Law/'
PERSIST_DIR = './Vector_Storage_Context/'

def safe_url(raw):
    safe_url = raw[raw.find('Current'):]  # get substring starting from 'Current'
    safe_url = safe_url.replace("\\", "/")  # replace backslashes with forward slashes FIRST
    safe_url = quote(safe_url, safe="/:")  # encode spaces, parentheses, etc., but keep slashes
    safe_url = safe_url.replace("(", "%28").replace(")", "%29")
    safe_url = '/static/legislations/' + safe_url  # append /static/legislations at the end
    return safe_url

# Open the PDF file in binary mode
def read_pdf(file):
    with open(file, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)

        # Get the total number of pages in the PDF
        num_pages = len(pdf_reader.pages)

        pdf_text = ""

        # Iterate through each page and extract text
        for page_number in range(num_pages):
            # Get a specific page
            page = pdf_reader.pages[page_number]

            # Extract text from the page
            text = page.extract_text()
            pdf_text += text

    return pdf_text


def get_pdfs(root_folder):
    pdf_files = []
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.pdf'):
                pdf_files.append(os.path.join(foldername, filename))
    return pdf_files

def get_required_states(query):
    prompt = f'''Suppose I have legislation documents on all the states of United States, along with federal and intenational level.\n
                Based on the folllowing query, which state documents should I look into?\n

                If the query says compare between state X and Y, you should mention both state X and Y.
                If the query says compare between state X and all other state with a condition,
                you should mention state X and all other state that satisfies the condition.
                If the query does not mention any state, you should mention all the states that are in the U.S.
                Think multiple time and do not miss out any state names.

                Give me the state names in comma seperated line.
                For example: Texas,Alabama,New York
                Do not add any additional explanation. Only the state names in python list format.
                
                -------------------------------------------------------------
                query:
                {query} 
                -------------------------------------------------------------
                '''
        
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages= [
        {
            "role":"system",
            "content":'''You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations.
            You have a good knowledge about the states of the united states. Their geological position, political relationships, etc.'''
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )

    return gpt_response.choices[0].message.content

def create_state_query_engine(state_name):
    print(f'Loading Index of {state_name}')
    #  -- change these lines while using in the interface --
    STATE_DATA_FOLDER = DATA_FOLDER + state_name + '/'
    STATE_PERSIST_DIR = PERSIST_DIR + state_name + '/'
    
    index = None

    if not os.path.exists(STATE_PERSIST_DIR):
        # creating the index from the documents
        print('Creating index of:',state_name)
        os.mkdir(STATE_PERSIST_DIR)

        pdf_files = get_pdfs(STATE_DATA_FOLDER)
        documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
        index = VectorStoreIndex.from_documents(documents=documents)

        # store it for later
        index.storage_context.persist(persist_dir=STATE_PERSIST_DIR)
    else:
        # retrieving a storage context from already exixting contex and loading the index
        storage_contex = StorageContext.from_defaults(persist_dir=STATE_PERSIST_DIR)
        index = load_index_from_storage(storage_context=storage_contex)


    retriever = VectorIndexRetriever(index=index, similarity_top_k=20)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.50)

    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])
    return query_engine


def get_states(data_folder):
  dirs = os.listdir(data_folder)
  return dirs

def create_query_engines(states = None):
  if states is None:
    states = get_states(DATA_FOLDER)
  query_engines = {}

  for i,state in enumerate(states):
    query_engines[state] = create_state_query_engine(state)

    # if i ==5:
    #     break
    # break  # remove this break to load all states
  
  return query_engines

import tiktoken

def count_tokens(text):
    
    # Initialize the encoder for the specific model
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Encode the prompt to get the token count
    tokenized_prompt = encoder.encode(text)
    token_count = len(tokenized_prompt)
    return token_count
    


def get_state_wise_response(state,question,top_k=10, model = "gpt-4o-mini"):
    prompt = question
    query_engine = state_wise_query_engines[state]
    response = query_engine.query(question)

    context_1 = ""
    context_2 = ""
    refs = []
    i = 0
    l = []
    for node in response.source_nodes:        
        # context += f"Context {i+1}: \n\n"
        refs.append(node.metadata['file_path'])
        text = ""
        text += f"File name: {node.metadata['file_path']}"
        file_text = read_pdf(node.metadata['file_path'])
        leg_code = file_text.split('\n')[0]
        text += "Legislation code:" + leg_code + '\n'
        text += file_text

        token_count = count_tokens(context_1) + count_tokens(text) + count_tokens(question) + 450 + 1500
        if token_count >= 16000 :
            break

        if 'insurance' in node.metadata['file_path'].lower():
            context_2 += f"Context {i+1}: \n\n"
            context_2 += text
        else:
            context_1 += f"Context {i+1}: \n\n"
            context_1 += text

        i += 1
        if i == top_k:
            break
        

    prompt = f'''You have the following contexts and a Question. 
                Based on the information in the context, answer the question.\n
                -------------------------------------------------------------
                Contexts:
                {context_1}
                -------------------------------------------------------------
                Question: 
                {question}
                -------------------------------------------------------------
                Based on these contexts, answer the question. Try to use exact word from the context.
                Answer as precisely as possible using the words from the context. Try to use all the information fom the context. 
                While answering, mention the legislation code first.
                Try to preserve the paragrapg numberings also.
                Do not add any informatio which is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                
                If I give you any context please mention the file name from where you are taking your information 
                at the end of your response as "References". Mention exact file paths as numbered list in seperate lines.
                No need to mention the sources with the paragraphs. Just mention them at the end.

                No need to mention refrence while aswering to greetings questions like Hi or Hello.

                Here is a example of a response. Follow this response formate strictly:
                According to Code of Ala. § 8-27-2:
                A “trade secret” is information that:
                a. Is used or intended for use in a trade or business;
                b. Is included or embodied in a formula, pattern, compilation, computer software,
                drawing, device, method, technique, or process;
                c. Is not publicly known and is not generally known in the trade or business of the person
                asserting that it is a trade secret;
                d. Cannot be readily ascertained or derived from publicly available information;
                e. Is the subject of efforts that are reasonable under the circumstances to maintain its
                secrecy; and
                f. Has significant economic value.

                Reference:
                1) [file path]
                '''
    # Question:  What are the identidying document accordint to Alabama Legislations?
    # Response:
        
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ],
    max_tokens=1500,
    )

    ret_1 = str(gpt_response.choices[0].message.content).replace("\n",'<br>')

    prompt = f'''You have the following contexts and a Question. 
                Based on the information in the context, answer the question.\n
                -------------------------------------------------------------
                Contexts:
                {context_2}
                -------------------------------------------------------------
                Question: 
                {question}
                -------------------------------------------------------------
                Based on these contexts, answer the question. Try to use exact word from the context.
                Answer as precisely as possible using the words from the context. Try to use all the information fom the context. 
                While answering, mention the legislation code first.
                Try to preserve the paragrapg numberings also.
                Do not add any informatio which is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                If you do not have any answer, just give an empty response.
                
                If I give you any context please mention the file name from where you are taking your information 
                at the end of your response as "References". Mention exact file paths as numbered list in seperate lines.
                No need to mention the sources with the paragraphs. Just mention them at the end.

                No need to mention refrence while aswering to greetings questions like Hi or Hello.

                Here is a example of a response. Follow this response formate strictly:
                According to Code of Ala. § 8-27-2:
                A “trade secret” is information that:
                a. Is used or intended for use in a trade or business;
                b. Is included or embodied in a formula, pattern, compilation, computer software,
                drawing, device, method, technique, or process;
                c. Is not publicly known and is not generally known in the trade or business of the person
                asserting that it is a trade secret;
                d. Cannot be readily ascertained or derived from publicly available information;
                e. Is the subject of efforts that are reasonable under the circumstances to maintain its
                secrecy; and
                f. Has significant economic value.

                Reference:
                1) Current Cybersecurity Law\Florida\Information Technology\Fla. Stat. _ 282.318.pdf
                '''
    # Question:  What are the identidying document accordint to Alabama Legislations?
    # Response:
        
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ],
    max_tokens=1500,
    )

    ret_2 = str(gpt_response.choices[0].message.content).replace("\n",'<br>')

    modified_ret = ""

    if len(ret_2)>0:
        modified_ret = ret_1 + "\n\nInformation based on insurance documents:\n" + ret_2
    else:
        modified_ret = ret_1 

    for ref in refs:
        if ref in ret_1 + ret_2:
            modified_ref = modify_ref(ref)
            modified_ret = modified_ret.replace(ref,modified_ref)
    return modified_ret


def modify_ref(ref):
    pos = ref.find('Current')
    rel_path = ref[pos:]
    html = '<a href= "static/'+str(rel_path)+'" target="_blank">'+ rel_path +'</a>'
    return html

def get_state_wise_response_updated(state,question,top_k=10, model = "gpt-4o-mini"):
    prompt = question
    query_engine = state_wise_query_engines[state]
    response = query_engine.query(question)

    context_1 = ""
    context_2 = ""
    refs = []
    i = 0
    l = []
    print("Number of node:",len(response.source_nodes))
    for node in response.source_nodes:   
             
        # context += f"Context {i+1}: \n\n"
        file_path = node.metadata['file_path'][node.metadata['file_path'].find('Current'):]
        refs.append(file_path)
        text = ""
        text += f"File Path: {file_path}"
        file_text = read_pdf('static/legislations/' + file_path)
        leg_code = file_text.split('\n')[0]
        text += "Legislation code:" + leg_code + '\n'
        text += "File text:" + file_text

        # print(node.metadata['file_path'])
        # print('-------------------')
        # print(file_text[:500])

        token_count = count_tokens(context_1) + count_tokens(text) + count_tokens(question) + 450 + 1500
        if token_count >= 16000 :
            break

        if 'insurance' in node.metadata['file_path'].lower():
            context_2 += f"Context {i+1}: \n\n"
            context_2 += text
        else:
            context_1 += f"Context {i+1}: \n\n"
            context_1 += text

        i += 1
        if i == top_k:
            break
        
    # print("Context:", context_1)
    prompt = f'''You have the following contexts and a Question. 
                Based on the information in the context, answer the question.\n
                -------------------------------------------------------------
                Contexts:
                {context_1}
                -------------------------------------------------------------
                Question: 
                {question}
                -------------------------------------------------------------
                Based on these contexts, answer the question. Strictly use exact word from the context.
                Answer as precisely as possible using the words from the context. Try to use all the relevant information from the context. 
                While answering, mention the legislation code first.
                Try to preserve the paragrapg numberings also. If ordered list is present in the context, try to preserve that also and make them appear in new lines.
                Do not add any information which is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                Prepare the answer in a markdown format.
                
                Your answer should be in a valid JSON format with two keys: "answer" and "references". Becareful about making the JSON valid.
                The "answer" key should contain the answer to the question based on the provided contexts.
                The "references" key should contain a list of file paths from which the information was taken.
                Example:
                {{ \"answer\": 
                \"According to Code of Ala. § 8-27-2:
                A “trade secret” is information that:
                a. Is used or intended for use in a trade or business;
                b. Is included or embodied in a formula, pattern, compilation, computer software,
                drawing, device, method, technique, or process;
                c. Is not publicly known and is not generally known in the trade or business of the person
                asserting that it is a trade secret;
                d. Cannot be readily ascertained or derived from publicly available information;
                e. Is the subject of efforts that are reasonable under the circumstances to maintain its
                secrecy; and
                f. Has significant economic value.\"
                , \"references\": [
                    \"file_path_1\",
                    \"file_path_2\"
                ]
                }}
                '''
    # Question:  What are the identidying document accordint to Alabama Legislations?
    # Response:
        
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    response_format={"type":"json_object"},
    messages= [
        {
            "role":"system",
            "content":"""You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. 
            Your role is to help with Transportation Cybersecurity Legislations. Follow the instructions and the examples strictly"""
        },
        {
            "role":"user",
            "content":prompt
        }
    ],
    max_tokens=1500,
    )

    res_1 = str(gpt_response.choices[0].message.content.strip())
    json_data = json.loads(res_1)

    # print(json_data['answer'])

    final_response_1 = ""

    final_response_1 += json_data['answer'].replace('\n','<br>') + '\n\nReferences:\n\n'

    for i,reference in enumerate(set(json_data['references']), start = 1):
        final_response_1 += f"[{i}] [{reference[reference.find('Current'):]}]({safe_url(reference)})\n\n"

    if len(context_2) == 0:
        return final_response_1


    prompt = f'''You have the following contexts and a Question. 
                Based on the information in the context, answer the question.\n
                -------------------------------------------------------------
                Contexts:
                {context_2}
                -------------------------------------------------------------
                Question: 
                {question}
                -------------------------------------------------------------
                Based on these contexts, answer the question. Strictly use exact word from the context.
                Answer as precisely as possible using the words from the context. Try to use all the relevant information from the context. 
                While answering, mention the legislation code first.
                Try to preserve the paragrapg numberings also. if ordered list is present in the context, try to preserve that also and make them appear in new lines.
                Do not add any information which is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                
                Your answer should be in a valid JSON format with two keys: "answer" and "references". Becareful about making the JSON valid.
                The "answer" key should contain the answer to the question based on the provided contexts.
                The "references" key should contain a list of file paths from which the information was taken.
                Example:
                {{ \"answer\": 
                \"According to Code of Ala. § 8-27-2:
                A “trade secret” is information that:
                a. Is used or intended for use in a trade or business;
                b. Is included or embodied in a formula, pattern, compilation, computer software,
                drawing, device, method, technique, or process;
                c. Is not publicly known and is not generally known in the trade or business of the person
                asserting that it is a trade secret;
                d. Cannot be readily ascertained or derived from publicly available information;
                e. Is the subject of efforts that are reasonable under the circumstances to maintain its
                secrecy; and
                f. Has significant economic value.\"
                , \"references\": [
                    \"file_path_1\",
                    \"file_path_2\"
                ]
                }}
                '''
    # Question:  What are the identidying document accordint to Alabama Legislations?
    # Response:
        
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    response_format={"type": "json_object"},
    messages= [
        {
            "role":"system",
            "content":"""You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. 
            Your role is to help with Transportation Cybersecurity Legislations. Follow the instructions and the examples strictly"""
        },
        {
            "role":"user",
            "content":prompt
        }
    ],
    max_tokens=1500,
    )

    res_2 = str(gpt_response.choices[0].message.content.strip())
    json_data = json.loads(res_2)

    # print(json_data['answer'])

    final_response_2 = ""

    final_response_2 += json_data['answer'] + '\n\nReferences:\n\n'

    for i,reference in enumerate(set(json_data['references']), start = 1):
        final_response_2 += f"[{i}] [{reference[reference.find("Current"):]}]({safe_url(reference)})\n\n"

    # modified_ret = ""

    if len(final_response_2)>0:
        final_response = final_response_1 + "\n\n**Information based on insurance documents:**\n\n" + final_response_2
    else:
        final_response = final_response_1 
    
    return final_response

    
    # return modified_ret


def get_accumulated_response(context, question, model="gpt-4o-mini"):
    # print('--- Accumulating Response ----')
        
    prompt = f'''you have the following contexts.\n
                -------------------------------------------------------------
                context:
                {context}
                -------------------------------------------------------------
                Accumulate the information from the contexts to answer the following question.
                Only use the information present in the context to answer the question.
                Do not use any information that is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                Query: {question}

                No need to mention refrence while aswering to greetings questions like Hi or Hello.'''
    
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )
    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
    return ret

def fact_checking(question, response, model = "gpt-4o-mini"):
    prompt = f'''To answer a question about transportation legislation around different states of United States,
                I have the following information about a particilar state. I am considering informations from different states to accumulate/compare them at the end to have a comprehensive answer.

                Based on the question given below, check if the information given following is useful information or not. 
                Response "Yes" if and only if the information is useful, otherwise respond "No".
                -------------------------------------------------------------
                Question: {question}
                -------------------------------------------------------------
                Information: {response}
                -------------------------------------------------------------
                '''
    
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )


    ret = str(gpt_response.choices[0].message.content)
    return ret

def get_summary(question,response, model = "gpt-4o-mini"):
    
    prompt = f'''To answer the following question, summarise the given response.\n
                -------------------------------------------------------------
                Question: {question}
                -------------------------------------------------------------
                Response: {response}
                -------------------------------------------------------------
                '''
    
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )


    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
    return ret



def get_response(query, only_accumulated_response = False, model = "gpt-4o-mini"):
    required_states_set = set(get_required_states(query).split(','))

    required_states = []
    for state in required_states_set:
        required_states.append(state.strip())
    
    if "" in required_states:
        required_states.remove("")
    
    response = ""
    # response += "Looking into the following states: <br>"
    # ind = 1
    # for state in required_states:
    #     response += str(ind) + '. ' + state + '<br>'
    #     ind+=1

    context = ''
    # response += '<br>Responses based on different states:<br>'
    state_wise_responses = {}
    for state in required_states:
        
        if state in state_wise_query_engines:
            # print(f"---------- Getting response for: {state} ---------------")
            state_wise_response = get_state_wise_response(state, query, model)
            fact_check = fact_checking(query, state_wise_response, model)

            if fact_check == "No":
                # print("Skipped!")
                response += state + ':<br>'
                response += f'No documents found on this state.' +'<br>'
                continue

            context += state_wise_response + '\n'
            response += state + ': <br>'
            response += state_wise_response +'<br>'
            # for summarization
            state_wise_responses[state] = state_wise_response
            # print("Included.")
        else:
            print(f'{state} is not present ------------------------------')
            response += state + ':<br>'
            response += f'No documents found based on {state}.' +'<br>'

    accumulated_response = ""   
    if len(required_states)>1:
        try:
            accumulated_response = get_accumulated_response(context, query,model)
        except Exception as e:
            print("Maximum limit of context exceeded! Generating Summaries!")
            response = "Looking into the following states: <br>"
            ind = 1
            for state in required_states:
                response += str(ind) + '. ' + state + '<br>'
                ind+=1

            context = ''


            for state in required_states:
                # response += state + ':<br>'
                if state in state_wise_query_engines:
                    print(f"---------- Getting summary for: {state} ---------------")
                    context += get_summary(query, state_wise_response,model) + '\n'
                    response += state_wise_response +'<br>'
                else:
                    print(f'{state} is not present ------------------------------')
                    response += f'No documents found based on {state}.' +'<br>'
            
            accumulated_response = get_accumulated_response(context, query, model)

        # response += '<br>' + accumulated_response + '<br>'

    if only_accumulated_response == True:
        if len(required_states)>1:
            return accumulated_response
        else:
            return response
    else:
        if len(required_states)>1:
            return response + '<br>' + accumulated_response + '<br>'
        else:
            return response
        
state_wise_query_engines = create_query_engines()

def check_query(question, model = "gpt-4o-mini"):
    
    prompt = f'''Check the user message if the user is asking a question related to laws and legislations.\n
                If yes, respond "Yes". 
                Otherwise, say 'No'.
                User message: {question}
                '''
    
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR-Legal-AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )


    ret = str(gpt_response.choices[0].message.content)
    return ret

def get_general_response(question, model = "gpt-4o-mini"):
    
    prompt = f'''Respond to the user message generally like a chatbot.
                User message: {question}
                '''
    
    gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model=model,
    messages= [
        {
            "role":"system",
            "content":"You are a helpful assisstant. Your name is TraCR-Legal-AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    )


    ret = str(gpt_response.choices[0].message.content)
    return ret

def get_response_streamed(query, only_accumulated_response = False, model = "gpt-4o-mini"):
    # check if the query is related to legislations
    check = check_query(query, model)
    if check[:3].strip().lower() != "yes":
        yield get_general_response(query, model)
        return
    
    # get the required states
    required_states_set = set(get_required_states(query).split(','))

    required_states = []
    for state in required_states_set:
        required_states.append(state.strip())
    
    if "" in required_states:
        required_states.remove("")
    
    all_states_flag = False
    # declare required states
    if len(required_states) == 50:
        all_states_flag = True
        yield "## Looking into documents from all the states of United States.\n"
    else:
        declaire_required_states = "## Looking into documents from the following states:\n"
        for i, state in enumerate(required_states, start=1):
            declaire_required_states += f"{i}. {state}\n"
        yield declaire_required_states
    
    yield "\n---\n\n"
    response = ""

    context = ''
    # response += '<br>Responses based on different states:<br>'
    yield '\n## According to the documents from the different states:\n'
    state_wise_responses = {}
    for i, state in enumerate(required_states, start=1):
        yield f'### {i}. {state}:\n'
        
        if state in state_wise_query_engines:
            # print(f"---------- Getting response for: {state} ---------------")
            try:
                state_wise_response = get_state_wise_response_updated(state, query, model)
            except Exception as e:
                yield f"Error occured while getting response from {state}. Skipping...\n"
                print(f"Error occured while getting response from {state}. Skipping...\n")
                print(e)
                continue
            fact_check = fact_checking(query, state_wise_response, model)

            if fact_check == "No":
                # print("Skipped!")
                response += state + ':\n'
                response += f'No relevant documents were found for this state.' +'\n'
                yield f'No relevant documents were found for this state.\n'

                context += f'{state}:\n'
                context += "No relevant documents were found for this state." + '\n'
                state_wise_responses[state] = "No relevant documents were found for this state."

                continue
            
            context += f'{state}:\n'
            context += state_wise_response + '\n'
            response += state + ':\n'
            response += state_wise_response +'\n'
            # for summarization
            state_wise_responses[state] = state_wise_response
            yield state_wise_response +'\n'
            yield '\n---\n\n'
            # print("Included.")
        else:
            print(f'{state} is not present ------------------------------')
            response += f'No relevant documents were found for the state of {state}.' +'\n'
            yield f'No relevant documents were found for the state of {state}.\n'

    # return 
    accumulated_response = ""   
    if len(required_states)>1:
        try:
            accumulated_response = get_accumulated_response(context, query,model)
        except Exception as e:
            print("Maximum limit of context exceeded! Generating Summaries!")

            full_response = ''
            for state in required_states:
                if state in state_wise_query_engines:
                    print(f"---------- Getting summary for: {state} ---------------")
                    full_response += state + ':\n'
                    full_response += state_wise_responses[state] + '\n'

            accumulated_response = get_accumulated_response(full_response, query, model)

        # response += '<br>' + accumulated_response + '<br>'

    if len(required_states)>1:
        yield "\n\n## In conclusion, based on the documents from different states:\n\n"
        yield accumulated_response
        # return accumulated_response


if __name__ == '__main__':
    query = "What are the identifying documents according to Alabama Legislations?"
    # response = get_response(query=query, only_accumulated_response=False, model="gpt-4o-mini")
    response = get_state_wise_response_updated(state="Alabama", question=query, top_k=10, model="gpt-4o-mini")
    print(response)