# AI-Tech-Doc-Assistant

## Screenshots

![USER INTERFACE](SCREEN_SHOTS/ui_overview.png)
*User Interface with indexing menu and query Input*


![USER INTERFACE](SCREEN_SHOTS/query.png)
*Sample query results with supporting text and image*


![USER INTERFACE](SCREEN_SHOTS/output2.png)
*Sample 'AI Assistant' output based on query results context*


![USER INTERFACE](SCREEN_SHOTS/json_output.png)
*Sample JSON output*

## Overview
Retrieval Augmented Generation (RAG) system to support Q/A of technical documents


## App Features

- **Technical Document Processing & Analysis**: Support PDF and TXT document types using the Unstructured library
- **Streamlit Interface**: Supports Q/A and configurable indexing options

- **Semantic Search**: ChromaDB vector database with sentence-transformers embeddings

- **Multi-Query Decomposition**: Automatically breaks compound questions into sub-queries or a list of queries

- **Cross-Encoder Reranking**: Improves result relevance using ms-marco-MiniLM model

- **PDF Image Extraction**: Captures and displays document images with supporting text

- **JSON Output**: Optional structured output for system integration

- **Named Entity Recognition (Future Version)**:
