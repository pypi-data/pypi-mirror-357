# Xeni 🧠

Xeni is a modular Python framework designed for building intelligent agents and automation pipelines. It emphasizes extensibility, configuration-driven workflows, and ease of integration with various models or tools.

---

## 🚀 Features

- ⚙️ Modular architecture with customizable adapters  
- 📁 Configuration-driven behavior using YAML/JSON  
- 🧪 Includes testable CLI for development and debugging  
- 🧵 Easily extensible with your own modules and logic  

---

## 📦 Installation

```bash
git clone https://github.com/ZotacMaster/Xeni.git
cd Xeni
pip install .
```
Or, install via pipx or pip
```bash
pipx install xeni
pip install xeni
```

## 📂 Project Structure
```bash 
Xeni
└── src
    └── xeni
        ├── http_proxy
        │   ├── endpoints
        │   │   ├── __init__.py
        │   │   ├── search.py
        │   │   ├── insert.py
        │   │   └── healthcheck.py
        │   └── server.py
        ├── mcp_proxy
        │   ├── adapters
        │   │   ├── __init__.py
        │   │   ├── base.py
        │   │   ├── claude.py
        │   │   ├── cursor.py
        │   │   └── cline.py
        │   └── server.py
        ├── utils
        │   ├── __init__.py
        │   ├── config.py
        │   ├── file_manager.py
        │   └── models.py
        ├── __init__.py
        └── cli.py
.gitignore
.python-version
LICENCE
pyproject.toml
uv.lock
```

## 🧑‍💻 Usage
Commands avialable to xeni:
```bash
xeni start #starts the FastAPI server

xeni connect ${agent_name} #Connect to supported agents

xeni key ${API_key} --token ${Bearer token} #Sets the user credentials

xeni set-url ${url}
```
