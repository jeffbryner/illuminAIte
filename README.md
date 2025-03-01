# ai_csv_chat
Use AI to have an interactive data conversation with your local csv files

## Why?

Data is everywhere in security. You have data about vulnerabilities, alerts, threats, forensic artifacts. It’s stored in a variety of formats, behind a variety of consoles, applications, command line tools, etc.
Making sense of that data is difficult. You need to format it, analyze it, decide what is useful, etc.
What if you could use AI to have a conversational interaction with your data in a way that lets you:

- Rapidly get an overview
- Have a conversation about the data
- Gain insights

AI csv chat aims to accomplish this by bringing data to AI in conjunction with simple tools in a way that allows you to meet your data where it lies (.csv files), get insights as quickly as possible and do it without having to write complicated queries or learn yet another language.


## Installation
Recommended to use a virtual python environment seeded with uv
- https://docs.astral.sh/uv/getting-started/installation/

### tl;dr
``` 
# mac
brew install uv

# windows
powershell -c "irm https://astral.sh/uv/install.ps1 | more"

# or install from https://github.com/astral-sh/uv/releases

```

### Installing csv chat
```
git clone https://github.com/jeffbryner/ai_csv_chat.git
cd ai_csv_chat
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

```

## Usage
```
# to use everything as default
# assumes you will use gemini in vertexAI and your local 
# gcloud config is set up with the project you want to use
python csv_chat.py
```