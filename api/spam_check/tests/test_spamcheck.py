import asyncio
import aiohttp
from pydantic import BaseModel
from typing import Literal

ContentType = Literal["event", "job", "codebase", "user"]


class SpamCheckInput(BaseModel):
    type: ContentType
    text: str


async def send_spam_check_requests(base_url: str, api_key: str):
    async with aiohttp.ClientSession() as session:
        tasks = []
        inputs = [
            ("event", "Join our free webinar on AI in computational modeling!"),
            ("job", "Remote position: Senior Agent-Based Modeler needed ASAP!!!"),
            (
                "codebase",
                "Check out my new social simulation framework - 100% efficient!",
            ),
            ("user", "Hi, I'm a researcher interested in ecological modeling :)"),
            (
                "event",
                "URGENT: Last chance to register for the conference - 24 HOURS LEFT!",
            ),
            ("job", "Earn $$$$ working from home as a part-time modeler!"),
            (
                "codebase",
                "Download my codebase now - GUARANTEED to speed up your simulations by 500%",
            ),
            ("user", "Hello dear friend, I have a business proposition for you..."),
            ("event", "FREE WORKSHOP: Learn to create unbeatable agent-based models!"),
            (
                "job",
                "HIRING NOW: No experience needed, become a modeling expert overnight!",
            ),
        ]

        for content_type, text in inputs:
            input_data = SpamCheckInput(type=content_type, text=text)
            task = asyncio.create_task(
                send_request(session, base_url, api_key, input_data)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results, 1):
            print(f"Request {i}:")
            print(f"Input: {inputs[i-1]}")
            print(f"Result: {result}")
            print()


async def send_request(session, base_url, api_key, input_data):
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    try:
        async with session.post(
            f"{base_url}/spamcheck", headers=headers, json=input_data.dict()
        ) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        return {"error": f"Request failed: {str(e)}"}


async def main():
    base_url = "http://{remote-server-ip}:8000"  # Replace with your actual base URL
    api_key = "secret-api-key"  # Replace with your actual API key
    await send_spam_check_requests(base_url, api_key)


if __name__ == "__main__":
    asyncio.run(main())
