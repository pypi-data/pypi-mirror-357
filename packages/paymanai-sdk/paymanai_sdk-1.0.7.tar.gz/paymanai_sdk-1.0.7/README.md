# Payman SDK for Python

This SDK provides a simple way to interact with the Payman AI Platform's API using client credentials authentication and OAuth. The SDK automatically handles token management, including fetching and refreshing access tokens.

## Installation

### For End Users

```bash
pip install paymanai-sdk
```

### For Developers

1. Clone the repository:
   ```bash
   git clone https://github.com/payman-ai/payman-sdk-python.git
   cd payman-sdk-python
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Build the package:
   ```bash
   poetry build
   ```

## Usage

### Basic Example

```python
from payman_sdk.client import PaymanClient
from payman_sdk.types import PaymanConfig

# Initialize the client with credentials
config: PaymanConfig = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'environment': 'LIVE',
    'name': 'example_client'
}
client = PaymanClient.with_credentials(config)

# Ask a question
response = client.ask('Hello, world!')
print(response)
```

### Using an Authorization Code

```python
config: PaymanConfig = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'environment': 'LIVE',
    'name': 'example_client'
}
auth_code = 'your_auth_code'
client = PaymanClient.with_auth_code(config, auth_code)
response = client.ask('Hello, world!')
print(response)
```

### Using a Pre-existing Token

```python
client_id = 'your_client_id'
token_info = {
    'accessToken': 'your_access_token',
    'expiresIn': 3600
}
client = PaymanClient.with_token(client_id, token_info, name='example_client')
response = client.ask('Hello, world!')
print(response)
```

## Features

- **Type Safety**: Fully type-checked with mypy.
- **Flexible Configuration**: Supports client credentials, authorization codes, and pre-existing tokens.
- **Streaming Support**: Handle streaming responses with callbacks.
- **Session Management**: Automatic session handling with support for conversation persistence.

### Session Management

The SDK automatically manages sessions for you. Each client instance maintains a session ID that persists across requests. Here's how to work with sessions:

1. **Default Session Handling**:
```python
# A new session ID is automatically generated
client = PaymanClient.with_credentials({
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret'
})
```

2. **Starting a New Session**:
```python
# Start a new session during a request
response = client.ask("Hello!", {
    'new_session': True,
    'metadata': {'source': 'web-app'}
})
```

3. **Resuming Conversations**:
```python
# Start a conversation
response1 = client.ask("Hello!")
session_id = response1['sessionId']  # Save this for later

# Later, resume the conversation with a new client instance
client2 = PaymanClient.with_credentials({
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'session_id': session_id
})
response2 = client2.ask("What did we talk about earlier?")

# Get the current session ID from any client instance
current_session_id = client.get_session_id()
```

Session IDs are included in the response and can be used to maintain conversation context across different client instances or application restarts. Each session ID follows the format `ses-{uuid}` and is guaranteed to be unique.

The SDK handles session management transparently:
- Automatically generates new session IDs when needed
- Maintains session context across requests
- Allows explicit session creation with `new_session: True`
- Supports resuming conversations with existing session IDs
- Provides easy access to current session ID via `get_session_id()`

## Development

### Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run type checks:
   ```bash
   poetry run mypy .
   ```

### Building

```bash
poetry build
```

## License

MIT

## Environment Setup

Before running the SDK or tests, you need to set up your environment variables. Create a `.env` file in the root directory with the following variables:

```bash
PAYMAN_CLIENT_ID=your-client-id
PAYMAN_CLIENT_SECRET=your-client-secret
```

These credentials are required for both running the SDK and executing tests.

## Development

### Project Structure
```
payman-sdk-python/
├── payman_sdk/          # Main package directory
│   ├── __init__.py     # Package initialization
│   ├── client.py       # Main client implementation
│   ├── types.py        # Type definitions
│   └── utils.py        # Utility functions
├── tests/              # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_client.py
│   ├── test_types.py
│   └── test_utils.py
├── pyproject.toml      # Poetry configuration
├── poetry.lock         # Locked dependencies
├── pytest.ini         # Pytest configuration
├── CHANGELOG.md       # Version history
└── README.md          # This file
```

### Development Workflow

1. **Setup Development Environment**
```bash
# Install all dependencies including development tools
poetry install

# Activate virtual environment
poetry shell
```

2. **Running Tests**
```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/test_client.py -v

# Run tests with coverage report
poetry run pytest --cov=payman_sdk --cov-report=html
```

3. **Code Quality**
```bash
# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .

# Run all quality checks
poetry run black . && poetry run isort . && poetry run mypy .
```

4. **Building and Publishing**
```bash
# Build the package
poetry build

# Publish to PyPI (requires authentication)
poetry publish
```

## API Reference

### PaymanClient

#### Static Methods

- `with_credentials(config: PaymanConfig) -> PaymanClient`
  - Creates a client using client credentials
  - `config`: Configuration object containing client_id, client_secret, and optional environment

- `with_auth_code(config: PaymanConfig, auth_code: str) -> PaymanClient`
  - Creates a client using an authorization code
  - `config`: Configuration object containing client_id, client_secret, and optional environment
  - `auth_code`: Authorization code obtained via OAuth

- `with_token(client_id: str, token_info: Dict[str, Any], environment: Optional[Environment] = 'LIVE') -> PaymanClient`
  - Creates a client using an existing access token
  - `client_id`: Your Payman client ID
  - `token_info`: Object containing access token and its expiration time
  - `environment`: Optional environment to use (defaults to "LIVE")

#### Instance Methods

- `ask(text: str, options: Optional[AskOptions] = None, raw: bool = False) -> Union[FormattedTaskResponse, TaskResponse]`
  - Sends a message to the Payman AI Agent
  - `text`: The message or question to send
  - `options`: Optional parameters for the request
  - `raw`: Whether to return raw responses (default: False)

- `get_access_token() -> Optional[Dict[str, Any]]`
  - Gets the current access token and its expiration information
  - Returns None if no token is set

- `is_access_token_expired() -> bool`
  - Checks if the current access token has expired
  - Returns True if the token has expired or is about to expire within 60 seconds

### Types

- `PaymanConfig`
  ```python
  {
      'client_id': str,
      'client_secret': str,
      'environment': Optional[Literal['TEST', 'LIVE', 'INTERNAL']]
  }
  ```

- `AskOptions`
  ```python
  {
      'on_message': Optional[Callable[[Union[FormattedTaskResponse, TaskResponse]], None]],
      'new_session': Optional[bool],
      'metadata': Optional[Dict[str, Any]],
      'part_metadata': Optional[Dict[str, Any]],
      'message_metadata': Optional[Dict[str, Any]]
  }
  ```

### Response Types

- `FormattedTaskResponse`
  ```python
  {
      'status': Literal['completed', 'failed', 'in_progress'],
      'is_final': bool,
      'artifacts': Optional[List[Dict[str, Any]]],
      'error': Optional[Dict[str, Any]]
  }
  ```

- `TaskResponse`
  ```python
  {
      'jsonrpc': Literal['2.0'],
      'id': str,
      'result': Optional[Dict[str, Any]],
      'error': Optional[Dict[str, Any]]
  }
  ```

### Events

- `TaskStatusUpdateEvent`
  ```python
  {
      'type': Literal['status_update'],
      'status': Literal['completed', 'failed', 'in_progress'],
      'is_final': bool
  }
  ```

- `TaskArtifactUpdateEvent`
  ```python
  {
      'type': Literal['artifact_update'],
      'artifacts': List[Dict[str, Any]]
  }
  ```

## Error Handling

The SDK uses the `requests` library for HTTP requests. All API calls will raise an exception if the request fails. You can catch these exceptions and handle them appropriately:

```python
try:
    response = payman.ask("What's the weather?")
except requests.exceptions.RequestException as e:
    if hasattr(e, 'response'):
        # The request was made and the server responded with a status code
        # that falls out of the range of 2xx
        print(e.response.json())
        print(e.response.status_code)
    else:
        # Something happened in setting up the request that triggered an Error
        print('Error:', str(e)) 