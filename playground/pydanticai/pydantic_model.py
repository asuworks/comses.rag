import os
from typing import List, cast

import logfire
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from sqlalchemy.dialects.postgresql import JSONB

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')


class Memories(BaseModel):
	category: str
	memories: List[str]

model = cast(KnownModelName, os.getenv('PYDANTIC_AI_MODEL', 'ollama:llama3.1'))
print(f'Using model: {model}')
agent = Agent(model, result_type=Memories, system_prompt=(
        "You will be given a text message from the user. Extract any information about the user worth storing in the long-term memory. Extract any info about the owner or his preferences or relations or hobbies. Reformulate individual pieces of information as atomic, independent memories. Disambiguate, if necessary. "
    ),retries=3)

if __name__ == '__main__':
	result = agent.run_sync('Remind me to call my wife Anastasia at +123456789987654321 and congratulate her with her birthday, which is today!')
	print(result.data)
	print(result.usage())