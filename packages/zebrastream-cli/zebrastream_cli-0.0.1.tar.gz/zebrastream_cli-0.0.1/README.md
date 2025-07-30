# ZebraStream CLI

An open-source command-line interface for the Management API of [ZebraStream](https://www.zebrastream.io), a simple, managed service to establish data flow between organizations, applications, and devices. Easily manage access tokens and view usage statistics for your ZebraStream account from your terminal.

## Features
- Create new access tokens
- List all access tokens
- Delete access tokens
- Show usage statistics

## Installation

### Recommended: Install Globally with pipx
[pipx](https://pypa.github.io/pipx/) allows you to run Python CLI tools in isolated environments:

```bash
pipx install zebrastream-cli
```

### Install the Latest Stable Release from PyPI
```bash
pip install zebrastream-cli
```

### Install the Latest Development Version from GitHub
```bash
pip install git+https://github.com/ZebraStream/zebrastream-cli.git
```

## Usage

After installation, the CLI is available as `zebrastream-cli`:

### Authentication
All commands require an API key. You can set it as an environment variable:

```bash
export ZEBRASTREAM_API_KEY=your_api_key_here
```

You can also set the API key persistently:
```bash
ZEBRASTREAM_API_KEY=your_api_key_here zebrastream-cli persist-config
```

### Optional: Custom API URL
The default uses the official ZebraStream Management API, but it is also possible to use a custom ZebraStream API endpoint:

```bash
export ZEBRASTREAM_API_URL=https://your.custom.api.url
```

### Commands

#### Create a New Access Token
```bash
zebrastream-cli create-token \
  --path /mystream \
  --access-mode read \
  --expires 2027-12-31 \
  [--recursive]
```
- `--expires` accepts ISO 8601 format (e.g. `2027-12-31` or `2027-12-31T12:34:56`).

#### List All Access Tokens
```bash
zebrastream-cli list-tokens
```
- Expired tokens are highlighted in red.

#### Delete an Access Token
```bash
zebrastream-cli delete-token --token-id key_xxxxxxxxxxxxxxxx
```

#### Show Usage Statistics
```bash
zebrastream-cli show-usage [--month YYYY-MM]
```



## Help
To see the available commands use:
```bash
zebrastream-cli --help
```

For detailed help on any command, use:
```bash
zebrastream-cli COMMAND --help
```

## License
See [LICENSE](LICENSE) for details.
