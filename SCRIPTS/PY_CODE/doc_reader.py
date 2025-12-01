from unstructured.partition.auto import partition
import json
from pathlib import Path

global file_name
cwd=Path.cwd()#Current working directory
doc_path ="/Users/lewisblackwell/Documents/DATASETS/Crawfords_Auto_Repair_Guide.pdf"

#process_type="image_text"
#process_type="text"

#The following script uses the unstructured library to read text or PDF files and save as json file.
def process_doc(doc_path,process_type):
    file_name=Path(doc_path).name
    complete_list=[]
    #/Users/lewisblackwell/Documents/RESUME/TORCH.AI/GIT/AI-Tech-Doc-Assistant/TECH_DOCUMENTS/IMAGES
    image_folder="./extracted_images"
    # ADD THESE PARAMETERS to extract images:
    if process_type=="image_text":
        print("Processing text and images")
        elements = partition(
            filename=doc_path,
            extract_images_in_pdf=True,                           # Enable image extraction
            extract_image_block_output_dir=image_folder  # Where images are saved.
        )

    else:
        print("Processing text only")
        elements = partition(filename=doc_path)#Only get non image elements
        
    # Now iterate through docment and capture metadata
    for pos,element in enumerate(elements):
        page_num = element.metadata.page_number
        category = element.category
        temp = {
        "iter":pos,
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
    save_path=cwd / "json_files" / f"{file_name}_doc.json" #Path where files are saved
    with open(save_path,"w") as f:
        f.write(viewJson)

if __name__=="__main__":
    process_doc(doc_path,process_type="text")
