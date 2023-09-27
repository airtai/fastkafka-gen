# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/App_Skeleton_Generator.ipynb.

# %% auto 0
__all__ = ['logger', 'generate_app_skeleton']

# %% ../../nbs/App_Skeleton_Generator.ipynb 1
from typing import *
import time
import json
from pathlib import Path

from yaspin import yaspin

from .._components.logger import get_logger
from .chat import CustomAIChat, ValidateAndFixResponse
from faststream_gen._code_generator.helper import (
    write_file_contents,
    validate_python_code,
    retry_on_error,
)
from .prompts import APP_SKELETON_GENERATION_PROMPT
from faststream_gen._code_generator.constants import (
    STEP_LOG_DIR_NAMES,
    APPLICATION_FILE_PATH,
    LOGS_DIR_NAME
)

# %% ../../nbs/App_Skeleton_Generator.ipynb 3
logger = get_logger(__name__)

# %% ../../nbs/App_Skeleton_Generator.ipynb 5
@retry_on_error()  # type: ignore
def _generate(
    model: str,
    prompt: str,
    app_description_content: str,
    total_usage: List[Dict[str, int]],
    output_directory: str,
    **kwargs,
) -> Tuple[str, List[Dict[str, int]]]:
    app_generator = CustomAIChat(
        params={
            "temperature": 0.2,
        },
        model=model,
        user_prompt=prompt,
        #         semantic_search_query=app_description_content,
    )
    app_validator = ValidateAndFixResponse(app_generator, validate_python_code)
    log_dir_path = Path(output_directory) / LOGS_DIR_NAME
    validator_result = app_validator.fix(
        app_description_content,
        total_usage,
        STEP_LOG_DIR_NAMES["skeleton"],
        str(log_dir_path),
        **kwargs,
    )

    try:
        validated_app_skeleton, total_usage = validator_result
        return validated_app_skeleton, total_usage, True
    except ValueError as e:
        return validator_result

# %% ../../nbs/App_Skeleton_Generator.ipynb 8
def generate_app_skeleton(
    validated_description: str,
    output_directory: str,
    model: str,
    total_usage: List[Dict[str, int]],
    relevant_prompt_examples: str,
) -> List[Dict[str, int]]:
    """Generate skeleton code for the new FastStream app from the application description

    Args:
        code_gen_directory: The directory containing the generated files.
        total_usage: list of token usage.
        relevant_prompt_examples: Relevant examples to add in the prompts.

    Returns:
        The total token used to generate the FastStream code
    """
    logger.info("==== Description to Skeleton Generation ====")
    with yaspin(
        text=f"Generating FastStream app skeleton code (usually takes around 15 to 45 seconds)...",
        color="cyan",
        spinner="clock",
    ) as sp:
        prompt = APP_SKELETON_GENERATION_PROMPT.replace(
            "==== RELEVANT EXAMPLES GOES HERE ====", f"\n{relevant_prompt_examples}"
        )

        validated_app_skeleton, total_usage, is_valid_skeleton_code = _generate(
            model, prompt, validated_description, total_usage, output_directory
        )

        output_file = Path(output_directory) / APPLICATION_FILE_PATH
        output_file.parent.mkdir(parents=True, exist_ok=True)
        write_file_contents(str(output_file), validated_app_skeleton)

        sp.text = ""
        if is_valid_skeleton_code:
            message = f" ✔ FastStream app skeleton code generated."
        else:
            message = " ✘ Error: Failed to generate a valid application skeleton code."
            sp.color = "red"

        sp.ok(message)
        return total_usage, is_valid_skeleton_code
