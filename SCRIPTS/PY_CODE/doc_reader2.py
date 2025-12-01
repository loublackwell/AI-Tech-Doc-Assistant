from unstructured.partition.auto import partition
import json
from pathlib import Path
import os
from groq import Groq

dir_path1= "/Users/lewisblackwell/Documents/RESUME/TORCH.AI/GIT/AI-Tech-Doc-Assistant/TECH_DOCUMENTS/DOCUMENTS/Crawfords_Auto_Repair_Guide.pdf"
dir_path="/Users/lewisblackwell/Documents/RESUME/TORCH.AI/GIT/AI-Tech-Doc-Assistant/TECH_DOCUMENTS/DOCUMENTS"
path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key
prompt_path="/Users/lewisblackwell/Documents/RESUME/TORCH.AI/GIT/AI-Tech-Doc-Assistant/PROMPTS/prompt_classify_doc.txt"


def query_gemini(task):
    # Query LLM. Takes as input the task definitiion and returns the LLM response.
    query_state = ""
    TEXT = ""
    model_name="gemini-2.0-flash"
    try:
        # Pass the API key directly as a string, not as a dictionary
        client = genai.Client(api_key=my_key)#Only hardcode when running app on my local machine
        
        #client = genai.Client(api_key=st.secrets["API_KEY"])#Use when running on cloud

        response = client.models.generate_content(
            model=model_name, contents=task
        )
        TEXT = str(response.text)
        # st.text(f"LLM:{TEXT}")
    except Exception as e:
        st.write(f"Unable to query llm. Please check network connection:  {e}")
        query_state = "error"
    return TEXT, query_state



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
    prompt=f"""{{classify_prompt}}
    
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
    path="/Users/lewisblackwell/Documents/API/groq.txt"#Read API Key
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


def process_pdf(doc_path):
    complete_list=[]
    all_text=[]
    # parameters for extract images:

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
        print(temp)
        
        #print("---")
    viewJson=json.dumps(complete_list,indent=2,ensure_ascii=False)
    print("Saving json")
    with open("doc_json_test.json","w") as f:
        f.write(viewJson)
    return complete_list,all_text


def process_docs(dir_path):
    doc_list=[]
    all_text=[]
    # Returns a list of pdf or txt files if found in directory
    path=Path(dir_path)
    for file_name in path.iterdir():
        file_ext=file_name.suffix.lower()#Get file extension
        file_path=os.path.join(dir_path,file_name)
        
        print(file_ext,file_path)
        #Read text file
        if file_ext==".txt":
            doc_list=process_txt(file_path)

        #Read pd file
        if file_ext==".pdf":
            doc_list,all_text=process_pdf(file_path)
        return doc_list,all_text

#Testing
if __name__=="__main__":
    print("hello")
    #doc_list,all_text=process_docs(dir_path)
    
    """
    samples=" ".join(all_text[0:75])
    prompt=task(samples,prompt_path)
    out=my_groq(prompt)
    print(out)
    #A,B=process_pdf(dir_path1)
    """
