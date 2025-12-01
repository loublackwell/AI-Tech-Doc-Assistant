#Author: Lewis Blackwell
import streamlit as st
from annotated_text import annotated_text
import json
from pathlib import Path
import os
from SCRIPTS.doc_reader3 import process_docs
from SCRIPTS.vector_chromadb import chromadb_index_process
from SCRIPTS.vector_chromadb import read_schema
from SCRIPTS.vector_chromadb import query_collection
from SCRIPTS.vector_chromadb import get_collection
from SCRIPTS.vector_chromadb import create_collection
from SCRIPTS.vector_chromadb import add_documents
from SCRIPTS.vector_chromadb import reranker_with_scores
from SCRIPTS.my_llm import my_groq
import json_repair
import time

#Main function for indexing tech documents (Demo)

#Declaration of variables
doc_number=0
chunk_size=0
chunk_overlap=0
image_dict={}
compound_list=[]
summary=""
text_group=""
cwd=Path.cwd()#Current working directory
vector_store_name="chromadb_vector_store"
default_folder=cwd / vector_store_name #Folder containing vectordb collections
documents_folder=cwd / "TECH_DOCUMENTS" / "DOCUMENTS" #Folder containing tech documents
json_file=cwd / "group_by_titles"/"chunk_metadata.json"
#PROMPT
summarize="""Summarize the text below in no more than 3 paragraphs only from the context of '{query}'.
                Do not add any additional information other than what was mentioned in the text. If there
                is not supporting text to answer the question directly or implicitly then say so. :
                   Text:
          """
compound_query="""
                 Your task is to determine if a 'query' to a database is a 'single query' or a 'compound query'. Note that if a query no matter how simple has more than one request, break down the single query into a list of queries. One hint that the query is compund is when the query has the word, 'and' or any other similar word that combines two or more requests together. Look at the example below. It is important to note that there are cases where 'and' is not explicitly used but may be implied. No other comments should be added
                 
                 
                 EXAMPLE OF A QUERY THAT NEEDS TO BE CONVERTED TO A LIST OF QUERIES:
                 How do you change a tire and how does a transmission work also list the two types of transmissions.
                 
                 Your task is to convert these type of queries into a unique list between triple backticks. Each query should end with a question mark. For example,
                 ```
                 How do you change a tire?
                 how does a transmission work?
                 List the two types of transmissions?
                 ```
                Remember to place the output between triple backticks and not add or remove any text from the original query or add additional information that was not requested and take your time and think through the reasoning process I explained before answering the question.
                
                ORIGINAL QUERY:
                 """
sme="technical writer"
years=25
main_query=f"""
      You are an expert {sme} with {years} of experience. Your task is to evaluate the provided text below and answer the query in the context of the text. Do not add any additiional comments than what was initially asked and do not add or remove anything from the included text. make sure you provide a thorough explanation using the text provided that includes your reasoning process:
          Place your answer in a valid python list between triple backticks as shown below:
          
          PYTHON OUTPUT FORMAT:
          ```
          {{'out':<insert your thoughtfull explnation here>}}
          ```
          TEXT:
           """

def multi_query(query):
    time.sleep(0.5)
    query=query.strip()
    #Query to break query into a list of queries.
    comp_query=f"{compound_query} {query}"
    out=my_groq(comp_query) #Transforms query to list.
    out=out.replace('\n','')
    questions=out.split("?")#Convert query into a list of queries
    questions2=[x for x in questions if x!=""]
    return questions2

def highlighter(text):
    # Highlight the entire variable
    annotated_text(
    (text, "summary", "#faa")
                    )
                    
def get_document_list(documents_folder):
    #Return list of files in directory
    all_docs=[]
    for file in documents_folder.iterdir():
        name=file.name
        extension=file.suffix #File extension
        if extension.lower==".txt" or extension.lower()==".pdf":
            all_docs.append(name)
    return (all_docs)

#User Interface
st.sidebar.title("AI Tech-Doc Assistant")
st.sidebar.write("#### Tech-Doc Indexing Parameters")

#indexing_options=st.sidebar.radio(
#        "Select Document(s) to Index",["Index Single doc","Index all docs"]
#                          )
indexing_options=st.sidebar.radio(
        "Select Document(s) to Index",["Index all docs"]
                          )

all_docs=get_document_list(documents_folder)
if indexing_options=="Index Single doc":
    selected_file = st.sidebar.selectbox("Choose a document to index", all_docs)
    print(all_docs)
    doc_number=1
else:
    st.sidebar.text(f"{len(all_docs)} documents available for indexing")
    doc_number=len(all_docs)

#Chunking Options
chunking_options=st.sidebar.radio(
        "Chunking options",["Auto Chunking","Static Chunking"])

if chunking_options=="Static Chunking":
    # Chunk size and overlap sliders
    chunk_size = st.sidebar.slider("Choose chunk size", min_value=128, max_value=1024, value=512, step=128)
    chunk_overlap = st.sidebar.slider("Choose chunk overlap", min_value=0, max_value=100, value=50, step=10)
    chunk="static"
else:
    chunk="auto"


#Image capture options
image_options=st.sidebar.radio(
        "Doc Image Indexing options",["Capture Image(s)","No Image Capturing"])
if image_options=="Capture Image(s)":
    image=True
else:
    image=False

    
#User selections:
st.sidebar.write("Current indexing parameters")
selections={"doc_number":doc_number,"chunking_type":chunk,
            "image":image,"chunk_size":chunk_size,
            "chunk_overlap":chunk_overlap}

# Create a container with a border
#container = st.container(border=True)

if os.path.isfile(json_file):
    my_ids, documents,image_dict=read_schema(json_file)#RETURN ID's documents and the image_dict list
    
#-------- INDEXING PROCESS --------
collection_name="my_collection" #**Create option for user to pass their own collection name **
index_button=st.sidebar.button("Index Documents")
if index_button:
    st.sidebar.text("Indexing in progress")
    
    #Read in all Document metadata and prepare for indexing
    my_ids, documents,image_dict=read_schema(json_file)#RETURN ID's documents and the image_dict list
    #Creates collection
    collection,client=create_collection(default_folder,collection_name)
    #Index collection
    add_documents(collection,documents,my_ids)
    
    #READ AND PROCESS DOCUMENTS
    if doc_number==1:
        single_file=[documents_folder / selected_file]
    
    else:
        all_schema,all_docs=process_docs(documents_folder,image)
        
#------- QUERY VECTORDB --------
collection_name="my_collection"
st.write("#### Query Your Documents")
documents2=[]
my_ids2=[]
dedup_dict={}

# Query input text box
query = st.text_input("Enter your question:")
original=query
if query!="": #CHECK FOR EMPTY OR NULL INPUT.
    text_group=""

    collection,client=get_collection(default_folder,collection_name)#Get collection
    if not collection: #Check if collection exists
        st.error("No Collection found. Please index documents first!")
        st.stop()
        
    print(f"Querying... {collection}")
    
    query_list=multi_query(query)#Converts input query into a list of queries
    for sub_query in query_list:
        results=query_collection(collection,sub_query,k=5)#Query collection
        #st.write(results)
        documents=results["documents"][0]#Returns the documents that were retrieved based on the query
        my_ids=results["ids"][0]
    
        valid_indices, valid_scores=reranker_with_scores(sub_query, documents, threshold=-999)

        #st.write("#### Query Results:")
        for pos,indicie in enumerate(valid_indices):
            ID=my_ids[indicie] #ID record
            
            #Only process unique ID's to prevent duplication of results
            if dedup_dict.get(ID)==None:
                dedup_dict[ID]="match"
                images=image_dict.get(ID)#Get any mapping images
                
                record=documents[indicie] #Mapping record
                
                text_group=text_group+record
                with st.expander(f"{pos}. {record[0:70]}..."):
                    if images!=None:
                        for image in images:
                            path=image["path"]
                            st.image(path)
                            #container.image(path)
                    #st.write(images)
                    st.text(f"{ID}\n,{record}")
    
    #----- QUERY OUTPUT RESULTS ----
    if text_group!="":
        prompt=f"""{main_query} 
                   {text_group}
                   QUERY:{original}
                """
        out=my_groq(prompt) #Get LLM feedback
        try:
            st.write("#### Text Output from LLM")
            pydict= json_repair.loads(out)#Try and repair any broken json from LLM
            if isinstance(pydict,dict):
                feedback=pydict.get("out",out)
                if isinstance(feedback,list):
                    feedback=" ".join(feedback)
                st.write(feedback)
                st.write("#### JSON output from LLM")
                st.write(pydict)
        except Exception as e:
            st.write("#### Error Message")
            st.write(e)
        
        
