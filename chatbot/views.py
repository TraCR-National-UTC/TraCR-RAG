from django.shortcuts import render, redirect
from django.http import JsonResponse
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
from TraCR.settings import BASE_DIR

from llama_index.core import TreeIndex
from llama_index.core.retrievers import TreeRootRetriever

import time

import pandas as pd

import tiktoken

from dotenv import load_dotenv


# Create your views here.

load_dotenv()  # loads variables from .env into environment
openai_api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = openai_api_key
client = openai.OpenAI()


data_folder = BASE_DIR / 'Current Cybersecurity Law/'
PERSIST_DIR = BASE_DIR / 'Vector_Storage_Context/'

import glob

import PyPDF2

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

            # Print the text
            # print("Page", page_number + 1)
            # print(text)
    return pdf_text


def get_pdfs(root_folder):
    pdf_files = []
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.pdf'):
                pdf_files.append(os.path.join(foldername, filename))
    return pdf_files

def get_required_states(query):
    prompt = f'''Suppose I have legislation documents on all the states of United States.\n
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

    print(gpt_response.choices[0].message.content)
    return gpt_response.choices[0].message.content

def create_state_wise_index(state_name):
    print(f'Loading Index of {state_name}')
    data_folder = BASE_DIR / f'Current Cybersecurity Law/{state_name}/'
    PERSIST_DIR = BASE_DIR / f'Vector_Storage_Context/{state_name}/'
    
    index = None

    if not os.path.exists(PERSIST_DIR):
        # creating the index from the documents
        print('Creating index of:',state_name)
        os.mkdir(PERSIST_DIR)

        pdf_files = get_pdfs(data_folder)
        documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
        index = VectorStoreIndex.from_documents(documents=documents)

        # store it for later
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        # retrieving a storage context from already exixting contex and loading the index
        storage_contex = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context=storage_contex)


    retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.80)

    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])
    return query_engine

def get_states(data_folder):
  dirs = os.listdir(data_folder)
  return dirs

def create_indices(states = None):
  if states is None:
    states = get_states(data_folder)
  indices = {}

  for state in states:
    indices[state] = create_state_wise_index(state)
  
  return indices

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


    retriever = VectorIndexRetriever(index=index, similarity_top_k=20)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.80)

    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])
    print('Query engine created')

    return query_engine


query_engine = get_query_engine()
state_wise_query_engines = create_indices()


def count_tokens(text):
    
    # Initialize the encoder for the specific model
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Encode the prompt to get the token count
    tokenized_prompt = encoder.encode(text)
    token_count = len(tokenized_prompt)
    return token_count

# def get_state_wise_response(state,question):
#     prompt = question
#     query_engine = state_wise_query_engines[state]
#     response = query_engine.query(question)

#     file_text = ""
#     # if len(response.source_nodes) != 0:
#     #     text = read_pdf(response.source_nodes[0].metadata['file_path'])

#     context = ""
#     sources = ""
#     refs = []
#     i = 0
#     l = []
#     for node in response.source_nodes:
        
#         # if len(context) + len(node.text) + len(question)+ 2300 >= 16385:
#         #     break
#         context += f"Context {i+1}: \n\n" + node.text
#         sources += node.metadata['file_path'] + '<br>'
#         refs.append(node.metadata['file_path'])
#         text = ""
#         text += f"from the file {node.metadata['file_path']}"
#         text += read_pdf(response.source_nodes[0].metadata['file_path'])

#         length = len(context) + len(node.text) + len(question)+ 2300
#         print(i,":",length)
#         if len(file_text) + len(text) + 2200 >= 60000:
#             break

#         file_text += text 
#         i += 1
#         if i==6:
#             break
        

#     prompt = f'''you have the following contexts.\n
#                 -------------------------------------------------------------
#                 context:
#                 {file_text}
#                 -------------------------------------------------------------
#                 sources:
#                 {sources}
#                 -------------------------------------------------------------
#                 Based on these contexts, answer the following query. Try to use exact word from the context.
#                 Try to use all the information fom the context. Try to preserve the paragrapg numberings also.
#                 Do not add any informatio which is not present in the context.
#                 Remove the word "Trayce Hockstad" from your response.
#                 Query: {question}
                
#                 If I give you any context please mention the file name from where you are taking your information 
#                 at the end of your response as "References". Mention exact file paths as numbered list in seperate lines. 
#                 No need to mention the sources with the paragraphs. Just mention them at the end.

                
                
#                 No need to mention refrence while aswering to greetings questions like Hi or Hello.'''

#     print(len(prompt))
    
    
#     gpt_response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages= [
#         {
#             "role":"system",
#             "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
#         },
#         {
#             "role":"user",
#             "content":prompt
#         }
#     ]
#     )

#     print(gpt_response.choices[0].message.content)

#     ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
#     modified_ret = ret

#     for ref in refs:
#         if ref in ret:
#             modified_ref = modify_ref(ref)
#             print(ref,'\n',modified_ref)
#             modified_ret = modified_ret.replace(ref,modified_ref)

#     # if sources != "":
#     #     ret+=  '<br><br>Source:<br>' + sources
#     print(modified_ret)
#     rel_path = "Current Cybersecurity Law\Connecticut\Criminal code\Conn. Gen. Stat. _ 53a-251.pdf"
#     return modified_ret #+ '<br>'+'{% load static %}' + '<a href= "{% static \''+ rel_path +'\' %}" target="_blank">'+ rel_path +'</a>'

    # return str(response) + '<br><br>Source:<br>' + sources

file = open('log.txt','a')
def get_context(question,state,context):
    file = open(f'{question[:10]}.txt','a')
    file.write(state+'\n')
    file.write(context+'\n')
    file.close()


def get_state_wise_response(state,question,top_k=10):
    prompt = question
    query_engine = state_wise_query_engines[state]
    response = query_engine.query(question)

    context = ""
    refs = []
    i = 0
    l = []
    for node in response.source_nodes:        
        context += f"Context {i+1}: \n\n"
        refs.append(node.metadata['file_path'])
        text = ""
        text += f"File name: {node.metadata['file_path']}"
        file_text = read_pdf(response.source_nodes[0].metadata['file_path'])
        leg_code = file_text.split('\n')[0]
        text += "Legislation code:" + leg_code + '\n'
        text += file_text + '\n'

        token_count = count_tokens(context) + count_tokens(text) + count_tokens(question) + 450 + 1500
        if token_count >= 16385 :
            break

        context += text 
        i += 1
        if i == top_k:
            break
    
    # this code writes the context in a different file
    get_context(question, state, context)
    return ''

    prompt = f'''You have the following contexts and a Question. 
                Based on the information in the context, answer the question.\n
                -------------------------------------------------------------
                Contexts:
                {context}
                -------------------------------------------------------------
                Question: 
                {question}
                -------------------------------------------------------------
                Based on these contexts, answer the question. Use exact words and formats from the context by EXTRACTING the information, not generating it.
                Do not exclude any numberings from the context from your extracted information.
                Answer as precisely as possible using the words from the context. Try to use all the information fom the context. 
                While answering, mention the legislation code first.
                Try to preserve the paragrapg numberings also.
                Do not add any information which is not present in the context.
                Remove the word "Trayce Hockstad" from your response.
                
                
                If I give you any context please mention the file name from where you are taking your information 
                at the end of your response as "References". Mention exact file paths as numbered list in seperate lines.
                No need to mention the sources with the paragraphs. Just mention them at the end.

                No need to mention refrence while aswering to greetings questions like "Hi" or "Hello".

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
                1) C:\\Users\\User\\Box\\UTD\\PhD Research\\RAG-app\\Current Cybersecurity Law\\Minnesota\\Information Technology\\Minn. Stat. _ 16E.03.pdf
                '''
    print("Getting Statewise response. ##")
    file.write("Getting Statewise response. ##\n")
    print("Prompt:")
    file.write("Prompt:\n")
    print(prompt)
    file.write(prompt+'\n')
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
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
    print("Response:")
    print(gpt_response.choices[0].message.content)
    file.write('Response:\n')
    file.write(gpt_response.choices[0].message.content+'\n')

    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
    modified_ret = ret

    for ref in refs:
        if ref in ret:
            modified_ref = modify_ref(ref)
            # print("Printing References:")
            # print(ref,'\n',modified_ref)
            modified_ret = modified_ret.replace(ref,modified_ref)

    # if sources != "":
    #     ret+=  '<br><br>Source:<br>' + sources
    # print(modified_ret)
    # rel_path = "Current Cybersecurity Law\Connecticut\Criminal code\Conn. Gen. Stat. _ 53a-251.pdf"
    return modified_ret #+ '<br>'+'{% load static %}' + '<a href= "{% static \''+ rel_path +'\' %}" target="_blank">'+ rel_path +'</a>'

    # return str(response) + '<br><br>Source:<br>' + sources

def modify_ref(ref):
    pos = ref.find('Current')
    rel_path = ref[pos:]
    # html = '<a href=[ static "'+rel_path+'" ] target="_blank">'+ rel_path +'</a>'
    # html += html.replace('[','"{%')
    # html += html.replace(']','%}"')
    # html = '<a href=\'https:://'+ref+'\' target="_blank">'+ rel_path +'</a>'
    html = '<a href= "static/'+str(rel_path)+'" target="_blank">'+ rel_path +'</a>'
    # <a href="{% static 'Current Cybersecurity Law/Connecticut/Criminal code/Conn. Gen. Stat. _ 53a-251.pdf' %}" target="_blank">Wiki</a>
    
    #"C:\Users\User\Box\UTD\PhD Research\RAG-app\Current Cybersecurity Law\Connecticut"
    # print("printing link\n")
    # print(html)
    return html

def get_accumulated_response(context, question):
    return ''
    print('--- Accumulating Response ----')
    file.write('--- Accumulating Response ----\n')
        
    prompt = f'''you have the following contexts.\n
                -------------------------------------------------------------
                context:
                {context}
                -------------------------------------------------------------
                Based on these contexts, answer the following query. Try to use exact word from the context.
                Try to use all the information fom the context. Try to preserve the paragrapg numberings also.
                Remove the word "Trayce Hockstad" from your response.
                Query: {question}

                No need to mention refrence while aswering to greetings questions like Hi or Hello.'''
    
    print("Prompt:")
    print(prompt)
    file.write("Prompt:\n")
    file.write(prompt+'\n')
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
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

    print("Response:")
    print(gpt_response.choices[0].message.content)

    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')

    print(ret)

    return ret

def get_gpt_resposne_turbo(question):
    prompt = question

    response = query_engine.query(question)

    text = " "
    # if len(response.source_nodes) != 0:
    #     text = read_pdf(response.source_nodes[0].metadata['file_path'])

    context = ""
    sources = ""
    refs = []
    i = 0
    l = []
    for node in response.source_nodes:
        context += "Context 1: \n\n" + node.text
        sources += node.metadata['file_path'] + '<br>'
        refs.append(node.metadata['file_path'])
        text += f"from the file {node.metadata['file_path']}"
        text += read_pdf(response.source_nodes[0].metadata['file_path'])
        i += 1
        if i==6:
            break
        

    prompt = f'''you have the following contexts.\n
                -------------------------------------------------------------
                context:
                {context} + \n
                {text}
                -------------------------------------------------------------
                sources:
                {sources}
                -------------------------------------------------------------
                Based on these contexts, answer the following query. Try to use exact word from the context.
                Try to use all the information fom the context. Try to preserve the paragrapg numberings also.
                Remove the word "Trayce Hockstad" from your response.
                Query: {question}
                
                If I give you any context please mention the file name from where you are taking your information 
                at the end of your response as "References". Mention exact file paths as numbered list in seperate lines. 
                No need to mention the sources with the paragraphs. Just mention them at the end.

                
                
                No need to mention refrence while aswering to greetings questions like Hi or Hello.'''
    
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
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

    print(gpt_response.choices[0].message.content)

    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
    modified_ret = ret

    for ref in refs:
        if ref in ret:
            modified_ref = modify_ref(ref)
            print(ref,'\n',modified_ref)
            modified_ret = modified_ret.replace(ref,modified_ref)

    # if sources != "":
    #     ret+=  '<br><br>Source:<br>' + sources
    print(modified_ret)
    rel_path = "Current Cybersecurity Law\Connecticut\Criminal code\Conn. Gen. Stat. _ 53a-251.pdf"
    return modified_ret #+ '<br>'+'{% load static %}' + '<a href= "{% static \''+ rel_path +'\' %}" target="_blank">'+ rel_path +'</a>'

    # return str(response) + '<br><br>Source:<br>' + sources


def chatbot_turbo(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot turbo')
    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)

        start_time = time.time()
        response = get_gpt_resposne_turbo(message)
        end_time = time.time()

        processing_time = end_time - start_time

        print('turbo', processing_time)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')

def get_response(query):
    required_states_set = set(get_required_states(query).split(','))

    required_states = []
    for state in required_states_set:
        required_states.append(state.strip())
    
    if "" in required_states:
        required_states.remove("")

    max_token_count = (16300 - 1500) / len(required_states)
    
    response = "Looking into the following states: <br>"
    ind = 1
    for state in required_states:
        response += str(ind) + '. ' + state + '<br>'
        ind+=1

    context = ''
    # response += '<br>Responses based on different states:<br>'
    state_wise_responses = {}
    for state in required_states:
        response += '<br>' + state + ':<br>'
        if state in state_wise_query_engines:
            print(f"---------- Getting response for: {state} ---------------")
            state_wise_response = get_state_wise_response(state,query)
            token_count = count_tokens(state_wise_response) 
            if token_count > max_token_count:
                print(f"---------- Getting summary for: {state} ---------------")
                state_wise_response = get_summary(query, state_wise_response)
            context += state_wise_response + '\n'
            response += state_wise_response +'<br>'
            # for summarization
            state_wise_responses[state] = state_wise_response
        else:
            print(f'{state} is not present ------------------------------')
            response += f'No documents found based on {state}.' +'<br>'

    accumulated_response = ""
    if len(required_states)>1:
        try:
            accumulated_response = get_accumulated_response(context, query)
            # return accumulated_response
        except Exception as e:
            print("Maximum limit of context exceeded!")
            response = "Looking into the following states: <br>"
            ind = 1
            for state in required_states:
                response += str(ind) + '. ' + state + '<br>'
                ind+=1

            context = ''


            for state in required_states:
                response += state + ':<br>'
                if state in state_wise_query_engines:
                    print(f"---------- Getting summary for: {state} ---------------")
                    context += get_summary(query, state_wise_response) + '\n'
                    response += state_wise_response +'<br>'
                else:
                    print(f'{state} is not present ------------------------------')
                    response += f'No documents found based on {state}.' +'<br>'
            
            accumulated_response = get_accumulated_response(context, query)
            # return accumulated_response


        response += '<br>' + accumulated_response + '<br>'
    return response
    # return accumulated_response

def get_summary(question,response):
    
    prompt = f'''To answer the following question, summarise the given response. But keep the reference part as it is.\n
                -------------------------------------------------------------
                Question: {question}
                -------------------------------------------------------------
                Response: {response}
                -------------------------------------------------------------
                '''
    
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
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

    # print(gpt_response.choices[0].message.content)

    ret = str(gpt_response.choices[0].message.content).replace("\n",'<br>')
    return ret

def sol(file):
    df = pd.read_csv(file, encoding='utf-8')

    questions = df['question']

    response = [[],[],[],[],[],[],[],[],[],[]]

    for j, question in enumerate(questions):
        print(question)
        for i in range(10):
            res = get_response(question)
            print(res)
            response[i].append(res)
        print('done')
        if j == 2:
            break



    df_out = pd.DataFrame()
    for i in range(10):
        df_out[f'response_{i+1}'] = response[i]
     
    df_out.to_csv('output_'+file,index=True) 

# sol('qa_trayce_ground_truth.csv')



def chatbot_titan(request):
    # sol()
    # chats = Chat.objects.filter(user=request.user)

    print('Chat bot titan')
    if request.method == 'POST':
        query = request.POST.get('message')
        # print(message)
        start_time = time.time()
        response = get_response(query=query)
        end_time = time.time()
        processing_time = end_time - start_time
        print('titan', processing_time)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': query, 'response': response})
    return render(request, 'chatbot/chatbot.html')


def test(request):
    rel_path = "Current Cybersecurity Law\Connecticut\Criminal code\Conn. Gen. Stat. _ 53a-251.pdf"
    link = '<a href=\'\{\% static \"'+rel_path+'\" \%\}\' target="_blank">'+ rel_path +'</a>'

    print(state_wise_query_engines.keys())

    return render(request, 'chatbot/test.html',{'link':link})

