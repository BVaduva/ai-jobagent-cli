# Local AI JobAgent

A command-line tool built with Python and local LLMs (Ollama) to analyze, filter, and critically evaluate tech job postings. 

This project serves as a **Proof of Concept (PoC)** for local Retrieval-Augmented Generation (RAG) and API state management. It is designed to protect junior developers from "overselling" themselves and falling into HR buzzword traps.

## The Problem it Solves

Job postings are often bloated with buzzwords. As a Junior/Mid-level developer, it is crucial to quickly identify:

* **Role vs. Reality Mismatch:** Exposing hidden biases (e.g., identifying a job that is actually 80%+ UI/Frontend despite a "Fullstack" title).
* **Config & Legacy Traps:** Distinguishing software engineering from configuring proprietary ecosystems (e.g., SAP, Salesforce, CMS).
* **Overselling Dangers:** Matching the required tech stack against actual, provable project experience to avoid failing technical interviews.
* **Logistical Dealbreakers:** Checking if the remote-policy actually matches the commute radius.

## Architecture & Stack

This tool uses a strictly local workflow to ensure **100% Data Privacy** (no CV data is sent to cloud APIs).

* **Language:** Python 3 (`BeautifulSoup4`, `requests`)
* **LLM Engine:** Local Ollama (I tried `Llama 3.1 8B` and `qwen2.5 7B`)
* **Context (RAG):** Markdown-based Context Injection

### Core Components

1. **`scrape.py`**: Extracts the structured `JobPosting` data directly from the `<script type='application/ld+json'>` tags and injects it into an analytical framework (`jobcheck_prompt.md`).
2. **`chat.py`**: A lightweight, stateless API client using native `urllib`. It loads the user's `masterprofile.md` as a permanent system prompt and handles the token-memory management.
3. **`Modelfile`**: Defines a strict "No-Bullshit" System Persona to force the LLM into a highly critical, analytical state.

## Engineering Decisions & Limitations

During the development of this PoC, several decisions were made:

### 1. Context Stuffing vs. Vector Databases (YAGNI)
I actively decided against using a Vector Database. The combined token count of a standard CV (`masterprofile.md`) and a job posting is well under 2,000 tokens. Modern LLMs handle this easily within their context window. Implementing complex embedding pipelines for data that fits into working memory is unnecessary over-engineering. Pure Context Stuffing is the most performant choice here.

### 2. API State Management (Statelessness)
A naive approach to CLI chatbots leads to memory leaks (Token Overflow) because the context window fills up with previous checks. The `chat.py` script implements a stateless workflow. The system prompt (CV) is kept in a permanent array, but the conversational array is deep-copied and reset for every `/check` command to keep the RAM stable.

### 3. Hardware Limitations (The 8B Parameter Bottleneck)
This tool shows the limits of running AI locally on standard laptops. A small 8-Billion parameter model (Llama 3.1) often struggles with the logical reasoning needed to analyze complex tech stacks. 

A smarter model (32B/70B) would fix this, but it requires too much RAM/VRAM and makes the CLI very slow. That's why this project remains a strict Proof of Concept (PoC) for local RAG. 

Using a cloud API (like OpenAI or Google) would easily solve the reasoning and hardware issues, but it would completely violate the core design goal of this tool: 100% data privacy.

### 4. Scraping Limits (Static vs. Dynamic DOM)
The lightweight scraper uses `requests` and `BeautifulSoup`. 
This works for Server-Side Rendered (SSR) pages that embed `JSON-LD` directly in the initial HTML. 
It fails on heavily protected Single Page Applications (SPAs) like Indeed or LinkedIn, which require JavaScript execution (e.g., via Playwright) or active anti-bot bypasses, which is out of scope for this CLI tool.

## Localization & Customization (German Default)

This project is currently tailored to the **DACH job market** and uses **German** as the default language for the `Modelfile`, prompt templates, and CLI outputs. 

* **Why German?** Feeding a German job posting into an English system prompt forces a small 8B model to constantly translate back and forth. Keeping the entire context loop (System Prompt -> Scraped Input -> Output) in a single language drastically reduces the cognitive overhead for the model, prevents context-switching confusion, and significantly improves the logical accuracy of the output.

**How to adapt this tool for your own needs:**

1. **Adjust the Persona (`Modelfile`):** The provided `Modelfile` contains highly opinionated rules tailored to my personal profile (e.g., treating proprietary ecosystems like SAP or CMS as strict red flags). You **must** edit the `SYSTEM` prompt in this file to align with your own career goals and preferences before building the model.
2. **For Non-German Speakers:** If you are applying for English-speaking roles, you should translate the core instruction files to English to maintain a single-language context loop. You will need to translate:
   * The `SYSTEM` prompt inside the `Modelfile`.
   * The analytical framework in `jobcheck_prompt.md`.
   * The `masterprofile_template.md`.
   * The context `injection` string inside `chat.py`.
   * Console outputs returned by `chat.py` and `scrape.py`

## Usage

1. Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/BVaduva/ai-jobagent-cli.git
cd ai-jobagent-cli
```

2. Ensure [Ollama](https://ollama.com/) is installed and running on your system.
3. Pull the desired model fitting your needs and hardware the best from [here](https://ollama.com/library):
```bash
ollama pull YourModelName
```

> [!info] Modelfile
> 
>  The `Modelfile` needs to be adjusted for the desired model.
>  Change the first line `FROM llama3.1` to `FROM YourModelName`

4. Build the custom model persona (this reads the `Modelfile` in your current directory):
```bash
ollama create jobagent -f Modelfile
```

5. Copy the `masterprofile_template.md` to `masterprofile.md` and fill in your actual data. 
   _(Note: `masterprofile.md` is `.gitignore`d to protect your data)._
6. Run the CLI:
```bash
python chat.py
```

7. Paste a job URL using the command: `/check <URL>`
