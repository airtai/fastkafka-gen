# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/App_Generator.ipynb.

# %% auto 0
__all__ = ['logger', 'generate_app']

# %% ../../nbs/App_Generator.ipynb 1
from typing import *
import time
import json
from tempfile import TemporaryDirectory
from pathlib import Path

from yaspin import yaspin

from .._components.logger import get_logger
from .helper import CustomAIChat, ValidateAndFixResponse, write_file_contents, read_file_contents
from .prompts import APP_GENERATION_PROMPT
from .constants import ASYNC_API_SPEC_FILE_NAME, APPLICATION_FILE_NAME

# %% ../../nbs/App_Generator.ipynb 3
logger = get_logger(__name__)

# %% ../../nbs/App_Generator.ipynb 5
def _validate_response(response: str) -> List[str]:
    return []

# %% ../../nbs/App_Generator.ipynb 8
def generate_app(code_gen_directory: str) -> str:
    """Generate code for the new FastKafka app from the validated plan

    Args:
        code_gen_directory: The directory containing the generated files.

    Returns:
        The total token used to generate the FastKafka code
    """
    # TODO: Validate the generated code
    with yaspin(
        text="Generating FastKafka app...", color="cyan", spinner="clock"
    ) as sp:
        spec_file_name = f"{code_gen_directory}/{ASYNC_API_SPEC_FILE_NAME}"
        asyncapi_spec = read_file_contents(spec_file_name)

        app_generator = CustomAIChat(
            params={
                "temperature": 0.5,
            },
            user_prompt=APP_GENERATION_PROMPT,
        )
        app_validator = ValidateAndFixResponse(app_generator, _validate_response)
        validated_app, total_tokens = app_validator.fix(asyncapi_spec)

        output_file = f"{code_gen_directory}/{APPLICATION_FILE_NAME}"
        write_file_contents(output_file, validated_app)

        sp.text = ""
        sp.ok(f" ✔ FastKafka app generated and saved at: {output_file}")
        return total_tokens
