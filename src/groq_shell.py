"""
Groq Shell Module

This module provides tools for executing local shell commands, reading files, and writing files.
"""

import os
import subprocess
import locale

def decode_bytes(data: bytes) -> str:
    """Decode raw bytes into a string with fallbacks."""
    if not data:
        return ""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass
    
    preferred = locale.getpreferredencoding()
    try:
        return data.decode(preferred)
    except UnicodeDecodeError:
        pass
        
    try:
        return data.decode("gbk")
    except UnicodeDecodeError:
        pass
        
    return data.decode("utf-8", errors="replace")

def run_shell_command(command: str, working_dir: str | None = None, timeout: int = 30) -> str:
    """执行本地 shell 命令，返回 stdout/stderr 合并结果。"""
    try:
        actual_cwd = None
        if working_dir:
            actual_cwd = os.path.abspath(os.path.expanduser(working_dir))
            
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            cwd=actual_cwd,
            timeout=timeout
        )
        
        stdout = decode_bytes(result.stdout)
        stderr = decode_bytes(result.stderr)
        
        if result.returncode == 0:
            return stdout
        else:
            return f"exit {result.returncode}\n{stderr}"
            
    except subprocess.TimeoutExpired as e:
        stdout = decode_bytes(e.stdout) if e.stdout else ""
        stderr = decode_bytes(e.stderr) if e.stderr else ""
        return f"exit -1\nCommand timed out after {timeout} seconds.\nStdout: {stdout}\nStderr: {stderr}"
    except Exception as e:
        return f"exit -1\nError running command: {str(e)}"

def read_file(path: str) -> str:
    """读取本地文件内容，返回字符串。"""
    try:
        full_path = os.path.abspath(os.path.expanduser(path))
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def write_file(path: str, content: str) -> str:
    """写入本地文件，返回成功/失败消息。"""
    try:
        full_path = os.path.abspath(os.path.expanduser(path))
        # Ensure parent directory exists
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"
