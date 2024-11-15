from dataclasses import asdict
import requests
from langchain_ollama import ChatOllama
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_ollama import ChatOllama
from openai import OpenAI
import instructor
from pydantic import BaseModel
import json
import ollama
from temporalio.exceptions import ApplicationError

from spam_check.dto import SpamReport


class ComsesClient:
    def __init__(self, comses_url: str, comses_api_key: str):
        self.comses_url = comses_url
        self.headers = {"X-API-Key": comses_api_key, "Content-Type": "application/json"}

    def get_latest_batch(self):
        response = requests.get(
            f"{self.comses_url}/api/spam/get-latest-batch/", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def send_spam_report(self, report: SpamReport) -> bool:
        url = f"{self.comses_url}/api/spam/update/"
        data = asdict(report)

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        return response.status_code == 200


class OllamaClient:
    def __init__(self, base_url: str):
        self.client = ollama.Client(host=base_url)

    async def chat(self, model: str, messages: List[Dict[str, str]]) -> str:
        ai_msg = self.client.chat(model, messages, stream=False)
        return ai_msg


class OllamaJSONClient:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url

    async def reply_with_json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        try:
            result = response.json()
            json_response = json.loads(result["message"]["content"])
            return json_response
        except json.JSONDecodeError:
            raise ValueError("The response from Ollama was not valid JSON.")

    def generate(self, prompt: str, response_model: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/generate"

        system_prompt = f"""You are a helpful AI assistant. 
        Respond to the user's request with a JSON object matching this structure:
        {json.dumps(response_model, indent=2)}
        Ensure your response is valid JSON."""

        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:",
            "stream": False,
            "format": "json",
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        try:
            result = response.json()
            json_response = json.loads(result["response"])
            return json_response
        except json.JSONDecodeError:
            raise ValueError("The response from Ollama was not valid JSON.")


class JsonChatOllamaClient:
    def __init__(self, base_url: str, model: str):
        self.llm = ChatOllama(model=model, base_url=base_url, format="json")

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        response = await self.llm.ainvoke(messages)
        return response


class InstructorOllamaClient:
    def __init__(
        self, model: str = "llama3.2", base_url: str = "http://localhost:11434/v1"
    ):
        self.client = instructor.from_openai(
            OpenAI(
                base_url=base_url,
                api_key="ollama",  # required, but unused
            ),
            mode=instructor.Mode.JSON,
        )
        self.model = model

    def chat(self, messages: List[Dict[str, str]], response_model: BaseModel) -> Any:
        model = self.client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            max_retries=5,
            messages=messages,
        )
        return model
