import os
import re
from typing import Optional

from nebulous import *  # type: ignore
from nebulous.containers.models import (
    V1ContainerRequest,
    V1EnvVar,
    V1ResourceMeta,
    V1ResourceMetaRequest,
    V1VolumeDriver,
    V1VolumePath,
)
from nebulous.errors import RetriableError

from orign.actors.models import Action
from orign.adapters.adapter import Adapter
from orign.adapters.models import (
    V1Adapter,
    V1AdapterRequest,
    V1AdapterUpdateRequest,
    V1LoraParams,
)
from orign.buffers.buffer import ReplayBuffer
from orign.buffers.models import (
    V1ReplayBuffer,
    V1ReplayBufferData,
    V1ReplayBufferRequest,
    V1ReplayBufferStatus,
)
from orign.config import Config
from orign.humans.human import Human
from orign.humans.models import (
    V1ApprovalRequest,
    V1ApprovalResponse,
    V1Feedback,
    V1FeedbackRequest,
    V1FeedbackResponse,
    V1Human,
    V1HumanRequest,
)
from orign.humans.models import V1Feedback as Feedback
from orign.llms.llm import OnlineLLM
from orign.llms.models import (
    V1OnlineLLM,
    V1OnlineLLMRequest,
    V1OnlineLLMs,
    V1OnlineLLMStatus,
)
from orign.trainings.models import (
    V1Training,
    V1TrainingRequest,
    V1TrainingStatus,
    V1TrainingUpdateRequest,
)
from orign.trainings.training import Training
from orign.zoo.trl import TRLRequest
from orign.zoo.vllm import VLLMRequest

from . import actors, adapters, agents, buffers, llms, mcp, tasks, trainings


def find_latest_checkpoint(directory: str) -> Optional[str]:
    """Finds the latest checkpoint in a directory."""
    if not os.path.isdir(directory):
        return None

    checkpoint_dirs = [
        d
        for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d)) and d.startswith("checkpoint-")
    ]

    if not checkpoint_dirs:
        return None

    latest_checkpoint_name = max(
        checkpoint_dirs,
        key=lambda d: int(re.search(r"checkpoint-(\d+)", d).group(1)),  # type: ignore
    )

    return os.path.join(directory, latest_checkpoint_name)


__all__ = [
    "TRLRequest",
    "VLLMRequest",
    "ReplayBuffer",
    "Human",
    "V1ContainerRequest",
    "V1EnvVar",
    "V1ResourceMeta",
    "V1ResourceMetaRequest",
    "V1VolumeDriver",
    "V1VolumePath",
    "V1ReplayBuffer",
    "V1ReplayBufferData",
    "V1ReplayBufferRequest",
    "V1ReplayBufferStatus",
    "V1ApprovalRequest",
    "V1ApprovalResponse",
    "V1Feedback",
    "V1FeedbackRequest",
    "V1FeedbackResponse",
    "V1Human",
    "V1HumanRequest",
    "V1OnlineLLM",
    "V1OnlineLLMRequest",
    "V1OnlineLLMs",
    "V1OnlineLLMStatus",
    "V1Adapter",
    "V1AdapterRequest",
    "V1AdapterUpdateRequest",
    "V1LoraParams",
    "V1Training",
    "V1TrainingRequest",
    "V1TrainingUpdateRequest",
    "Adapter",
    "Training",
    "Config",
    "Feedback",
    "OnlineLLM",
    "Action",
    "V1TrainingStatus",
    "RetriableError",
    "find_latest_checkpoint",
    "adapters",
    "actors",
    "agents",
    "buffers",
    "llms",
    "mcp",
    "tasks",
    "trainings",
]
