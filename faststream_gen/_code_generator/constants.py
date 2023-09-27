# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Constants.ipynb.

# %% auto 0
__all__ = ['APPLICATION_FILE_PATH', 'TEST_FILE_NAME', 'LOGS_DIR_NAME', 'STEP_LOG_DIR_NAMES', 'DEFAULT_PARAMS', 'MAX_RETRIES',
           'MAX_RESTARTS', 'MAX_ASYNC_SPEC_RETRIES', 'TOKEN_TYPES', 'MODEL_PRICING', 'OPENAI_KEY_EMPTY_ERROR',
           'OPENAI_KEY_NOT_SET_ERROR', 'EMPTY_DESCRIPTION_ERROR', 'INCOMPLETE_DESCRIPTION', 'DESCRIPTION_EXAMPLE',
           'MAX_NUM_FIXES_MSG', 'INCOMPLETE_APP_ERROR_MSG', 'FASTSTREAM_REPO_ZIP_URL', 'FASTSTREAM_DOCS_DIR_SUFFIX',
           'FASTSTREAM_EXAMPLES_DIR_SUFFIX', 'FASTSTREAM_EXAMPLE_FILES', 'FASTSTREAM_TMP_DIR_PREFIX',
           'FASTSTREAM_DIR_TO_EXCLUDE', 'FASTSTREAM_TEMPLATE_ZIP_URL', 'FASTSTREAM_TEMPLATE_DIR_SUFFIX', 'OpenAIModel']

# %% ../../nbs/Constants.ipynb 2
APPLICATION_FILE_PATH = "app/application.py"
TEST_FILE_NAME = "tests/test_application.py"
LOGS_DIR_NAME = "_faststream_gen_logs"

STEP_LOG_DIR_NAMES = {
    "skeleton": "app-skeleton-generation-logs",
    "app": "app-and-test-generation-logs"
}

# %% ../../nbs/Constants.ipynb 4
DEFAULT_PARAMS = {
    "temperature": 0.7,
}

MAX_RETRIES = 3
MAX_RESTARTS = 3
MAX_ASYNC_SPEC_RETRIES = 3


from enum import Enum
class OpenAIModel(str, Enum):
    gpt3 = "gpt-3.5-turbo-16k"
    gpt4 = "gpt-4"


# %% ../../nbs/Constants.ipynb 7
TOKEN_TYPES = ["prompt_tokens", "completion_tokens", "total_tokens"]

MODEL_PRICING = {
    OpenAIModel.gpt4.value: {
        "input": 0.03,
        "output": 0.06
    },
    OpenAIModel.gpt3.value: {
        "input": 0.003,
        "output": 0.004
    },
}

# %% ../../nbs/Constants.ipynb 9
OPENAI_KEY_EMPTY_ERROR = "Error: OPENAI_API_KEY cannot be empty. Please set a valid OpenAI API key in OPENAI_API_KEY environment variable and try again.\nYou can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details."
OPENAI_KEY_NOT_SET_ERROR = "Error: OPENAI_API_KEY not found in environment variables. Set a valid OpenAI API key in OPENAI_API_KEY environment variable and try again. You can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details."

EMPTY_DESCRIPTION_ERROR = "Error: you need to provide the application description by providing it with the command line argument or by providing it within a textual file wit the --input_file argument."



INCOMPLETE_DESCRIPTION = """Please check if your application description is missing some crucial information:
- Description of the messages that will be produced or consumed
- At least one topic
- The business logic to implement while consuming or producing the messages
"""
DESCRIPTION_EXAMPLE = """
If you're unsure about how to construct the app description, consider the following example for guidance

APPLICATION DESCRIPTION EXAMPLE:
Create a FastStream application using localhost broker for testing and use the default port number. 
It should consume messages from the 'input_data' topic, where each message is a JSON encoded object containing a single attribute: 'data'. 
For each consumed message, create a new message object and increment the value of the data attribute by 1. Finally, send the modified message to the 'output_data' topic.
"""

MAX_NUM_FIXES_MSG = "Maximum number of retries"

INCOMPLETE_APP_ERROR_MSG = """Apologies, we couldn't generate a working application and test code from your application description.

Please run the following command to start manual debugging:
"""

# %% ../../nbs/Constants.ipynb 11
FASTSTREAM_REPO_ZIP_URL = "http://github.com/airtai/faststream/archive/main.zip"
FASTSTREAM_DOCS_DIR_SUFFIX = "faststream-main/.faststream_gen"
FASTSTREAM_EXAMPLES_DIR_SUFFIX = "faststream-main/faststream_gen_examples"
FASTSTREAM_EXAMPLE_FILES = ['description.txt', 'app_skeleton.py', 'app.py', 'test_app.py']
FASTSTREAM_TMP_DIR_PREFIX = "appended_examples"
FASTSTREAM_DIR_TO_EXCLUDE = "api"

# %% ../../nbs/Constants.ipynb 13
FASTSTREAM_TEMPLATE_ZIP_URL = "http://github.com/airtai/faststream-template/archive/main.zip"
FASTSTREAM_TEMPLATE_DIR_SUFFIX = "faststream-template-main"
