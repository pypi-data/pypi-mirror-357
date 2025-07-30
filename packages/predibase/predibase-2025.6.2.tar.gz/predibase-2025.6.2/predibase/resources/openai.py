from typing import Dict, List, TYPE_CHECKING, Union

from openai import OpenAI

from predibase.pql.api import Session

if TYPE_CHECKING:
    from predibase.resources.deployment import Deployment


def openai_compatible_endpoint(session: Session, deployment_ref: Union[str, "Deployment"]) -> str:
    # Check not isinstance(deployment_ref, str) instead of
    #  isinstance(deployment_ref, Deployment) to avoid import error.
    if not isinstance(deployment_ref, str):
        deployment_ref = deployment_ref.name

    return f"https://{session.serving_http_endpoint}/{session.tenant}/deployments/v2/llms/" f"{deployment_ref}/v1"


def create_openai_client(url, session: Session):
    return


class OpenAIBase:
    def __init__(self, client):
        self._pb_client = client
        self._client = None
        self.model = None

    def init_client(self, model: str):
        if self.model != model:
            deployment = self._pb_client.deployments.get(model)
            openai_url = openai_compatible_endpoint(self._pb_client._session, deployment)
            self._client = OpenAI(api_key=self._pb_client._session.token, base_url=openai_url)
            self.model = model


class OpenAIChatCompletion(OpenAIBase):
    def __init__(self, client: OpenAI):
        super().__init__(client)

    def create(self, model: str, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.7):
        self.init_client(model)
        return self._client.chat.completions.create(
            model="",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )


class OpenAICompletion(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(self, model: str, prompt: str, max_tokens: int = 1000, temperature: float = 0.7):
        self.init_client(model)
        return self._client.completions.create(
            model="",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )


class OpenAIEmbeddings(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(self, model: str, input: str):
        self.init_client(model)
        return self._client.embeddings.create(model="", input=input)


class OpenAIChat:
    def __init__(self, client):
        self.completion = OpenAIChatCompletion(client)
