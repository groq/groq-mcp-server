import pytest
import os
from src.groq_shell import run_shell_command, read_file, write_file

def test_run_shell_command():
    # echo hello is cross-platform
    res = run_shell_command("echo hello")
    assert "hello" in res.lower()

def test_run_shell_command_with_cwd(temp_dir):
    # test in a temporary directory
    # create a file there first
    test_file = temp_dir / "cwd_test.txt"
    test_file.write_text("cwd_success", encoding="utf-8")
    
    # run dir (Windows) or ls (Unix) depending on OS
    cmd = "dir" if os.name == "nt" else "ls"
    res = run_shell_command(cmd, working_dir=str(temp_dir))
    assert "cwd_test.txt" in res

def test_run_shell_command_timeout():
    # ping -n 5 127.0.0.1 (Windows) or sleep 5 (Unix)
    cmd = "ping -n 5 127.0.0.1" if os.name == "nt" else "sleep 5"
    res = run_shell_command(cmd, timeout=1)
    assert "timed out" in res
    assert "exit -1" in res

def test_read_write_file(temp_dir):
    test_file = str(temp_dir / "test_rw.txt")
    write_res = write_file(test_file, "hello world from test")
    assert "Successfully wrote" in write_res
    
    read_res = read_file(test_file)
    assert read_res == "hello world from test"

def test_read_nonexistent_file():
    res = read_file("nonexistent_file_xyz_123.txt")
    assert "Error reading file" in res
