# Local Setup Guide for Windows 10 & 11

This document provides complete instructions for executing the Supplier Reliability Scoring System locally.

---

### 1. Prerequisites Installation

Download and install the following software packages:
1. **Python 3.11+**: [python.org/downloads](https://www.python.org/downloads/)
   * Ensure the **"Add python.exe to PATH"** checkbox is checked during installation.
2. **Git for Windows**: [git-scm.com/download/win](https://git-scm.com/download/win)
3. **Visual Studio Code**: [code.visualstudio.com](https://code.visualstudio.com/)

---

### 2. Environment Initialization

Launch **Windows PowerShell** as Administrator or open the built-in terminal in VS Code (`Ctrl + ~`).

```powershell
# Navigate to the workspace directory
cd supplier-reliability-scoring

# Create a virtual environment
python -m venv venv

# Set execution policy if script execution is blocked
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt