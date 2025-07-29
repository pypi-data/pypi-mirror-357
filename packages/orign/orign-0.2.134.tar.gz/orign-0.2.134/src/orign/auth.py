from typing import Dict, Optional

import requests
from pydantic import BaseModel

from orign.config import GlobalConfig


class V1UserProfile(BaseModel):
    email: str
    display_name: Optional[str] = None
    handle: Optional[str] = None
    picture: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    external_id: Optional[str] = None
    actor: Optional[str] = None
    # structure is {"org_id": {"org_name": <name>, "org_role": <role>}}
    organizations: Optional[Dict[str, Dict[str, str]]] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    token: Optional[str] = None


def get_user_profile(api_key: str) -> V1UserProfile:
    config = GlobalConfig.read()
    current_server = config.get_current_server_config()
    if not current_server:
        raise ValueError("No current server config found.")
    url = f"{current_server.server}/v1/users/me"

    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
    response.raise_for_status()

    return V1UserProfile.model_validate(response.json())
