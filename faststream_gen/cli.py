# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/CLI.ipynb.

# %% auto 0
__all__ = ['logger', 'app', 'generate_fastkafka_app']

# %% ../nbs/CLI.ipynb 1
from typing import *

import typer
from pathlib import Path

from ._components.logger import get_logger
from faststream_gen._code_generator.app_description_validator import (
    validate_app_description,
)
from faststream_gen._code_generator.helper import (
    set_logger_level,
    add_tokens_usage,
    get_relevant_prompt_examples,
    strip_white_spaces,
    write_file_contents,
    ensure_openai_api_key_set,
)
from ._code_generator.constants import MODEL_PRICING, EMPTY_DESCRIPTION_ERROR, OpenAIModel
from ._components.new_project_generator import create_project
from ._code_generator.app_skeleton_generator import generate_app_skeleton
# from faststream_gen._code_generator.app_and_test_generator import generate_app_and_test

# %% ../nbs/CLI.ipynb 3
logger = get_logger(__name__)

# %% ../nbs/CLI.ipynb 6
app = typer.Typer(
    short_help="Commands for accelerating FastStream project creation using advanced AI technology",
     help="""Commands for accelerating FastStream project creation using advanced AI technology.

These commands use OpenAI's model to generate FastStream project. To access this feature, kindly sign up if you haven't already and create an API key with OpenAI. You can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details.

Once you have the key, please set it in the OPENAI_API_KEY environment variable before executing the code generation commands.

Note: Accessing OpenAI API incurs charges. For further information on pricing and free credicts, check this link: https://openai.com/pricing
    """,
)

# %% ../nbs/CLI.ipynb 7
def _calculate_price(total_tokens_usage: Dict[str, int], model: str) -> float:
    """Calculates the total price based on the number of promt & completion tokens and the models price for input and output tokens (per 1k tokens).

    Args:
        total_tokens_usage: OpenAI "usage" dictionaries which defines prompt_tokens, completion_tokens and total_tokens


    Returns:
        float: The price for used tokens
    """
    model_price = MODEL_PRICING[model]
    price = (total_tokens_usage["prompt_tokens"] * model_price["input"] + total_tokens_usage["completion_tokens"] * model_price["output"]) / 1000
    return price

# %% ../nbs/CLI.ipynb 9
def _get_description(input_path: str) -> str:
    """Reads description from te file and returns it as a string

    Args:
        input_path: Path to the file with the desription
        
    Raises:
        ValueError: If the file does not exist.

    Returns:
        The description string which was read from the file.
    """
    try:
        with open(input_path) as file:
            # Read all lines to list
            lines = file.readlines()
            # Join the lines 
            description = '\r'.join(lines)
            logger.info(f"Reading application description from '{str(Path(input_path).absolute())}'.")
    except Exception as e:
        raise ValueError(f"Error while reading from the file: '{str(Path(input_path).absolute())}'\n{str(e)}")
    return description

# %% ../nbs/CLI.ipynb 12
def _validate_app_description(
    description: Optional[str],
    input_path: str,
    model: OpenAIModel,
    tokens_list: List[Dict[str, int]],
) -> Tuple[str, List[Dict[str, int]]]:
    if not description:
        if not input_path:
            raise ValueError(EMPTY_DESCRIPTION_ERROR)
        description = _get_description(input_path)
        cleaned_description = strip_white_spaces(description)
        return validate_app_description(cleaned_description, model.value, tokens_list)

# %% ../nbs/CLI.ipynb 16
@app.command(
    "generate",
    help="Effortlessly create a new FastStream project based on the app description.",
)
@set_logger_level
def generate_fastkafka_app(
    description: Optional[str] = typer.Argument(
        None,
        help="""Summarize your FastStream application in a few sentences!


\nInclude details about messages, topics, servers, and a brief overview of the intended business logic.


\nThe simpler and more specific the app description is, the better the generated app will be. Please refer to the below example for inspiration:


\nCreate a FastStream application using localhost broker for testing and use the default port number. 
It should consume messages from the "input_data" topic, where each message is a JSON encoded object containing a single attribute: 'data'. 
For each consumed message, create a new message object and increment the value of the data attribute by 1. Finally, send the modified message to the 'output_data' topic.
\n""",
    ),
    input_path: str = typer.Option(
        None,
        "--input_file",
        "-i",
        help="""
        The path to the file with the app desription. This path should be relative to the current working directory.
        
        \n\nIf the app description is passed via both a --input_file and a command line argument, the description from the command line will be used to create the application.
        """,
    ),
    output_path: str = typer.Option(
        ".",
        "--output_path",
        "-o",
        help="The path to the output directory where the generated project files will be saved. This path should be relative to the current working directory.",
    ),
    model: OpenAIModel = typer.Option(
        OpenAIModel.gpt3.value,
        "--model",
        "-m",
        help=f"The OpenAI model that will be used to create the FastStream project. For better results, we recommend using '{OpenAIModel.gpt4.value}'.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging by setting the logger level to INFO.",
    ),
    save_log_files: bool = typer.Option(
        False,
        "--dev",
        "-d",
        help="Save the complete logs generated by faststream-gen inside the output_path directory.",
    ),
) -> None:
    """Effortlessly create a new FastStream project based on the app description."""
    logger.info("Project generation started.")
    try:
        tokens_list: List[Dict[str, int]] = []
        ensure_openai_api_key_set()

        # Step 1: Validate description
        validated_description, tokens_list = _validate_app_description(
            description, input_path, model, tokens_list
        )
        
        # Step 2: Project creation
        create_project(output_path)

        # Step 3: Get relevant application examples
        prompt_examples = get_relevant_prompt_examples(validated_description)

        # Step 4: Generate application skeleton
        tokens_list, is_valid_skeleton_code = generate_app_skeleton(
            validated_description,
            output_path,
            model.value,
            tokens_list,
            prompt_examples["description_to_skeleton"],
        )
#         if is_valid_skeleton_code:
#             tokens_list, is_valid_app_code = generate_app_and_test(
#                 validated_description,
#                 model.value,
#                 output_path,
#                 tokens_list,
#                 prompt_examples["skeleton_to_app_and_test"],
#             )

    except (ValueError, KeyError) as e:
        fg = typer.colors.RED
        typer.secho(e, err=True, fg=fg)
        raise typer.Exit(code=1)
    except Exception as e:
        fg = typer.colors.RED
        typer.secho(f"Unexpected internal error: {e}", err=True, fg=fg)
        raise typer.Exit(code=1)
    finally:
        total_tokens_usage = add_tokens_usage(tokens_list)
        price = _calculate_price(total_tokens_usage, model.value)

        fg = typer.colors.CYAN
        typer.secho(f" Tokens used: {total_tokens_usage['total_tokens']}", fg=fg)
        logger.info(f"Prompt Tokens: {total_tokens_usage['prompt_tokens']}")
        logger.info(f"Completion Tokens: {total_tokens_usage['completion_tokens']}")
        typer.secho(f" Total Cost (USD): ${round(price, 5)}", fg=fg)
