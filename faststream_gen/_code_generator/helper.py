# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Helper.ipynb.

# %% auto 0
__all__ = ['logger', 'examples_delimiter', 'set_cwd', 'set_logger_level', 'retry_on_error', 'ensure_openai_api_key_set',
           'add_tokens_usage', 'get_relevant_prompt_examples', 'strip_white_spaces', 'write_file_contents',
           'read_file_contents', 'mock_openai_create', 'download_and_extract_github_repo', 'validate_python_code']

# %% ../../nbs/Helper.ipynb 1
from typing import *
import os
import re
import functools
import logging
from collections import defaultdict
from tempfile import TemporaryDirectory
from pathlib import Path
from contextlib import contextmanager
import unittest.mock
import zipfile
import importlib.util
import time

import typer
import requests
from langchain.schema.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from .._components.logger import get_logger, set_level
from .._components.logger import suppress_timestamps
from faststream_gen._code_generator.constants import (
    OPENAI_KEY_EMPTY_ERROR,
    OPENAI_KEY_NOT_SET_ERROR,
    TOKEN_TYPES,
    MAX_RESTARTS,
    MAX_RETRIES,
    STEP_LOG_DIR_NAMES,
)
from .._components.package_data import get_root_data_path

# %% ../../nbs/Helper.ipynb 3
logger = get_logger(__name__, level=logging.WARNING)

# %% ../../nbs/Helper.ipynb 5
@contextmanager
def set_cwd(cwd_path: Union[Path, str]) -> Generator:
    """Set the current working directory for the duration of the context manager.

    Args:
        cwd_path: The path to the new working directory.

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://github.com/airtai/docstring-gen)
    """
    cwd_path = Path(cwd_path)
    original_cwd = os.getcwd()
    os.chdir(cwd_path)

    try:
        yield
    finally:
        os.chdir(original_cwd)

# %% ../../nbs/Helper.ipynb 7
def set_logger_level(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to set the logger level based on verbosity.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.
    """

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs): # type: ignore
        if ("verbose" in kwargs) and kwargs["verbose"]:
            set_level(logging.INFO)
        else:
            set_level(logging.WARNING)
        return func(*args, **kwargs)

    return wrapper_decorator

# %% ../../nbs/Helper.ipynb 10
def retry_on_error(max_retries: int = MAX_RESTARTS, delay: int = 1):  # type: ignore
    def decorator(func):  # type: ignore
        def wrapper(*args, **kwargs):  # type: ignore
            for i in range(max_retries):
                try:
                    kwargs["attempt"] = i
                    return func(*args, **kwargs)
                except ValueError as e:
                    # Log the error here
                    logger.info(f"Attempt {i} failed. Restarting step.")
                    time.sleep(delay)
                    # Capture exception details here
                    last_exception = e
            return last_exception.args[0], last_exception.args[1]
        return wrapper

    return decorator

# %% ../../nbs/Helper.ipynb 13
def ensure_openai_api_key_set() -> None:
    """Ensure the 'OPENAI_API_KEY' environment variable is set and is not empty.

    Raises:
        KeyError: If the 'OPENAI_API_KEY' environment variable is not found.
        ValueError: If the 'OPENAI_API_KEY' environment variable is found but its value is empty.
    """
    try:
        openai_api_key = os.environ["OPENAI_API_KEY"]
        if openai_api_key == "":
            raise ValueError(OPENAI_KEY_EMPTY_ERROR)
    except KeyError:
        raise KeyError(OPENAI_KEY_NOT_SET_ERROR)

# %% ../../nbs/Helper.ipynb 17
def add_tokens_usage(usage_list: List[Dict[str, int]]) -> Dict[str, int]:
    """Add list of OpenAI "usage" dictionaries by categories defined in TOKEN_TYPES (prompt_tokens, completion_tokens and total_tokens).

    Args:
        usage_list: List of OpenAI "usage" dictionaries


    Returns:
        Dict[str, int]: Dictionary where the keys are TOKEN_TYPES and their values are the sum of OpenAI "usage" dictionaries
    """
    added_tokens: Dict[str, int] = defaultdict(int)
    for usage in usage_list:
        for token_type in TOKEN_TYPES:
            added_tokens[token_type] += usage[token_type]
            
    return added_tokens

# %% ../../nbs/Helper.ipynb 20
examples_delimiter = {
    "description": {
        "start": "==== description.txt starts ====",
        "end": "==== description.txt ends ====",
    },
    "skeleton": {
        "start": "==== app_skeleton.py starts ====",
        "end": "==== app_skeleton.py ends ====",
    },
    "app": {
        "start": "==== app.py starts ====",
        "end": "==== app.py ends ====",
    },
    "test_app": {
        "start": "==== test_app.py starts ====",
        "end": "==== test_app.py ends ====",
    },
}


def _split_text(text: str, delimiter: Dict[str, str]) -> str:
    return text.split(delimiter["start"])[-1].split(delimiter["end"])[0]


def _format_examples(parent_docs_str: List[str]) -> Dict[str, str]:
    """Format and extract examples from parent document.

    Args:
        parent_docs_str (List[str]): A list of parent document strings containing example sections.

    Returns:
        Dict[str, List[str]]: A dictionary with sections as keys and lists of formatted examples as values.
    """
    ret_val = {"description_to_skeleton": "", "skeleton_to_app_and_test": ""}
    for d in parent_docs_str:
        description = _split_text(d, examples_delimiter["description"])
        skeleton = _split_text(d, examples_delimiter["skeleton"])
        app = _split_text(d, examples_delimiter["app"])
        test_app = _split_text(d, examples_delimiter["test_app"])

        ret_val[
            "description_to_skeleton"
        ] += f"\n==== EXAMPLE APP DESCRIPTION ====\n{description}\n\n==== YOUR RESPONSE ====\n\n{skeleton}"
        ret_val[
            "skeleton_to_app_and_test"
        ] += f"\n==== EXAMPLE APP DESCRIPTION ====\n{description}\n\n==== EXAMPLE APP SKELETON ====\n{skeleton}\n==== YOUR RESPONSE ====\n\n### application.py ###\n{app}\n### test.py ###\n{test_app}"

    return ret_val

# %% ../../nbs/Helper.ipynb 22
def get_relevant_prompt_examples(query: str) -> Dict[str, str]:
    """Load the vector database and retrieve the most relevant examples based on the given query for each step.

    Args:
        query: The query for relevance-based document retrieval.

    Returns:
        The dictionary of the most relevant examples for each step.
    """
    db_path = get_root_data_path() / "examples"
    db = FAISS.load_local(db_path, OpenAIEmbeddings()) # type: ignore
    results = db.similarity_search(query, k=3, fetch_k=5)
    results_page_content = [r.page_content for r in results]
    prompt_examples = _format_examples(results_page_content)
    return prompt_examples

# %% ../../nbs/Helper.ipynb 24
def strip_white_spaces(description: str) -> str:
    """Remove and strip excess whitespaces from a given description

    Args:
        description: The description string to be processed.

    Returns:
        The cleaned description string.
    """
    pattern = re.compile(r"\s+")
    return pattern.sub(" ", description).strip()

# %% ../../nbs/Helper.ipynb 26
def write_file_contents(output_file: str, contents: str) -> None:
    """Write the given contents to the specified output file.

    Args:
        output_file: The path to the output file where the contents will be written.
        contents: The contents to be written to the output file.

    Raises:
        OSError: If there is an issue while attempting to save the file.
    """
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(contents)

    except OSError as e:
        raise OSError(
            f"Error: Failed to save file at '{output_file}' due to: '{e}'. Please ensure that the specified 'output_path' is valid and that you have the necessary permissions to write files to it."
        )

# %% ../../nbs/Helper.ipynb 28
def read_file_contents(output_file: str) -> str:
    """Read and return the contents from the specified file.

    Args:
        output_file: The path to the file to be read.

    Returns:
        The contents of the file as string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: The file '{output_file}' does not exist. Please ensure that the specified 'output_path' is valid and that you have the necessary permissions to access it."
        )

# %% ../../nbs/Helper.ipynb 31
@contextmanager
def mock_openai_create(test_response: str) -> Generator[None, None, None]:
    mock_choices = {
        "choices": [{"message": {"content": test_response}}],
        "usage": { 
            "prompt_tokens": 129,
            "completion_tokens": 1,
            "total_tokens": 130
        },
    }

    with unittest.mock.patch("openai.ChatCompletion") as mock:
        mock.create.return_value = mock_choices
        yield

# %% ../../nbs/Helper.ipynb 33
def _fetch_content(url: str) -> requests.models.Response: # type: ignore
    """Fetch content from a URL using an HTTP GET request.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        Response: The response object containing the content and HTTP status.

    Raises:
        requests.exceptions.Timeout: If the request times out.
        requests.exceptions.RequestException: If an error occurs during the request.
    """
    attempt = 0
    while attempt < 4:
        try:
            response = requests.get(url, timeout=50)
            response.raise_for_status()  # Raises an exception for HTTP errors
            return response
        except requests.exceptions.Timeout:
            if attempt == 3:  # If this was the fourth attempt, raise the Timeout exception
                raise requests.exceptions.Timeout(
                    "Request timed out. Please check your internet connection or try again later."
                )
            time.sleep(1)  # Sleep for one second before retrying
            attempt += 1
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"An error occurred: {e}")

# %% ../../nbs/Helper.ipynb 35
@contextmanager
def download_and_extract_github_repo(url: str) -> Generator[Path, None, None]:
    with TemporaryDirectory() as d:
        try:
            input_path = Path(f"{d}/archive.zip")
            extrated_path = Path(f"{d}/extrated_path")
            extrated_path.mkdir(parents=True, exist_ok=True)

            response = _fetch_content(url)

            with open(input_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(input_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    zip_ref.extract(member, extrated_path)

            yield extrated_path

        except Exception as e:
            fg = typer.colors.RED
            typer.secho(f"Unexpected internal error: {e}", err=True, fg=fg)
            raise typer.Exit(code=1)

# %% ../../nbs/Helper.ipynb 37
def validate_python_code(file_name: str, **kwargs: Dict[str, Any]) -> List[str]:
    """Validate and report errors in the provided Python code.

    Args:
        file_name: Python file to validate

    Returns:
        A list of error messages encountered during validation. If no errors occur, an empty list is returned.
    """
    try:
        # Import the module using importlib
        spec = importlib.util.spec_from_file_location("tmp_module", file_name)
        module = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(module)  # type: ignore

    except Exception as e:
        return [f"{type(e).__name__}: {e}"]

    return []
