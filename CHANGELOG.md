# Release notes

<!-- do not remove -->

## 0.0.1.dev2023091101

### New Features

- Move hardcoded examples in the prompt into a vector database ([#71](https://github.com/airtai/faststream-gen/pull/71)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Integrate new library and test ([#66](https://github.com/airtai/faststream-gen/pull/66)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Retrieve relevant embeddings and add it to prompt ([#65](https://github.com/airtai/faststream-gen/pull/65)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Generate embeddings for guides and the index page and store them in the package data directory ([#61](https://github.com/airtai/faststream-gen/pull/61)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Generate embeddings for guides and the index page, and store them in the package_data ([#57](https://github.com/airtai/faststream-gen/issues/57))

- Validate the generated test code against the application code and auto fix the errors ([#53](https://github.com/airtai/faststream-gen/pull/53)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Update test generation prompt ([#43](https://github.com/airtai/faststream-gen/pull/43)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Show the approximate cost in dollars on the console, similar to how the langchain library does. ([#40](https://github.com/airtai/faststream-gen/issues/40))

- Show token usage and provide an estimated cost (in $), even if the CLI command terminates due to an error. ([#38](https://github.com/airtai/faststream-gen/issues/38))

- Generate test code for the generated application code ([#32](https://github.com/airtai/faststream-gen/pull/32)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

- Generate application code based on the asyncapi spec ([#28](https://github.com/airtai/faststream-gen/pull/28)), thanks to [@harishmohanraj](https://github.com/harishmohanraj)

### Bugs Squashed

- Update the app_creation prompt to fix the error mentioned in the description ([#36](https://github.com/airtai/faststream-gen/issues/36))