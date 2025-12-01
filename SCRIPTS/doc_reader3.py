#Author: Lewis Blackwell
from unstructured.partition.auto import partition
import json
from pathlib import Path
import os
from groq import Groq

global chunk_path

path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key (Replace path with your local key)

cwd=Path.cwd() # Current working directory
chunk_path=cwd / "group_by_titles"   #Path where documents that are grouped by title are saved.

def read_prompt(prompt_path):
    #Open prompt given path as input
    try:
        with open(prompt_path,"r") as f:
            text=f.read()
            return text
    except Exception as e:
        text=""
        print(f"Unable to open prompt: {prompt_path}: {e}")
    return text
    

def task(sample_text,prompt_path):
    classify_prompt=read_prompt(prompt_path)#Load classification prompt
    prompt=f"""{classify_prompt}
    
    {sample_text}
    """
    return prompt

def classify_doc():
    pass

def read_api(path):
    api_key=None
    with open(path,"r") as f:
        api_key=f.read().strip()
    return api_key

def my_groq(prompt):
    path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key (local testing only)
    api_key=read_api(path)# Get API key
    out=groq_llm(path,api_key,prompt)
    return out


def groq_llm(path,api_key,content):
    client = Groq(api_key=api_key)
    model_name="llama-3.1-8b-instant"
    model_name = model_name = "llama-3.3-70b-versatile"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model=model_name,
    )
    try:
        out=chat_completion.choices[0].message.content
    except Exception as e:
        out=None
    return out


def process_pdf_txt(doc_path,image_bool):
    complete_list=[]
    all_text=[]
    if image_bool==True:
        # parameters for extract images:
        # ADD THESE PARAMETERS to extract images:
        elements = partition(
        filename=doc_path,
        extract_images_in_pdf=True,                           # Enable image extraction
        extract_image_block_output_dir="./extracted_images"   # where images are saved-Verify if images get***** overwritten
        )
    else:
        #Only extract text and ignore any embedded images
        elements = partition(filename=doc_path)#Only get non image elements
    
    # Now iterate
    for pos,element in enumerate(elements):
        text=element.text
        all_text.append(text)
        page_num = element.metadata.page_number
        category = element.category
        temp = {
        "type": type(element).__name__,
        "text": element.text if element.text else 'N/A',
        "page": page_num,
        "category": category,
        "image_path": getattr(element.metadata, 'image_path', None),
        "coordinates": str(getattr(element.metadata, 'coordinates', None)),  # Bounding boxes
        "filename": element.metadata.filename
        }
        complete_list.append(temp)
        #print(temp)
        #print("---")
    viewJson=json.dumps(complete_list,indent=2,ensure_ascii=False)
    with open("doc_json.json","w") as f:
        f.write(viewJson)
    return complete_list,all_text


def process_docs(dir_path,image_bool):
    #Initialize variables
    counter=0
    doc_list=[]
    all_text=[]
    all_docs=[]
    all_schema={"context":[],
                "image-dict":{}}
    # Returns a list of pdf or txt files if found in directory
    path=Path(dir_path)
    #print(f"PATH:{path}")
    #Loop thru each file
    for file_name in path.iterdir():
        counter+=1
        file_ext=file_name.suffix.lower()#Get file extension
        file_path=dir_path / file_name #File path
        print(f"{counter}: {file_name.name}")

        #Process .pdf or .txt files only
        if file_ext==".pdf" or file_ext==".txt":
            doc_list,all_text=process_pdf_txt(file_path,image_bool)#Process each pdf and txt file.
            all_schema=group_by_title(doc_list,file_name,all_schema)#Split document text by chunks
            
            
            #Captures metadata for each document
            """
            temp={"file_name":file_name.name,"type":file_ext,
            "doc_list":doc_list,"all_text":all_text}
            """
            temp2={"file_name":file_name.name,"type":file_ext,
            "doc_list":all_schema,"all_text":all_text}
            all_docs.append(temp2)
            
    if all_schema["context"]:
        save_title_context(all_schema,chunk_path)
    return all_schema,all_docs
       


def group_by_title(docs,file_name,schema):
    #Groups unstructured output by title
    image_dict={}
    title_context=[]
    if "context" not in schema:
        schema["context"]=[]
    if "image-dict" not in schema:
        schema["image-dict"]={}
        
    text_list=[]
    title_list=[]
    image_list=[]
    title_counter=0
    reset=0
    title=""
    previous_title=""
    previous_page=None
    """
    {'FigureCaption',
     'Header',
     'Image',
     'ListItem',
     'NarrativeText',
     'Table',
     'Text',
     'Title'}
    """

    for pos,doc in enumerate(docs): # Loop thru each split section of document
        header=doc.get("Header")
        image=doc.get("image_path")
        narrativetext=doc.get("NarrativeText")
        table=doc.get("Table")
        page=doc.get("page")
        doc_type=doc.get("type")
        text=doc.get("text")
        fname=file_name.name#Filename
        
        #Group text in doc by title when detected by unstrictured
        if doc_type=="Title" and text.strip()!="":
            title=text
            title_counter+=1#Count the number of detected titles
            if reset!=title_counter:
                ID=f"{fname}-{pos}".strip() #ID for indexing in Chromadb
                #List of dictionaries with metadata captured by title
                #Capture metadata capture between title text blocks
                temp={"id":ID,"step":pos,"page":page,"title":previous_title,"supporting_text":text_list,"image_path":image_list}
                if image_list!=[]:
                    image_dict[ID]=image_list #Track image list by ID
                
                title_context.append(temp)#Capture title and mapping text
                text_list=[]
                image_list=[]
                
        else:
            text_list.append(text)
            #Update image to list if there
            if image!=None:
                image_list.append({"path":image,"page":page,"position":pos})
            reset=title_counter
            previous_title=title
            previous_page=page

    ID=f"{fname}-{pos}".strip() #ID for indexing in Chromadb
    if text_list and title:
        temp={"id":ID,"step":pos,"page":previous_page,"title":title,"supporting_text":text_list,
              "image_path":image_list}
        image_dict[ID]=image_list
        title_context.append(temp)
        
    #Capture document anatomy and image dict
    schema["context"].extend(title_context)
    schema["image-dict"].update(image_dict)
    return(schema)

def save_title_context(title_context,chunk_path):
    #Save doc metadata
    try:
        chunk_fname=os.path.join(chunk_path,"chunk_metadata.json")
        viewJson=json.dumps(title_context,indent=2,ensure_ascii=False)
        with open(chunk_fname,"w") as f:
            f.write(viewJson)
    except Exception as e:
        print(f"Unable to save:{chunk_fname}: {e}")
        

#Testing
if __name__=="__main__":
    print("test")
    all_schema,doc_list=process_docs(dir_path,image_bool=True)
    viewJson=json.dumps(doc_list,indent=2,ensure_ascii=False)
    with open("group.json","w") as f:
        f.write(viewJson)
    print(doc_list[0:10])
    #samples=" ".join(all_text[0:75])
    #prompt=task(samples,prompt_path)
    #out=my_groq(prompt)
    #print(out)
    #A,B=process_pdf(dir_path1)

