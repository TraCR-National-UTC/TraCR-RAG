# TraCR-RAG

This project develops a Retrieval-Augmented Generation (RAG) powered Large Language Model (LLM) designed to support legislative analysis for connected and automated transportation systems. The framework extracts relevant information from existing laws to answer policy-related inquiries, reduces LLM hallucinations by generating curated training datasets, and highlights potential legal gaps for further review. By combining retrieval with generative capabilities, the system provides more accurate, reliable, and context-specific responses compared to leading commercial LLMs. This approach demonstrates how domain-specific RAG frameworks can enhance legal analysis, cybersecurity, and data privacy policymaking in emerging transportation technologies.

---

## 1) Prerequisites

Before you can run this project, you’ll need a few tools installed on your computer.  

- **Python (version 3.10 or higher)**  
  Python is the main programming language this project is written in.  
  👉 Download it from [python.org/downloads](https://www.python.org/downloads/).

  To check if Python is already installed, open your command line (Terminal on macOS/Linux, PowerShell on Windows) and type:
  ```bash
  python --version
  ```
  or

  ```bash
  python3 --version
  ```
  
If you see something like `Python 3.11.5`, you’re good to go.

- **pip**  
  pip is Python’s package manager. 
  It comes with Python by default and is used to install the extra libraries the project needs.

- **virtualenv (or venv)**  
  This is where we install only the tools needed for this project, so they don’t interfere with other softwares or projects on any computer.  

- **Git**  
  Git helps to download (or “clone”) the project from GitHub.  
  👉 Get it from [git-scm.com](https://git-scm.com/downloads).

- **SQLite (optional)**  
  This is a lightweight database that usually comes included with Python.  
  You don’t need to install anything extra for development unless you plan to use a different database.

> **Tip:** On **Windows**, open PowerShell. On **macOS/Linux**, open Terminal.  
> All the commands in this guide should be typed there.

---
## 2) Clone & enter the project

This step copies the project from GitHub to your computer and moves you into the project folder.

```bash
# Clone the repository 
git clone https://github.com/TraCR-National-UTC/TraCR-RAG.git

# Move into the project directory
cd TraCR-RAG
```

---

## 3) Create & activate a virtual environment

A **virtual environment** is like a private workspace where only the tools and libraries needed for this project are installed.  
This keeps things clean and avoids conflicts with other Python projects on your computer.

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### Windows (PowerShell)

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```
✅ When the virtual environment is active, your command line will show (.venv) at the start of the line.
To leave (deactivate) the virtual environment later, just type:
```bash
deactivate
```





