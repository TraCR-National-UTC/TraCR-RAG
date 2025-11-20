# TraCR-RAG

This project develops a Retrieval-Augmented Generation (RAG) powered Large Language Model (LLM) designed to support legislative analysis for connected and automated transportation systems. The framework extracts relevant information from existing laws to answer policy-related inquiries, reduces LLM hallucinations by generating curated training datasets, and highlights potential legal gaps for further review. By combining retrieval with generative capabilities, the system provides more accurate, reliable, and context-specific responses compared to leading commercial LLMs. This approach demonstrates how domain-specific RAG frameworks can enhance legal analysis, cybersecurity, and data privacy policymaking in emerging transportation technologies.
<br><br>
<img width="1433" height="790" alt="image" src="https://github.com/user-attachments/assets/efdaba35-8cdf-4dd2-848e-8dd148fee390" />

---

## 1) Prerequisites

Before you can run this project, you’ll need a few tools installed on your computer.  

- **Python 3.12**  [must] <br>
  Python is the main programming language this project is written in.  
  👉 Download Python 3.12.9 from [https://www.python.org/downloads/release/python-3129/](https://www.python.org/downloads/release/python-3129/) or click here to download it for windows -> [Download Python 3.12.9](https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe)
  
  <img width="1186" height="421" alt="image" src="https://github.com/user-attachments/assets/ba22a3f8-abb2-489d-a818-497c4c84ac22" />
  👉 Install Python 3.12.9 by double clicking on the installer that has just been download.
  
  👉 To check if Python is already installed, open your command line (Terminal on macOS/Linux, PowerShell on Windows) and type:
  ```bash
  python --version
  ```
  or

  ```bash
  python3 --version
  ```
  
If you see something like `Python 3.12.9`, you’re good to go.

- **pip**  [auto]
  pip is Python’s package manager. 
  It comes with Python by default and is used to install the extra libraries the project needs.

- **virtualenv (or venv)**  [auto]
  This is where we install only the tools needed for this project, so they don’t interfere with other softwares or projects on any computer.
  It will also come with Python by default. 

- **Git**  [must]
  Git helps to download (or “clone”) the project from GitHub.  
  👉 Download and Install Git similarly from [git-scm.com](https://git-scm.com/downloads).

**SHORTCUT:**
If you would like to take a shortcut, follow the steps below. If not, go to step 2.
- Download the `setup.bat` file from here: [TraCR-RAG/setup.bat](https://github.com/TraCR-National-UTC/TraCR-RAG/blob/main/setup.bat).  
  Create a folder and place the `setup.bat` file inside it. Then double-click the file to run it.  
  This will execute all commands from steps 2 to 4. After it finishes, you will see the `TraCR-RAG` folder downloaded and set up inside your folder.

- Inside the TraCR-RAG project folder, you will find a `.env` file. Open it with Notepad or any other text editor and add your OpenAI API key.  
  (Refer to [Step 5](https://github.com/TraCR-National-UTC/TraCR-RAG/edit/main/README.md#5-configuration-environment-variables) for instructions on obtaining an OpenAI API key.)

- Inside the TraCR-RAG folder, there is a `run.bat` file. Double-click it to run. It automatically performs steps 6 and 7.

Once the process is complete, go to **http://127.0.0.1:8000/** to access **TraCR-Legal-AI**.



---
## 2) Clone & enter the project
> **Tip:** On **Windows**, open PowerShell. On **macOS/Linux**, open Terminal.  
> All the commands in this guide should be typed there.

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

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv .venv
source ./.venv/bin/activate
```


✅ When the virtual environment is active, your command line will show (.venv) at the start of the line.

---
## 4) Install dependencies

Dependencies are like ingredients the project needs to run.  
They are listed in a file called `requirements.txt`. The GitHub repository should already have this file.

A typical `requirements.txt` might look like this:

```txt
django>=4.2
openai>=1.0.0
python-dotenv>=1.0.0
```
Run the following commands to install all the dependencies.
```bash
# Make sure pip is up to date
pip install --upgrade pip

# Install everything listed in requirements.txt
pip install -r requirements.txt
```
💡 If you get a permissions error, make sure your virtual environment (.venv) is activated before running these commands.

---
## 5) Configuration (environment variables)

The project needs secret information (like your OpenAI API key).  
These are stored in **environment variables** so they’re not visible in the code.

### Use a `.env` file (recommended)

1. In the root folder of your project (where `manage.py` is located), create a new file called **`.env`**.
2. Add the following content inside it:

```env
# --- Django ---
ALLOWED_HOSTS=localhost,127.0.0.1

# --- OpenAI ---
OPENAI_API_KEY=sk-...your-key-here...
```
Here, the "OPENAI_API_KEY" has to be your own API_KEY from the openai platform.
This key powers the generator component of the RAG system. In our setup, we use GPT-4o-mini, the lightweight version of the model, as the LLM.

You can get the key from here:

1. Go to https://platform.openai.com/settings/organization/general and then navigate to **API keys** from the left sidebar.  
2. Create a new key.  
3. Copy and paste it here.  
4. Go to **Billing** from the left sidebar.  
5. Add some credit to your API key — you can start with as little as **$5**.

👉 Never share or upload .env files! They should always be added to .gitignore.

## 6) Load the static files

Run the following command to load the static files (images, styles, etc.):

```bash
python manage.py collectstatic --noinput 
```
or 

```bash
python3 manage.py collectstatic --noinput 
```

## 7) Run the development server

Now you can start the server:

```bash
python manage.py runserver
```
Once it starts, open your browser and visit:
👉 http://127.0.0.1:8000/



