from typing import List, Dict
from temporalio import activity
from temporalio.exceptions import ApplicationError
import json

from spam_check.dto import LLMSpamReport, SpamCheckModel


class LLMActivities:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    @activity.defn
    async def generate_llm_spam_report(self, input: SpamCheckModel) -> LLMSpamReport:
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant tasked with identifying spam content.",
                },
                {
                    "role": "user",
                    "content": f"""Is this a spam submission for the {input.contentType} board on a website for computational modelling and agent based modelling in social and ecological studies: 
                                Title: {input.contentObject.title}
                                Summary: {input.contentObject.summary}
                                Description: {input.contentObject.description}
                                External Url: {input.contentObject.externalUrl}
                                
                                Respond using JSON only with the following structure: {{
                                                                        "is_spam": boolean,
                                                                        "spam_indicators": [list of indicators],
                                                                        "reasoning": "brief explanation",
                                                                        "confidence": float (0-1)
                                                                        }}
                            """,
                },
            ]

            response = await self.llm_client.chat(messages)
            llm_spam_report = LLMSpamReport(**json.loads(response.content))
            return llm_spam_report
        except json.JSONDecodeError:
            raise ApplicationError("Unable to parse the spam check json_data as JSON")
        except Exception as e:
            raise ApplicationError(f"Failed to chat with LLM: {str(e)}")
