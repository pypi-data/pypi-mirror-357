# appserver-sdk-python-secrets

Gerenciador de segredos local usando `keyring`, com índice em JSON.

## Instalação

PyPI:

```bash
pip install appserver-sdk-python-secrets
```

Poetry:

```bash
poetry add appserver-sdk-python-secrets
```

pipx:

```bash
pipx install appserver-sdk-python-secrets
```

```bash
pipx install git+https://github.com/appserver-sdk/python-secrets.git
```

## Uso

```bash
appserver-secrets --set --service github --key GITHUB_TOKEN --password ghp_xxx
appserver-secrets --get --service github --key GITHUB_TOKEN
appserver-secrets --list
appserver-secrets --delete --service github --key GITHUB_TOKEN
```

## Caminho padrão do índice

- **Linux/macOS:** `~/.appserver_secrets_index.json`
- **Windows:** `C:\Users\SeuNomeDeUsuário\.appserver_secrets_index.json`

## Licença

MIT
