import os

import llama_index

from llama_index import (
    LLMPredictor,
    GPTTreeIndex,
    Document,
    GPTSimpleVectorIndex,
    SimpleDirectoryReader,
    RefinePrompt,
    QuestionAnswerPrompt,
    GPTListIndex,
    PromptHelper,
)
from pathlib import Path
from tqdm import tqdm
import re
from llama_index.composability import ComposableGraph
from IPython.display import Markdown, display
import json
from llama_index import Prompt
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Type

import logging
import sys

def compact_text_chunks(self, prompt: Prompt, text_chunks: List[str]) -> List[str]:
    logging.debug("Compacting text chunks...🚀🚀🚀")
    combined_str = [c.strip() for c in text_chunks if c.strip()]
    combined_str = [f"[{index+1}] {c}" for index, c in enumerate(combined_str)]
    combined_str = "\n\n".join(combined_str)
    # resplit based on self.max_chunk_overlap
    text_splitter = self.get_text_splitter_given_prompt(prompt, 1, padding=1)
    return text_splitter.split_text(combined_str)
