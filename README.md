# trip-advisor-rag-agent

## Python environment

Use Python 3.14 on Windows for this project. The current dependency set includes
`zstandard` through LangSmith; on Python 3.15, pip may try to build it from
source and require Microsoft C++ Build Tools.

If `.venv` was created with Python 3.15, recreate it with Python 3.14:

```powershell
Remove-Item -Recurse -Force .venv
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

In VS Code, select `.venv\Scripts\python.exe` as the workspace interpreter.
The repository pins the recommended Python version in `.python-version`.