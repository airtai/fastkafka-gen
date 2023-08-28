# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Constants.ipynb.

# %% auto 0
__all__ = ['ASYNC_API_SPEC_FILE_NAME', 'APPLICATION_FILE_NAME', 'INTEGRATION_TEST_FILE_NAME', 'DEFAULT_PARAMS', 'DEFAULT_MODEL',
           'MAX_RETRIES', 'MAX_ASYNC_SPEC_RETRIES', 'TOKEN_TYPES', 'MODEL_PRICING', 'INCOMPLETE_DESCRIPTION',
           'DESCRIPTION_EXAMPLE', 'MAX_NUM_FIXES_MSG']

# %% ../../nbs/Constants.ipynb 2
ASYNC_API_SPEC_FILE_NAME = "asyncapi.yml"
APPLICATION_FILE_NAME = "application.py"
INTEGRATION_TEST_FILE_NAME = "test.py"

# %% ../../nbs/Constants.ipynb 4
DEFAULT_PARAMS = {
    "temperature": 0.7,
}

DEFAULT_MODEL = "gpt-3.5-turbo-16k" # gpt-3.5-turbo

MAX_RETRIES = 5
MAX_ASYNC_SPEC_RETRIES = 3

# %% ../../nbs/Constants.ipynb 6
TOKEN_TYPES = ["prompt_tokens", "completion_tokens", "total_tokens"]

MODEL_PRICING = {
    "gpt-4-32k": {
        "input": 0.06,
        "output": 0.12
    },
    "gpt-3.5-turbo-16k": {
        "input": 0.003,
        "output": 0.004
    },
}

# %% ../../nbs/Constants.ipynb 8
INCOMPLETE_DESCRIPTION = "Please check if your application description is missing some crutial information:\n - Description of the messages which will be produced/consumed\n - At least one topic\n - The business logic to implement while consuming/producing the messages\n"
DESCRIPTION_EXAMPLE = """
If you're unsure about how to construct the app description, consider the following example for guidance

APPLICATION DESCRIPTION EXAMPLE:
Write a fastkafka application with with one consumer function and two producer functions. 
The consumer function should receive the a message posted on "new_joinee" topic. 
The message should contain "employee_name", "age", "location" and "experience" attributes. 
After consuming the consumer function should send the details to the "project_team" and "admin_team" topics. 
Use only localhost broker."""

MAX_NUM_FIXES_MSG = "Maximum number of retries"
