# FatController

**FatController** is a versatile daemon management and automation framework designed to give system administrators power and flexibility in managing tasks across heterogeneous systems. It provides a unique "GUI-CLI" interface, blending the visual feedback of a graphical interface with the efficiency and scriptability of a command line.

![Status](https://img.shields.io/badge/status-active-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)

## 📖 Overview

At its core, FatController allows you to:
- **Manage Entities**: Interact with Local, SSH, Telnet, and other systems as unified objects.
- **Schedule Daemons**: Create internal schedulers to run tasks periodically.
- **Automate Workflows**: Write scripts to chain commands across multiple entities.
- **Monitor & Alert**: Collect data from command output and trigger alerts based on defined thresholds.

Whether you are managing a single server or orchestrating complex tasks across a network, FatController acts as your central command hub.

## 🚀 Quickstart

### Prerequisites
- Python 3.13 or higher
- `tkinter` (usually included with Python)
- `paramiko` (for SSH support)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mattjwarren/fatcontroler.git
    cd fatcontroler/fatcontroler
    ```

2.  **Install dependencies:**
    ```bash
    pip install paramiko
    ```

3.  **Run the application:**
    ```bash
    python FatController.py
    ```

### Basic Usage

Once FatController is running, you can use the command bar at the bottom to define entities and run commands.

1.  **Define a Local Entity:**
    ```text
    define entity LOCAL MyPC
    ```

2.  **Run a command:**
    ```text
    MyPC dir
    ```

3.  **Define an SSH Entity:**
    ```text
    define entity SSH MyServer 192.168.1.100 user pass None
    MyServer ls -la
    ```

4.  **Get Help:**
    Type `help` to see a full list of commands or read `TheManual.md` for detailed documentation.

---

## 🕰️ A Note from the Developer

> "This was my first main Python program, started over 20 years ago."

FatController (originally *v0.0.1a*) was born in an era where Python 2 was king and I was just starting my journey into software development. For years, it served as a trusty tool in my day job, helping manage complex system administration tasks with a quirky but effective custom interface.

Like many passion projects, it sat dormant for a while... until now.

### 🤖 Resurrected with AI
With the help of **Google Antigravity** (an advanced AI agent), FatController is being brought back to life and modernized. We are:
- 🐍 Migrating from Python 2 to Python 3.13.
- 🖼️ Replacing the legacy `wxPython` GUI with a native `tkinter` interface.
- 🔐 Implementing modern security practices (goodbye `eval()`, hello `paramiko`!).
- 🧪 Adding comprehensive unit tests and CI/CD workflows.

### 🔮 The Future: AI Agents
The most exciting part of this resurrection is the potential for **LLM Agent Entities**. Imagine defining an entity not just for a server, but for an *AI Agent* that can reason, plan, and execute tasks autonomously within the FatController framework. 

The tool that automated my job 20 years ago is evolving to automate the jobs of the future.

---

*Copyright (c) 2005-2025 Matthew Warren*
