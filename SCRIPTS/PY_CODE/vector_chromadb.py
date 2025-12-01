#!/usr/bin/env python
# coding: utf-8

# # Chromadb Library that performs CRUD operations
# ### Lewis Blackwell

# In[66]:


"""
#Reference: 
#https://docs.trychroma.com/docs/overview/getting-started
#https://docs.trychroma.com/docs/run-chroma/persistent-client
#https://docs.trychroma.com/docs/embeddings/embedding-functions#using-embedding-functions
#https://docs.trychroma.com/docs/run-chroma/persistent-client
#https://docs.trychroma.com/docs/collections/manage-collections
#https://cookbook.chromadb.dev/embeddings/cross-encoders/
#https://huggingface.co/cross-encoder
"""
import chromadb
import os
import json
from sentence_transformers import CrossEncoder
from pathlib import Path


# In[67]:


#Declaration of variables
global cwd,json_path,vector_store
length=512
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=length)
cwd=Path.cwd()#Get current working directory
knowledge = "honda_knowledge_store"
json_path=cwd / "honda.json"
vector_store="chromadb_vector_store"


# In[68]:


def create_folder(default_folder):
    #Create folder
    if not os.path.exists(default_folder):
        os.makedirs(default_folder)


# In[69]:


def create_collection(collection_name):
    #cwd=os.getcwd()#Current working directory
    default_folder=cwd / vector_store
    create_folder(default_folder)
    collection_folder=default_folder / collection_name 
    try:
        #Build Chromadb collection name
        client = chromadb.PersistentClient(collection_folder)    
        collection = client.get_or_create_collection(name=collection_name)
        return collection,client
    except Exception as e:
        collection_message=f"Unable to create collection: {collection_name}: {e}"
        print(collection_message)


# In[70]:


def delete_collection(collection_name):
    #Delete Collection
    default_folder=cwd / "chromadb_vector_store"
    create_folder(default_folder)
    collection_folder=default_folder / collection_name
    try:
        client = chromadb.PersistentClient(collection_folder)    
        client.delete_collection(name=collection_name)
        print(f"{collection_name} has been deleted")
    except Exception as e:
        print(f"Unable to delete collection: {collection_name}")


# In[71]:


def add_documents(collection,documents,my_ids):
    #Add documents to chroma vector database
    try:
        collection.upsert(
            documents=documents,
            ids=my_ids
        )  
    except Exception as e:
        print("Unable to add documents to collection")


# In[72]:


def query_collection(collection,query,k):
    #Query collection
    try:
        results = collection.query(
        query_texts=[query], # Chroma will embed this for you
        n_results=k # how many results to return
        )
    except Exception as e:
        print(f"Unable to query DB: {e}")
    return results


# In[73]:


def get_collection(collection_name):
    #Get collection and return collection and client.
    try:
        #cwd=os.getcwd()#Current working directory
        default_folder=cwd / vector_store
        vector_path=default_folder / "my_collection"
        client = chromadb.PersistentClient(path=vector_path)
        collection =client.get_or_create_collection(name=collection_name)
        return collection,client
    except Exception as e:
        print(f"Unable to retrieve collection: {e}")


# In[74]:


def delete_record_by_id(collection,client,id_list,collection_name):
    #Delete records by id list
    try:
        collection =client.get_or_create_collection(name=collection_name)
        collection.delete(
        ids=id_list,
        )
        print("Records deleted")
        return collection
    except Exception as e:
        print(f"Unable to delete records with ID: {id_list}: {e}")


# In[75]:


"""
def reranker(query,documents):
    valid_indices=[]
    scores = model.predict([(query, doc) for doc in results["documents"][0]])
    score_dict={x.item():pos for pos,x in enumerate(scores)}#Use scores as keys
    ranking_keys=list(score_dict.keys())
    ranking_keys.sort(reverse=True)#Sort keys in decending order
    thresh=0
    for key in ranking_keys:
        if key>0 and key>=thresh:
            valid_indices.append(score_dict[key])#Returns valid index position for retrieving valid query results
    return valid_indices
"""
def reranker_with_scores(query, documents, threshold=0):
    #Using a cross encoder
    """Return both indices and scores"""
    scores = model.predict([(query, doc) for doc in documents])
    
    # Create and sort (index, score) pairs
    scored_pairs = [(i, score) for i, score in enumerate(scores)]
    scored_pairs.sort(key=lambda x: x[1], reverse=True)
    
    # Filter by threshold
    valid_pairs = [(idx, score) for idx, score in scored_pairs if score > threshold]
    
    # Separate indices and scores
    valid_indices = [pair[0] for pair in valid_pairs]
    valid_scores = [pair[1] for pair in valid_pairs]
    
    return valid_indices, valid_scores


# # Test Script functions

# In[76]:


#Test
if __name__=="__main__":
    collection_name="my_collection"
    #documents=["This is a document about pineapple","This is a document about oranges"]
    #my_ids=["id1", "id2"]
    documents=[]
    my_ids=[]
    
    #Load dataset-consist of "id" and "text" field. <--(DOCUMENT LOADER SCRIPT WOULD BE USED HERE)
    with open(json_path,"r") as f:
        recs=json.loads(f.read())
    for rec in recs:
        my_ids.append(str(rec["id"]))
        documents.append(rec["text"])  
        
    #Create collection given name as input
    collection,client=create_collection(collection_name)
    
    #Add documents to collection
    add_documents(collection,documents,my_ids)

    #Query Vector database and display results
    query="Change your oil"
    results=query_collection(collection,query,k=5)
    print(results)
    
    #Delete records
    id_list=['10','33']
    delete_record_by_id(collection,client,id_list,collection_name)
    delete_collection(collection_name)


# In[77]:


valid_indicies=reranker_with_scores(query,documents)
print(valid_indicies)


# In[78]:


valid_indicies[0]


# In[ ]:





# In[ ]:




