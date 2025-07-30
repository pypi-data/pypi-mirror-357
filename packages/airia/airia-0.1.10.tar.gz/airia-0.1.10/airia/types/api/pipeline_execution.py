from typing import Any, AsyncIterator, Dict, Iterator

from pydantic import BaseModel, ConfigDict

from ..sse_messages import SSEMessage


class PipelineExecutionResponse(BaseModel):
    result: str
    report: None
    isBackupPipeline: bool


class PipelineExecutionDebugResponse(BaseModel):
    result: str
    report: Dict[str, Any]
    isBackupPipeline: bool


class PipelineExecutionV1StreamedResponse(BaseModel):
    webSocketUrl: str


class PipelineExecutionV2StreamedResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: Iterator[SSEMessage]


class PipelineExecutionV2AsyncStreamedResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: AsyncIterator[SSEMessage]
