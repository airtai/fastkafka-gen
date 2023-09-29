# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/App_And_Test_Generator.ipynb.

# %% auto 0
__all__ = ['logger', 'generate_app_and_test']

# %% ../../nbs/App_And_Test_Generator.ipynb 1
from typing import *
import time
import importlib.util
from tempfile import TemporaryDirectory
from pathlib import Path
import platform
from collections import defaultdict
import subprocess  # nosec: B404: Consider possible security implications associated with the subprocess module.

from yaspin import yaspin

from .._components.logger import get_logger
from .chat import CustomAIChat, ValidateAndFixResponse
from faststream_gen._code_generator.helper import (
    write_file_contents,
    read_file_contents,
    validate_python_code,
    retry_on_error,
    set_cwd
)
from .prompts import APP_AND_TEST_GENERATION_PROMPT
from faststream_gen._code_generator.constants import (
    APPLICATION_FILE_PATH,
    TEST_FILE_PATH,
    STEP_LOG_DIR_NAMES,
    LOGS_DIR_NAME,
)

from .constants import OpenAIModel

# %% ../../nbs/App_And_Test_Generator.ipynb 3
logger = get_logger(__name__)

# %% ../../nbs/App_And_Test_Generator.ipynb 5
_code_fix_prompt = """
Your task is to correct the provided code. Your response should consist solely of valid Python code. You must follow the below rules while responding:

- Do not include explanations or wrap your response in ```python tags.
"""

def _fix_generated_code(s: str) -> str:
    ai = CustomAIChat(
        params={
            "temperature": 0.2,
        },
        model=OpenAIModel.gpt3.value,
        user_prompt=_code_fix_prompt,
    )
    response, usage = ai(s) # todo: add this usage to total usage
    return str(response)

# %% ../../nbs/App_And_Test_Generator.ipynb 7
def _split_app_and_test_code(response: str) -> Tuple[str, str]:
    app_code, test_code = response.split("### application.py ###")[1].split(
        "### test.py ###"
    )
    return app_code, test_code


def _validate_response(
    response: str, output_directory: str, **kwargs: Dict[str, Any]
) -> Tuple[List[str], str]:
    try:
        app_code, test_code = _split_app_and_test_code(response)
    except (IndexError, ValueError) as e:
        return (
            ["Please add ### application.py ### and ### test.py ### in your response"],
            response,
        )

    app_code = app_code.replace("### application.py ###", "").strip()
    test_code = test_code.strip()

    fixed_app_code = _fix_generated_code(app_code)
    fixed_test_code = _fix_generated_code(test_code).replace("from application import ", "from app.application import ")

    app_file_name = Path(output_directory) / APPLICATION_FILE_PATH
    test_file_name = Path(output_directory) / TEST_FILE_PATH

    write_file_contents(str(app_file_name), fixed_app_code)
    write_file_contents(str(test_file_name), fixed_test_code)

    with set_cwd(output_directory):
        cmd = ["pytest", "--tb=short"]
        # nosemgrep: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
        p = subprocess.run(  # nosec: B602, B603 subprocess call - check for execution of untrusted input.
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True if platform.system() == "Windows" else False,
        )
    if p.returncode != 0:
        response = f"### application.py ###\n{fixed_app_code}\n\n### test.py ###\n{fixed_test_code}\n"
        return ([str(p.stdout.decode("utf-8"))], response)

    return ([], "")

# %% ../../nbs/App_And_Test_Generator.ipynb 11
@retry_on_error()  # type: ignore
def _generate(
    model: str,
    prompt: str,
    app_skeleton: str,
    total_usage: List[Dict[str, int]],
    output_directory: str,
    **kwargs,
) -> Tuple[str, List[Dict[str, int]], bool]:
    test_generator = CustomAIChat(
        params={
            "temperature": 0.2,
        },
        model=model,
        user_prompt=prompt,
    )
    test_validator = ValidateAndFixResponse(test_generator, _validate_response)
    validator_result = test_validator.fix(
        app_skeleton,
        total_usage,
        STEP_LOG_DIR_NAMES["app"],
        str(output_directory),
        **kwargs,
    )
    
    return (
        (validator_result, True) # type: ignore
        if isinstance(validator_result[-1], defaultdict)
        else validator_result
    )

# %% ../../nbs/App_And_Test_Generator.ipynb 14
def generate_app_and_test(
    description: str,
    model: str,
    output_directory: str,
    total_usage: List[Dict[str, int]],
    relevant_prompt_examples: str,
) -> Tuple[List[Dict[str, int]], bool]:
    """Generate integration test for the FastStream app

    Args:
        description: Validated User application description
        code_gen_directory: The directory containing the generated files.
        relevant_prompt_examples: Relevant examples to add in the prompts.

    Returns:
        The generated integration test code for the application
    """
    logger.info("==== Skeleton to App and Test Generation ====")
    with yaspin(
        text="Generating application and tests (usually takes around 30 to 90 seconds)...",
        color="cyan",
        spinner="clock",
    ) as sp:
        app_skeleton_file_name = Path(output_directory) / APPLICATION_FILE_PATH
        app_skeleton = read_file_contents(str(app_skeleton_file_name))

        prompt = (
            APP_AND_TEST_GENERATION_PROMPT.replace(
                "==== REPLACE WITH APP DESCRIPTION ====", description
            )
            .replace("==== RELEVANT EXAMPLES GOES HERE ====", relevant_prompt_examples)
            .replace("from .app import", "from app.application import")
        )

        total_usage, is_valid_app_code = _generate(
            model, prompt, app_skeleton, total_usage, output_directory
        )
        
        sp.text = ""
        if is_valid_app_code:
            message = " ✔ The application and the test files are generated."
        else:
            message = " ✘ Error: Failed to generate a valid application and test code."
            sp.color = "red"

        sp.ok(message)

        return total_usage, is_valid_app_code
