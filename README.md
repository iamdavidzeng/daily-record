# daily-record
Daily coding...

```
git clone git@github.com:iamdavidzeng/iadz.git

cd /path/to/iadz/python
```

## Prerequisites

- [Python3](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/stable/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## Initial environment

1. Use virtualenv initial your virtual python environment first.
```
virtualenv -p python3 .env
```
2. Activate your virtual environment
```
source .env/bin/activate
```
3. Install packages
```
pip install -e ".[dev]"
```
4. If you use VS-Code
```
# edit this in your .vscode/settings.json:
    {
        "python.linting.pylintEnabled": false,
        "python.linting.flake8Enabled": true,
        "python.linting.enabled": true,
        "python.pythonPath": "${workspaceFolder}/python/.env/bin/python3.6"
    }
then you are able to use you virtualenv in VS-Code.
```
