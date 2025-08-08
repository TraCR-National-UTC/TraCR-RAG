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

from dotenv import load_dotenv

# Create your views here.
load_dotenv()  # loads variables from .env into environment
openai_api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"] = openai_api_key
client = openai.OpenAI()


data_folder = BASE_DIR / 'Current Cybersecurity Law/'
PERSIST_DIR = BASE_DIR / f'Vector_Storage_Context/'
PERSIST_DIR_TREE = BASE_DIR / f'Tree_Index_Previous/'

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

def get_tree_query_engine():
    print('Getting tree query engine')
    
    if not os.path.exists(PERSIST_DIR_TREE):
    # creating the index from the documents
        os.mkdir(PERSIST_DIR_TREE)

        pdf_files = get_pdfs(data_folder)
        documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
        tree_index = TreeIndex.from_documents(documents=documents, build_tree=True)

        # store it for later
        tree_index.storage_context.persist(persist_dir=PERSIST_DIR_TREE)
    else:
        # retrieving a storage context from already exixting contex and loading the index
        storage_contex = StorageContext.from_defaults(persist_dir=PERSIST_DIR_TREE)
        tree_index = load_index_from_storage(storage_context=storage_contex)

    tree_retriever = TreeRootRetriever(index=tree_index)
    tree_query_engine = RetrieverQueryEngine(retriever=tree_retriever)
    print('Tree Query engine created')

    return tree_query_engine


query_engine = get_query_engine()
tree_query_engine = get_tree_query_engine()


def get_tree_gpt_resposne(question):
    prompt = question

    response = tree_query_engine.query(question)

    # context = ""
    # sources = ""
    # for node in response.source_nodes:
    #     context += "Context 1: \n\n" + str(response)
    #     sources += node.metadata['file_path'] + '<br>'
    #     break

    # prompt = f'''you have the following contexts and the source of contexts.\n
    #             -------------------------------------------------------------
    #             context:
    #             {context}
    #             -------------------------------------------------------------
    #             sources:
    #             {sources}
    #             -------------------------------------------------------------
    #             Based on these contexts, answer the following query. Try to use exact word from the context.
    #             Query: {question}'''
    
    # gpt_response = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    # messages= [
    #     {
    #         "role":"system",
    #         "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
    #     },
    #     {
    #         "role":"user",
    #         "content":prompt
    #     }
    # ]
    # )

    # print(gpt_response.choices[0].message.content)
    # ret = gpt_response.choices[0].message.content
    # if sources != "":
    #     ret += '<br><br>Source:<br>' + sources

    # return  ret

    return str(response)


def get_gpt_resposne(question):
    prompt = question

    response = query_engine.query(question)

    text = " "
    if len(response.source_nodes) != 0:
        text = read_pdf(response.source_nodes[0].metadata['file_path'])

    context = ""
    sources = ""
    for node in response.source_nodes:
        context += "Context 1: \n\n" + node.text
        sources += node.metadata['file_path'] + '<br>'
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
                Query: {question}'''
    
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
    if sources != "":
        ret+=  '<br><br>Source:<br>' + sources
    return ret

    # return str(response) + '<br><br>Source:<br>' + sources

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
    print("printing link\n")
    print(html)
    return html

def get_gpt_resposne_beta(question):
    prompt = question

    response = query_engine.query(question)

    text = " "
    # if len(response.source_nodes) != 0:
    #     text = read_pdf(response.source_nodes[0].metadata['file_path'])

    context = ""
    sources = ""
    i = 0
    l = []
    for node in response.source_nodes:
        context += "Context 1: \n\n" + node.text
        sources += node.metadata['file_path'] + '<br>'
        text += f"from the file {node.metadata['file_path']}"
        text += response.source_nodes[0].text
        i += 1
        if i==10:
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
                at the end of your response as reference. Mention exact file paths as numbered list in seperate lines'''
    
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
    # if sources != "":
    #     ret+=  '<br><br>Source:<br>' + sources
    return ret

    # return str(response) + '<br><br>Source:<br>' + sources

def get_required_states(query):
    prompt = f'''Suppose I have legislation documents on all the states of United States.\n
                Based on the folllowing query, which state documents should I look into?\n

                If the query says compare between state X and Y, you should mention both state X and Y.
                If the query says compare between state X and all other state with a condition,
                you should mention state X and all other state that satisfies the condition.
                If the query does not mention any staet, you should mention all the states that are in the U.S.
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
            "content":"You are a helpful assisstant. Your name is TraCR AI. You were developed by TraCR. Your role is to help with Transportation Cybersecurity Legislations."
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
    data_folder = data_folder + state_name + '/'
    PERSIST_DIR = PERSIST_DIR + state_name + '/'
    

    index = None

    if not os.path.exists(PERSIST_DIR):
        # creating the index from the documents
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

state_wise_query_engines = create_indices()

# Create your views here.
def chatbot(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot 1')

    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)
        response = get_gpt_resposne(message)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')

def chatbot_2(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot 2')
    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)
        response = get_tree_gpt_resposne(message)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')


def chatbot_turbo(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot turbo')
    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)
        response = get_gpt_resposne_turbo(message)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')


def chatbot_beta(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot turbo')
    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)
        response = get_gpt_resposne_beta(message)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')

def chatbot_titan(request):
    # chats = Chat.objects.filter(user=request.user)
    print('Chat bot turbo')
    if request.method == 'POST':
        message = request.POST.get('message')
        # print(message)
        required_states = get_required_states(message).split(',')
        
        response = "Looking into the following states: <br><br>"
        for state in required_states:
            response += state + '<br>'
        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot/chatbot.html')


def test(request):
    rel_path = "Current Cybersecurity Law\Connecticut\Criminal code\Conn. Gen. Stat. _ 53a-251.pdf"
    link = '<a href=\'\{\% static \"'+rel_path+'\" \%\}\' target="_blank">'+ rel_path +'</a>'

    return render(request, 'chatbot/test.html',{'link':link})

