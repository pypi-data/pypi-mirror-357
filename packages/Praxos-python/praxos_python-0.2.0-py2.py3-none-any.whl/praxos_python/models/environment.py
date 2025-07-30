import os
from typing import List, Dict, Any, Type, Union
from pydantic import BaseModel
from .source import SyncSource
from ..exceptions import APIError
from .context import Context
from ..types.message import Message

ACCEPTABLE_SOURCE_EXTENSIONS_TO_CONTENT_TYPE = {
    "pdf": "application/pdf",
    "json": "application/json",
}

class BaseEnvironmentAttributes:
    """
    Base attributes for an Environment resource.
    Ensures consistent initialization with core fields.
    """
    def __init__(self, id: str, name: str, created_at: str, description: str, **kwargs):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.description = description

class SyncEnvironment(BaseEnvironmentAttributes):
    """Represents a synchronous Environment resource."""
    def __init__(self, client, id: str, name: str, created_at: str, description: str, **data: Any):
        super().__init__(id=id, name=name, created_at=created_at, description=description, **data)
        self._client = client

    def __repr__(self) -> str:
        return f"<SyncEnvironment id='{self.id}' name='{self.name}'>"

    def get_context(self, query: str, top_k: int = 1) -> Context|List[Context]:
        """Gets context for an LLM."""
        # print(f"SDK (Sync Env: {self.name}): API to get context for query '{query}'...") # For debugging
        response_data = self._client._request(
            "POST", f"/search", json_data={"query": query, "top_k": top_k, "environment_id": self.id}
        )

        contexts = []
        for context in response_data["hits"]:
            contexts.append(Context(score=context["score"], data=context["data"], sentence=context["sentence"]))

        if top_k == 1:
            return contexts[0]
        else:
            return contexts
    
    def extract_items(self, schema: Union[str, Type[BaseModel]]):
        """Extracts items from a schema."""
        schema_name = schema if isinstance(schema, str) else schema.__name__

        response_data = self._client._request("POST", f"/extract", json_data={"label": schema_name, "environment_id": self.id})
        return response_data.get("items", [])
        

    def add_conversation(self, messages: List[Message|Dict[str, str]], name: str=None, description: str=None) -> SyncSource:
        """Adds a conversation source."""
        if len(messages) == 0:
            raise ValueError("Messages must be a non-empty list")
        
        messages = [Message.from_dict(message) if isinstance(message, dict) else message for message in messages]
        
        payload = {
            "messages": [message.to_dict() for message in messages],
            "description": description
        }

        if name:
            payload["name"] = name

        response_data = self._client._request("POST", f"/sources", params={"type": "conversation", "environment_id": self.id}, json_data=payload)
        return SyncSource(client=self._client, **response_data)

    def add_file(self, path: str, name: str=None, description: str=None) -> SyncSource:
        """Adds a file source."""
        global ACCEPTABLE_SOURCE_EXTENSIONS_TO_CONTENT_TYPE

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        file_extension = path.split('.')[-1]
        if file_extension not in ACCEPTABLE_SOURCE_EXTENSIONS_TO_CONTENT_TYPE:
            raise ValueError(f"File extension {file_extension} is not supported. Supported extensions are: {', '.join(ACCEPTABLE_SOURCE_EXTENSIONS_TO_CONTENT_TYPE.keys())}")
        
        if name is None:
            name = '.'.join(os.path.basename(path).split('.')[:-1])

        try:
            with open(path, 'rb') as f:
                files = {'file': (name, f, ACCEPTABLE_SOURCE_EXTENSIONS_TO_CONTENT_TYPE[file_extension])}
                form_data = {"type": "file", "name": name, "description": description}
                response_data = self._client._request(
                    "POST", f"sources", params={"environment_id": self.id}, data=form_data, files=files
                )
            return SyncSource(client=self._client, **response_data)
        except FileNotFoundError:
            raise ValueError(f"File not found: {path}")
        except Exception as e:
            raise APIError(status_code=0, message=f"Sync file upload failed: {str(e)}") from e
        
    def add_business_data(self, data: Dict[str, Any], name: str=None, description: str=None) -> SyncSource:
        """Adds business data source."""
        payload = {
            "data": data,
            "name": name,
            "description": description
        }

        response_data = self._client._request("POST", f"/sources", params={"environment_id": self.id}, json_data=payload)
        return SyncSource(client=self._client, **response_data)
    
    def get_sources(self) -> List[SyncSource]:
        """Gets all sources for the environment."""
        response_data = self._client._request("GET", f"/sources", params={"environment_id": self.id})
        return [SyncSource(client=self._client, **source) for source in response_data]

    def get_source(self, id: str=None, name: str=None) -> SyncSource:
        """Gets a source for the environment."""
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        
        if id:
            response_data = self._client._request("GET", f"/sources", params={"environment_id": self.id, "id": id})
        else:
            response_data = self._client._request("GET", f"/sources", params={"environment_id": self.id, "name": name})

        return SyncSource(client=self._client, **response_data)
