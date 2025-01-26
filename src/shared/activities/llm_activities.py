from typing import Dict, List

from temporalio import activity, workflow
from temporalio.exceptions import ApplicationError

from shared.models.base import Chunk, \
    DocSection  # Assuming you have this import

with workflow.unsafe.imports_passed_through():
    from langchain_core.messages import BaseMessage

class LLMActivities:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    @activity.defn
    async def chat(self, messages: List[Dict[str, str]]) -> BaseMessage:
        try:
            response: BaseMessage = await self.llm_client.chat(messages)
            activity.logger.info(
                f"Got response from LLM.")
            return response
        except Exception as e:
            raise ApplicationError(f"Failed to chat with LLM: {str(e)}")

    @activity.defn
    async def compute_embedding(self, text: str) -> List[float]:
        if not text:
            return []
        try:
            embedding: List[float] = await self.llm_client.compute_embedding(
                text)

            activity.logger.info(f"Embedding for text {text[0:50]} (text size: {len(text)}) computed.")
            return embedding
        except Exception as e:
            raise ApplicationError(f"Failed to compute embedding: {str(e)}")

    @activity.defn
    async def add_context_to_chunk(self, chunk: Chunk,
                                   context: Dict[str, any]) -> Chunk:
        try:
            chunk.content_with_context = f"{context['doc_section_content']}\n\nContext: {' > '.join(context['title_breadcrumbs'])}\n\n{chunk.content}"
            return chunk
        except Exception as e:
            raise ApplicationError(f"Failed to add context to chunk: {str(e)}")

    @activity.defn
    async def add_chunk_summary(self, chunk: Chunk) -> Chunk:
        try:
            messages = [
                {"role": "system",
                 "content": "You are a helpful assistant that summarizes text."},
                {"role": "user",
                 "content": f"Please summarize the following text:\n\n{chunk.content}"}
            ]
            response = await self.chat(messages)
            chunk.summary = response.content
            return chunk
        except Exception as e:
            raise ApplicationError(f"Failed to add chunk summary: {str(e)}")

    @activity.defn
    async def add_chunk_qas(self, chunk: Chunk) -> Chunk:
        try:
            messages = [
                {"role": "system",
                 "content": "You are a helpful assistant that generates questions and answers based on given text."},
                {"role": "user",
                 "content": f"Please generate 3 question-answer pairs based on the following text:\n\n{chunk.content}"}
            ]
            response = await self.chat(messages)

            # Parse the response and add QAs to the chunk
            qas = self.parse_qas(response.content)
            chunk.qas = qas
            return chunk
        except Exception as e:
            raise ApplicationError(f"Failed to add chunk QAs: {str(e)}")

    def parse_qas(self, content: str) -> List[Dict[str, str]]:
        # This is a simple parser. You might need to adjust it based on the actual format of the LLM's response
        qas = []
        lines = content.split('\n')
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                question = lines[i].strip()
                answer = lines[i + 1].strip()
                if question.startswith('Q:'):
                    question = question[2:].strip()
                if answer.startswith('A:'):
                    answer = answer[2:].strip()
                qas.append({"question": question, "answer": answer})
        return qas


    @activity.defn
    async def add_context_to_doc_section(self, doc_section: DocSection, context: Dict[str, any]) -> DocSection:
        try:
            doc_section.content_with_context = f"Context: {' > '.join(context['title_breadcrumbs'])}\nTitle: {context['title']}\n\n{doc_section.content}"
            return doc_section
        except Exception as e:
            raise ApplicationError(
                f"Failed to add context to doc section: {str(e)}")


    @activity.defn
    async def add_doc_section_summary(self, doc_section: DocSection) -> DocSection:
        try:
            messages = [
                {"role": "system",
                 "content": "You are a helpful assistant that summarizes text."},
                {"role": "user",
                 "content": f"Please summarize the following text:\n\n{doc_section.content}"}
            ]
            response = await self.chat(messages)
            doc_section.summary = response.content
            return doc_section
        except Exception as e:
            raise ApplicationError(
                f"Failed to add doc section summary: {str(e)}")


    @activity.defn
    async def add_doc_section_qas(self, doc_section: DocSection) -> DocSection:
        try:
            messages = [
                {"role": "system",
                 "content": "You are a helpful assistant that generates questions and answers based on given text."},
                {"role": "user",
                 "content": f"Please generate 3 question-answer pairs based on the following text:\n\n{doc_section.content}"}
            ]
            response = await self.chat(messages)

            # Parse the response and add QAs to the doc_section
            qas = self.parse_qas(response.content)
            doc_section.qas = qas
            return doc_section
        except Exception as e:
            raise ApplicationError(f"Failed to add doc section QAs: {str(e)}")