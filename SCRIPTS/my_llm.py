#Author: Lewis Blackwell
from unstructured.partition.auto import partition
import json
from pathlib import Path
import os
from groq import Groq

global chunk_path

path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key (Replace with your actual key)


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
    #Future implementation
    #The idea here is to build a classifer that could classify the doc type and approximate
    #the chunking values.
    pass

def read_api(path):
    api_key=None
    with open(path,"r") as f:
        api_key=f.read().strip()
    return api_key

def my_groq(prompt):
    path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key
    try:
        api_key=read_api(path)# Get API key
        out=groq_llm(path,api_key,prompt)
    except Exception as e:
        print(f"Unable to process llm request: {e}")
        out=f"Unable to process llm request: {e}"
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




#Testing
if __name__=="__main__":
    print("test")
