import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow

from shared.activities.llm_activities import LLMActivities
from shared.activities.text_activities import TextActivities
from shared.activities.vector_store_activities import VectorStoreActivities
from shared.const import OLLAMA_EMBEDDING_TASK_QUEUE, \
    VECTOR_STORE_TASK_QUEUE
from shared.models.base import ModelDoc
from shared.models.vector import VectorPoint

EMBEDDING_BATCH_SIZE = 10

@workflow.defn
class ComputeEmbeddingsWorkflow:
    @workflow.run
    async def run(self, texts: List[str], start_index: int = 0, previous_results: List[List[float]] = None) -> List[List[float]]:
        if previous_results is None:
            previous_results = []

        end_index = min(start_index + EMBEDDING_BATCH_SIZE, len(texts))
        current_batch = texts[start_index:end_index]

        embedding_tasks = [
            workflow.execute_activity(
                LLMActivities.compute_embedding,
                args=[text],
                task_queue=OLLAMA_EMBEDDING_TASK_QUEUE,
                start_to_close_timeout=timedelta(seconds=10)
            ) for text in current_batch
        ]

        batch_results = await asyncio.gather(*embedding_tasks)
        all_results = previous_results + batch_results

        if end_index < len(texts):
            # There are more texts to process
            return await workflow.continue_as_new(args=[texts, end_index, all_results])
        else:
            # This is the last batch, return all results
            return all_results



@workflow.defn
class ComputeAndUpsertModelDocEmbeddingsWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        """
                Goal of the workflow is to populate the following Qdrant Collections:

                MVP:
                Chunks -> chunk.content_with_context is embedded

                # TODO: Enhance RAG
                ModelDocSummaryChunks -> ModelDoc.summary is chunked and embedded

                DocSectionSummaryChunksLevel1-6 -> DocSection.summary is chunked and embedded at DocSection levels 1-6

                ChunkQuestions -> ChunkQuestions are embedded
                ChunkAnswers -> ChunkAnswers are embedded

                DocSectionQuestions -> DocSectionQuestions are embedded
                DocSectionAnswers -> DocSectionAnswers are embedded

                @param model_doc:
                @return:
        """

        workflow.logger.info(
            "Starting ComputeAndUpsertModelDocEmbeddingsWorkflow")

        # Execute child workflows in parallel
        tasks = [
            asyncio.create_task(workflow.execute_child_workflow(
                PopulateChunksCollectionWorkflow.run, args=[model_doc])),

            asyncio.create_task(workflow.execute_child_workflow(
                PopulateModelDocSummaryChunksCollectionWorkflow.run,
                args=[model_doc])),

            # Populate DocSectionSummaryChunksLevel1
            asyncio.create_task(workflow.execute_child_workflow(
                PopulateDocSectionSummaryChunksCollectionWorkflow.run, args=[model_doc, 1])),

            # Populate DocSectionSummaryChunksLevel2
            # asyncio.create_task(workflow.execute_child_workflow(
            # 	PopulateDocSectionSummaryChunksCollectionWorkflow.run,
            # 	args=[model_doc, 2])),

            # Populate DocSectionSummaryChunksLevel3
            # asyncio.create_task(workflow.execute_child_workflow(
            # 	PopulateDocSectionSummaryChunksCollectionWorkflow.run,
            # 	args=[model_doc, 3])),

            # Populate DocSectionSummaryChunksLevel4
            # asyncio.create_task(workflow.execute_child_workflow(
            # 	PopulateDocSectionSummaryChunksCollectionWorkflow.run,
            # 	args=[model_doc, 4])),

            # Populate DocSectionSummaryChunksLevel5
            # asyncio.create_task(workflow.execute_child_workflow(
            # 	PopulateDocSectionSummaryChunksCollectionWorkflow.run,
            # 	args=[model_doc, 5])),

            # Populate DocSectionSummaryChunksLevel6
            # asyncio.create_task(workflow.execute_child_workflow(
            # 	PopulateDocSectionSummaryChunksCollectionWorkflow.run,
            # 	args=[model_doc, 6])),


            asyncio.create_task(workflow.execute_child_workflow(
                PopulateChunkQuestionsCollectionWorkflow.run, args=[model_doc])),
            asyncio.create_task(workflow.execute_child_workflow(
                PopulateChunkAnswersCollectionWorkflow.run, args=[model_doc])),
            asyncio.create_task(workflow.execute_child_workflow(
                PopulateDocSectionQuestionsCollectionWorkflow.run, args=[model_doc])),
            asyncio.create_task(workflow.execute_child_workflow(
                PopulateDocSectionAnswersCollectionWorkflow.run, args=[model_doc])),
        ]

        # Wait for all child workflows to complete
        await asyncio.gather(*tasks)

        workflow.logger.info(
            "ComputeAndUpsertModelDocEmbeddingsWorkflow completed.")


@workflow.defn
class PopulateChunksCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        all_points = []
        for doc_section in model_doc.doc_sections:
            chunk_contents = [chunk.content_with_context for chunk in
                              doc_section.chunks]
            embeddings = await workflow.execute_child_workflow(
                ComputeEmbeddingsWorkflow.run,
                args=[chunk_contents]
            )
            points = [
                VectorPoint(
                    id=chunk.id,
                    payload={
                        "doc_section_id": chunk.doc_section_id,
                        "type": chunk.type,
                        "content": chunk.content,
                        "model_id": model_doc.model_id
                    },
                    vector=embedding
                )
                for chunk, embedding in zip(doc_section.chunks, embeddings)
            ]
            all_points.extend(points)

        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["Chunks", all_points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )


@workflow.defn
class PopulateModelDocSummaryChunksCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        chunked_summary = await workflow.execute_activity(
            TextActivities.chunk_text,
            args=[model_doc.summary],
            start_to_close_timeout=timedelta(seconds=10)
        )
        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[chunked_summary]
        )
        points = [
            VectorPoint(
                id=f"model_doc_summary_{i}",
                payload={"summary": chunk, "model_id": model_doc.model_id},
                vector=embedding
            )
            for i, (chunk, embedding) in
            enumerate(zip(chunked_summary, embeddings))
        ]
        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["ModelDocSummaryChunks", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )


@workflow.defn
class PopulateDocSectionSummaryChunksCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc, level: int):
        # Get doc sections at the specified level
        doc_sections = [doc_section for doc_section in model_doc.doc_sections if
                        doc_section.level == level]

        # Chunk summaries for each doc section
        chunked_summaries_tasks = [
            workflow.execute_activity(
                TextActivities.chunk_text,
                args=[doc_section.summary],
                start_to_close_timeout=timedelta(seconds=10)
            ) for doc_section in doc_sections
        ]
        chunked_summaries: List[List[str]] = await asyncio.gather(*chunked_summaries_tasks)

        # Compute embeddings for all chunks
        all_chunks = [chunk for summary_chunks in chunked_summaries for chunk in summary_chunks]
        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[all_chunks]
        )

        # Create points, preserving the link between chunks and doc_section.id
        points = []
        embedding_index = 0
        for doc_section, summary_chunks in zip(doc_sections, chunked_summaries):
            for chunk_index, chunk in enumerate(summary_chunks):
                points.append(
                    VectorPoint(
                        id=f"doc_section_summary_level{level}_{doc_section.id}_{chunk_index}",
                        payload={
                            "summary": chunk,
                            "level": str(level),
                            "model_id": model_doc.model_id,
                            "doc_section_id": doc_section.id
                        },
                        vector=embeddings[embedding_index]
                    )
                )
                embedding_index += 1

        # Upsert points to vector store
        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=[f"DocSectionSummaryChunksLevel{level}", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )

@workflow.defn
class PopulateChunkQuestionsCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        # Collect questions with their associated chunk and doc_section IDs
        questions_data = [
            {
                "question": qa.question,
                "chunk_id": qa.chunk_id,
                "doc_section_id": doc_section.id,
                "qa_id": qa.id
            }
            for doc_section in model_doc.doc_sections
            for chunk in doc_section.chunks
            for qa in chunk.qas
        ]

        # Extract just the questions for embedding
        questions = [data["question"] for data in questions_data]

        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[questions]
        )

        points = [
            VectorPoint(
                id=f"chunk_question_{data['chunk_id']}_{data['qa_id']}",
                payload={
                    "qa_id": data["qa_id"],
                    "model_id": model_doc.model_id,
                    "doc_section_id": data["doc_section_id"],
                    "chunk_id": data["chunk_id"],
                    "question": data["question"]
                },
                vector=embedding
            )
            for data, embedding in zip(questions_data, embeddings)
        ]

        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["ChunkQuestions", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )

@workflow.defn
class PopulateChunkAnswersCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        # Collect answers with their associated chunk and doc_section IDs
        answers_data = [
            {
                "answer": qa.answer,
                "chunk_id": qa.chunk_id,
                "doc_section_id": doc_section.id,
                "qa_id": qa.id
            }
            for doc_section in model_doc.doc_sections
            for chunk in doc_section.chunks
            for qa in chunk.qas
        ]

        # Extract just the answers for embedding
        answers = [data["answer"] for data in answers_data]

        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[answers]
        )

        points = [
            VectorPoint(
                id=f"chunk_answer_{data['chunk_id']}_{data['qa_id']}",
                payload={
                    "qa_id": data["qa_id"],
                    "model_id": model_doc.model_id,
                    "doc_section_id": data["doc_section_id"],
                    "chunk_id": data["chunk_id"],
                    "answer": data["answer"]
                },
                vector=embedding
            )
            for data, embedding in zip(answers_data, embeddings)
        ]

        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["ChunkAnswers", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )

@workflow.defn
class PopulateDocSectionQuestionsCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        # Collect questions with their associated doc_section IDs
        questions_data = [
            {
                "question": qa.question,
                "doc_section_id": doc_section.id,
                "qa_id": qa.id
            }
            for doc_section in model_doc.doc_sections
            for qa in doc_section.qas
        ]

        # Extract just the questions for embedding
        questions = [data["question"] for data in questions_data]

        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[questions]
        )

        points = [
            VectorPoint(
                id=f"doc_section_question_{data['doc_section_id']}_{data['qa_id']}",
                payload={
                    "qa_id": data["qa_id"],
                    "model_id": model_doc.model_id,
                    "doc_section_id": data["doc_section_id"],
                    "question": data["question"]
                },
                vector=embedding
            )
            for data, embedding in zip(questions_data, embeddings)
        ]

        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["DocSectionQuestions", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )

@workflow.defn
class PopulateDocSectionAnswersCollectionWorkflow:
    @workflow.run
    async def run(self, model_doc: ModelDoc):
        # Collect answers with their associated doc_section IDs
        answers_data = [
            {
                "answer": qa.answer,
                "doc_section_id": doc_section.id,
                "qa_id": qa.id
            }
            for doc_section in model_doc.doc_sections
            for qa in doc_section.qas
        ]

        # Extract just the answers for embedding
        answers = [data["answer"] for data in answers_data]

        embeddings = await workflow.execute_child_workflow(
            ComputeEmbeddingsWorkflow.run,
            args=[answers]
        )

        points = [
            VectorPoint(
                id=f"doc_section_answer_{data['doc_section_id']}_{data['qa_id']}",
                payload={
                    "qa_id": data["qa_id"],
                    "model_id": model_doc.model_id,
                    "doc_section_id": data["doc_section_id"],
                    "answer": data["answer"]
                },
                vector=embedding
            )
            for data, embedding in zip(answers_data, embeddings)
        ]

        await workflow.execute_activity(
            VectorStoreActivities.upsert_metadata_vector_points,
            args=["DocSectionAnswers", points],
            task_queue=VECTOR_STORE_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=10)
        )