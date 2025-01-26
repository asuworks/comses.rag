from dataclasses import dataclass
from typing import List, Optional

from shared.models.model_metadata import ModelMetadata


@dataclass
class DocSectionQA:
    id: str
    docsection_id: str
    question: str
    answer: str


@dataclass
class ChunkQA:
    id: str
    chunk_id: str
    question: str
    answer: str

# max chunk size ~ 100-250 words? Semantic Chunking? Chunk overlapping?
# -> TODO: find a good chunking strategy
@dataclass
class Chunk:
  id: str
  doc_section_id: str

  type: str  # text | image | table | formula | ...

  # this will be the text for the main embedding
  content: str

  ############################ LLM generated attributes ########################

  # llmgenerated
  # enrich content by adding additional content from outer scope (all parent DocSections content)
  content_with_context: Optional[str] = None

  # llmgenerated
  # summary of the chunk
  summary: Optional[str] = None

  # List of Q&A about the chunk: [{"question": "A question about the content of the chunk"], "answer": "Answer to the question."}] #llmgenerated
  qas: Optional[List[ChunkQA]] = None

@dataclass
class DocSection:
  id: str

  ################################# References #################################

  # fk reference to the ModelDocs object
  model_doc_id: str

  ########################## DocSection attributes #############################

  title: str
  level: int
  content: str  # all section content
  chunks: List[Chunk]  # used to compute embeddings

  ######################## LLM generated attributes ############################

  # llmgenerated
  # LLM generated DocSection summary
  summary: Optional[str] = None

  # llmgenerated
  # List of QAs about the chunk:
  qas: Optional[List[DocSectionQA]] = None

  # sibling DocSections (text is split into chapters, chapters into subchapters...)
  parent: Optional['DocSection'] = None
  children: Optional[List['DocSection']] = None

@dataclass
class ModelDoc:
  id: str

  # reference to the Model
  model_id: str

  # DocSections
  doc_sections: List[DocSection] # on_delete: cascade

  # LLM generated summarized version of the ODD protocol
  summary: Optional[str] = None

  # source documentation MINIO object names (store them for reference)
  markdown_object_name: Optional[str] = None
  original_source_object_name: Optional[str] = None

# Analog to CoMSES Codebase
@dataclass
class Model:
  id: str
  external_id: str  # comses codebase id

  metadata: ModelMetadata
  docs: ModelDoc
  # code: ModelCode

@dataclass
class IngestModelInput:
  model_id: str # this should be set externally -> uuid.UUID
  model_slug: str  # used for workflow ids, minio object names
  original_file_path: str  # pdf documentation file
  metadata_json_path: str  # codemeta.json
  code_folder_path: Optional[str] = None  # folder with code source files