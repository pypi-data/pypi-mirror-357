from typing import TypedDict, Optional
import httpx
import os

class AgentDetail(TypedDict):
    agent_id: str
    description: str
    agent_name: str
    base_url: str # something like http://api.openai.com/v1/chat/completions
    status: str # "running" or "!running"
    avatar_url: Optional[str]

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN", "super-secret") 

async def get_agent_detail(
    agent_id: str,
    backend_base_url: str = BACKEND_BASE_URL,
    authorization_token: str = AUTHORIZATION_TOKEN,
) -> Optional[AgentDetail]:
    """
    Get the details of an agent
    """

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BACKEND_BASE_URL}/vibe-agent/{agent_id}",
                headers={"Authorization": f"Bearer {AUTHORIZATION_TOKEN}"}
            )
        except httpx.HTTPStatusError:
            return None

        if response.status_code == 200:
            data: dict = response.json()
            meta_data: dict = data["meta_data"]

            container: str = data["container_name"] or data["container_id"]
            port: int = data["port"] or 80

            return AgentDetail(
                agent_id=agent_id,
                description=data.get("description", ""),
                agent_name=data.get("name", str(agent_id)),
                base_url=f"http://{container}:{port}/prompt",
                status=data.get("status", "unknown"),
                avatar_url=meta_data.get("nft_token_image", None),
            )

        return None
