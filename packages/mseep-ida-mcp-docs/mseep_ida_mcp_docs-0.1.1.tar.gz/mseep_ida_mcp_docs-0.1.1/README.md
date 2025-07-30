# IDA Pro MCP Documentation and Utilities

This project provides documentation and utilities for working with IDA Pro through MCP (Machine Code Processor).

This project was a for-fun for myself to learn how to use MCP, it is not meant for real-life use.

## ⚠️ System Requirements

- IDA Pro installation is required
- Python 3.8 or higher

## 🔧 Prerequisites

1. **IDA Pro Installation**
   - Ensure you have a working installation of IDA Pro
   - Set the `IDADIR` environment variable to point to your IDA Pro installation directory
     ```powershell
     # Example (PowerShell):
     $env:IDADIR = "C:\Program Files\IDA Pro"
     # or set it permanently through Windows System Properties > Environment Variables
     ```


## 📥 Installation

1. **Install Poetry** (if not already installed)
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```
   OR 
   ```powershell
   pipx install poetry
   ```

2. **Install Dependencies**
   ```powershell
   poetry install
   ```

## 🚀 Setting up the MCP Server
1. Cursor MCP configuration setup
   ```json
   "ida-pro-doc": {
      "command": "<venv_python_path>/python.exe",
      "args": [
        "<path_to_project>/server.py"
      ]
    }
   ```

## 🔍 Troubleshooting

1. If you encounter issues with MCP server:
   - Ensure `IDADIR` environment variable is correctly set
   - Verify IDA Pro installation is working properly
   - Check if any antivirus software is blocking the connections

2. Common Issues:
   - "IDADIR not found": Set the environment variable as shown in Prerequisites
   - Connection refused: Make sure no other instance of MCP server is running
   - **Windows only**: This project has been tested and is supported only on Windows systems
   - **Cursor only**: This project has only been tested inside of cursor but should work with other software.

## 📝 Notes

- The server uses idalib and opening ida pro is not required! (this is supported only after IDA 9.0)
- Always ensure IDA Pro is properly closed before starting the MCP server
- The MCP server needs to be running for any IDA Pro automation scripts to work
- This project is Windows-only at the moment - other operating systems are not supported but should work (with a little tweaking)
- This is a rough stupid implementation but it works for my tests, it allows the LLM to better understand the api of ida-pro it's accessible to,
  this will help developing plugins and scripts for ida!

**For any and all questions feel free to reach out to me at sysc4lls@gmai.com**

## 📄 License

MIT License

Copyright (c) 2024 IDA Pro MCP Documentation and Utilities
