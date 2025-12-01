#Author: Lewis Blackwell
"""
#Chromadb Reference Docs: 
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

#Declaration of variables
global cwd,json_path,vector_store
length=512
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=length)
cwd=Path.cwd()#Get current working directory
parent=cwd.parent
group_by_titles=parent / "group_by_titles"
json_file= group_by_titles / "chunk_metadata.json"

vector_store="chromadb_vector_store"

def read_schema(json_file):
    #Transforms file into indexing format
    #try:
    ids=[]
    documents=[]
    image_list=[]
    try:
        with open(json_file,"r") as f:
            schema=json.loads(f.read())
            context=schema["context"]#Returned group text by title
            image_list=schema["image-dict"]#Return image dictionary
        for rec in context:
            ID=rec["id"]
            title=rec["title"]
            supporting_text=rec["supporting_text"]
            text=" ".join(supporting_text)
            ids.append(ID)
            documents.append(text)
    except Exception as e:
        print (f"Unable to read: {json_file}: {e}")
    return ids,documents,image_list
        

def create_folder(default_folder):
    #Create folder
    if not os.path.exists(default_folder):
        os.makedirs(default_folder)


def create_collection(default_folder,collection_name):
    collection_folder=os.path.join(default_folder,collection_name)
    create_folder(collection_folder)
    try:
        #Build Chromadb collection name
        client = chromadb.PersistentClient(collection_folder)    
        collection = client.get_or_create_collection(name=collection_name)
        return collection,client
    except Exception as e:
        collection_message=f"Unable to create collection: {collection_name}: {e}"
        print(collection_message)
        return None,None


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


def add_documents(collection,documents,my_ids):
    #Add documents to chroma vector database
    try:
        collection.upsert(
            documents=documents,
            ids=my_ids
        )  
    except Exception as e:
        print("Unable to add documents to collection")


def query_collection(collection,query,k):
    #Query collection
    try:
        results = collection.query(
        query_texts=[query], # Chroma will embed this for you
        n_results=k # how many results to return
        )
        print(f"QUERY RESULTS:{results}")
    except Exception as e:
        print(f"Unable to query DB: {e}")
        results=""
    return results


def get_collection(default_folder,collection_name):
    #Get collection and return collection and client.
    try:
        collection_path=default_folder / collection_name
        client = chromadb.PersistentClient(path=str(collection_path))
        collection =client.get_or_create_collection(name=collection_name)
        print(f"Got collection name: {collection_name} {type(collection)}")
        return collection,client
    except Exception as e:
        print(f"Unable to retrieve collection: {e}")
        return None,None

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
def reranker_with_scores(query, documents, threshold=-999):
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


def chromadb_index_process(collection_name,my_ids,documents,json_file):
    #Create collection given name as input
    collection,client=create_collection(collection_name)
    #Add documents to collection
    add_documents(collection,documents,my_ids)
    return collection

    
# # Test Script functions
if __name__=="__main__":
    print(parent)
    #my_ids, documents=read_schema(json_file)
    #print(my_ids[0:10])

    collection_name="my_collection"
    #collection=chromadb_index_process(collection_name,my_ids,documents,json_file)

    #Query Vector database and display results
    query="Change your oil"
    collection,client=get_collection(collection_name)
    results=query_collection(collection,query,k=5)
    print(results)
    
"""
    #Delete records
    id_list=['10','33']
    delete_record_by_id(collection,client,id_list,collection_name)
    delete_collection(collection_name)


#valid_indicies=reranker_with_scores(query,documents)
#print(valid_indicies)

#valid_indicies[0]
"""


