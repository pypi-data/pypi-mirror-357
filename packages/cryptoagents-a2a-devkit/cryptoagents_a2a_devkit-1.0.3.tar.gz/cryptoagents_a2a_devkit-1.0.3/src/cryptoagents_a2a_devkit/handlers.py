from typing import TypedDict, Optional
import httpx
import os
import logging

logger = logging.getLogger(__name__)

class AgentDetail(TypedDict):
    agent_id: str
    description: str
    agent_name: str
    base_url: str # something like http://api.openai.com/v1/chat/completions
    status: str # "running" or "!running"
    avatar_url: Optional[str]

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN", "super-secret") 

def get_router_port() -> int:
    try:
        return int(os.getenv("ROUTER_HOST_PORT") or "12321")
    except ValueError:
        return 0

ROUTER_PORT = get_router_port()
SERVER_MODE = ROUTER_PORT > 0

async def get_agent_detail(
    agent_id: str,
    backend_base_url: str = BACKEND_BASE_URL,
    authorization_token: str = AUTHORIZATION_TOKEN,
) -> Optional[AgentDetail]:
    """
    Get the details of an agent
    """

    authorization_token = authorization_token.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{backend_base_url}/vibe-agent/{agent_id}",
                headers={"Authorization": f"Bearer {authorization_token}"}
            )
        except Exception as e:
            logger.error(f"Error getting agent detail: {e}")
            return None

        if response.status_code == 200:
            data: dict = response.json()
            meta_data: dict = data.get("meta_data", {})

            container: str = data.get("container_name", data.get("container_id", ""))

            if not container:
                return None
            
            port: int = data.get("port", 80)

            base_url = (
                f"{backend_base_url}/agent-router/prompt?url=http://localhost:{ROUTER_PORT}/{container}"
                if SERVER_MODE
                else f"http://{container}:{port}"
            ).rstrip("/")

            return AgentDetail(
                agent_id=agent_id,
                description=data.get("description", ""),
                agent_name=data.get("name", str(agent_id)),
                base_url=base_url,
                status=data.get("status", "unknown"),
                avatar_url=meta_data.get("nft_token_image", None),
            )

        return None
