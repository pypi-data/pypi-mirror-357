from sparkflintcli.core.services.auth_service import AuthService
from sparkflintcli.core.services.config_service import ConfigService
from sparkflintcli.core.models.pipeline_model import Pipeline
from sparkflintcli.core.context import session

config_service = ConfigService()
auth_service = AuthService()

from sparkflintcli.core.utils.token_cache import (
    load_token,
)


def get_pipelines() -> list[Pipeline]:
    origin = config_service.get_origin()
    token = load_token()
    url = f"{origin}/pipelines"
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return [Pipeline.from_dict(p) for p in data.get("pipelines", [])]


def get_pipeline_by_id(pipeline_id: str) -> Pipeline:
    origin = config_service.get_origin()
    token = load_token()
    url = f"{origin}/pipelines/{pipeline_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(url, headers=headers)
    response.raise_for_status()
    return Pipeline.from_dict(response.json())


def get_pipeline_by_name(name: str) -> Pipeline | None:
    pipelines = get_pipelines()
    for pipeline in pipelines:
        if pipeline.name.lower() == name.lower():
            return get_pipeline_by_id(pipeline.id)
    return None
