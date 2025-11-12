# Whale

A 2D casino-themed dice-building roguelike.

## requirements
- Python 3.12.x


## to start developing

1) **create venv:**
*for macos/linux:*
```bash
python -m venv .venv
source .venv/bin/activate
```

*for windows:*
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) **install dependencies**
```bash
python -m pip install -U pip
pip install -e ".[dev]"
```


## dev workflow

**run**
```bash
whale
# or
python -m whale.main
```

**run tests**
```bash
pytest
```

