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
pip install forgekit-cli
```

Go to www.forgekit.info and register to aquire keys.

Set your environment variables:

```bash
forgekit-cli login
```

## 🚀 Usage

```bash
forgekit-cli [COMMAND] [OPTIONS]
```

### Commands

#### `forgekit-cli list-drivers`

List available drivers from the connected server.

#### `forgekit-cli generate`

Generate a new project based on your config.

#### `forgekit-cli fix`

Attempt to fix build errors in a generated project using AI.

## 🧾 Config File

Create a `forgekit.config.json` via the following command:

```bash
forgekit-cli initialize
```

## 📜 License

Copyright (c) 2025 Mitchell Long

This software is proprietary.