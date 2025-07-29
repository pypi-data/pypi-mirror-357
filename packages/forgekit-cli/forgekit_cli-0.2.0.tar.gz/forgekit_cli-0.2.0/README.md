# 📦 Forge Kit CLI

<img src="forgekit.png" width="300" />

Forge Kit CLI is a command-line tool that interacts with the Forge Kit Server to generate, scaffold, and manage AI-assisted software projects using modular drivers and LLM-powered code generation.

## ✨ Features

* Connects to Forge Kit Server via API
* Provides simple terminal commands for scaffolding, fixing, and managing code
* Supports automatic config detection and override
* Requires a ForgeKit server api

## ⚙️ Installation

```bash
git clone https://github.com/your-repo/forgekit-cli.git
cd forgekit-cli
pip install -e .
```

Set your environment variables:

```bash
export FORGEKIT_API_URL=http://localhost:8000
export FORGEKIT_API_KEY=your-secret-key
```

## 🚀 Usage

```bash
forgekit [COMMAND] [OPTIONS]
```

### Commands

#### `forgekit list-drivers`

List available drivers from the connected server.

#### `forgekit generate`

Generate a new project based on your config.

#### `forgekit fix`

Attempt to fix build errors in a generated project using AI.

## 🧾 Config File

Create a `forgekit.config.json` like:

```json
{
  "name": "my-app",
  "description": "A FastAPI app with OpenAI support",
  "references": ["https://example.com"],
  "model": "gpt-4",
  "driver": "Next.js"
}
```

## 📜 License

Copyright (c) 2025 Mitchell Long

This software is proprietary. Unauthorized use is prohibited.