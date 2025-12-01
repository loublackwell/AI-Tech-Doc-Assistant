#!/usr/bin/env python
# coding: utf-8

# In[3]:


import json
import os


# In[10]:


#This script is to be used in conjunction with: doc_reader.py (uses unstructured)

path="/Users/lewisblackwell/Documents/DESIGN_KID/notebooks/doc_json.json"
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


# In[5]:


def read_json(path):
    try:
        with open(path,"r") as f:
            pydict=json.loads(f.read())
            return pydict
    except Exception as e:
        print(f"Unable to read {path} due to: {e}")


# In[6]:


docs=read_json(path)


# In[7]:


title_context=[]
text_list=[]
title_list=[]
title_counter=0
reset=0
title=""

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
    image=doc.get("Image")
    narrativetext=doc.get("NarrativeText")
    table=doc.get("Table")
    page=doc.get("page")
    doc_type=doc.get("type")
    text=doc.get("text")

    #Group text in doc by title when detected by unstrictured
    if doc_type=="Title" and text.strip()!="":
        title=text
        title_counter+=1#Count the number of detected titles
        
        if reset!=title_counter:
            List of dictionaries with metadata captured by title
            #Capture metadata capture between title text blocks
            title_context.append([{"step":pos,"page":page,"title":previous_title,"supporting_text":text_list}])#Capture title and mapping text
            text_list=[]
            
    else:
        text_list.append(text)
        reset=title_counter
        previous_title=title
        previous_page=page


# In[8]:


title_context[10]


# In[9]:


for check in title_context:
    print(check[0])


# In[ ]:





# In[ ]:




