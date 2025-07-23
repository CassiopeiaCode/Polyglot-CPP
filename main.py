import asyncio
import uuid
import os
import subprocess
import difflib
import logging
import json
from typing import Optional
from datetime import datetime, timedelta
from fastmcp import FastMCP

import contextlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@contextlib.asynccontextmanager
async def lifespan(mcp):
    load_cpp_files()
    cleanup_expired_files()
    yield

mcp = FastMCP(
    "Polyglot-CPP: The C++ MCP Server",
    lifespan=lifespan,
    instructions="""
This server provides a comprehensive environment for compiling, running, and analyzing C++ code. It is particularly well-suited for competitive programming and debugging tasks.

**Core Features:**
- **Compilation:** Compiles C++ code using clang++ with support for profiling and debugging flags.
- **Execution:** Runs compiled programs with standard input and captures standard output/error.
- **Timeout Control:** Enforces a 10-second execution timeout to prevent infinite loops.
- **Debugging:** Automatically enables AddressSanitizer (`-fsanitize=address`) to provide detailed error reports for memory issues like segmentation faults.
- **Profiling:** Generates a performance report using `gprof` to identify hotspots and function call times.
- **Persistence:** Compiled programs are stored and can be re-run by their unique `file_id`. Note that `file_id`s will expire and be cleaned up automatically after 24 hours.

**Available Tools:**
- `create_program`: Compiles C++ code and returns a `file_id`.
- `run_program`: Executes a previously compiled program using its `file_id`.
- `create_and_run_program`: A convenience tool that compiles and runs code in a single call.
"""
)

CPP_FILES_JSON = "cpp_files.json"

# In-memory storage for C++ files, loaded from disk
cpp_files = {}

def load_cpp_files():
    global cpp_files
    if os.path.exists(CPP_FILES_JSON):
        with open(CPP_FILES_JSON, "r") as f:
            try:
                cpp_files = json.load(f)
            except json.JSONDecodeError:
                cpp_files = {}
    else:
        cpp_files = {}

def save_cpp_files():
    with open(CPP_FILES_JSON, "w") as f:
        json.dump(cpp_files, f)

def cleanup_expired_files():
    now = datetime.now().isoformat()
    to_delete = [
        file_id for file_id, info in cpp_files.items()
        if info["expiration"] < now
    ]
    for file_id in to_delete:
        info = cpp_files.pop(file_id)
        try:
            os.remove(info["source_path"])
            os.remove(info["output_path"])
            logging.info(f"Cleaned up expired file: {file_id}")
        except OSError as e:
            logging.error(f"Error cleaning up file {file_id}: {e}")
    if to_delete:
        save_cpp_files()



async def _create_program(content: str):
    """
    Creates a C++ program, compiles it, and stores it.
    """
    file_id = str(uuid.uuid4())
    
    cpps_dir = os.path.join(os.path.dirname(__file__), "cpps")
    os.makedirs(cpps_dir, exist_ok=True)
    
    source_path = os.path.join(cpps_dir, f"{file_id}.cpp")
    output_path = os.path.join(cpps_dir, file_id)

    with open(source_path, "w") as f:
        f.write(content)

    compile_result = subprocess.run(
        ["clang++", "-pg", "-fsanitize=address", "-o", output_path, source_path],
        capture_output=True,
        text=True
    )

    if compile_result.returncode != 0:
        logging.error(f"Compilation failed for {file_id}: {compile_result.stderr}")
        os.remove(source_path)
        return {"success": False, "error": compile_result.stderr}

    expiration = (datetime.now() + timedelta(days=1)).isoformat()
    cpp_files[file_id] = {
        "output_path": output_path,
        "source_path": source_path,
        "expiration": expiration
    }
    save_cpp_files()
    logging.info(f"Successfully compiled and stored program with file_id: {file_id}")
    return {"success": True, "file_id": file_id}

@mcp.tool(description="Accepts C++ code as a string, compiles it with profiling and address sanitizer flags, and stores the binary. Returns a unique `file_id` for the compiled program, which can be used with `run_program`.")
async def create_program(content: str) -> dict:
    return await _create_program(content)

async def _run_program(file_id: str, custom_input: str = "", expected_output: Optional[str] = None):
    """
    Runs a compiled C++ program.
    """
    load_cpp_files() # Ensure we have the latest data
    if file_id not in cpp_files:
        logging.warning(f"Attempted to run non-existent file_id: {file_id}")
        return {"success": False, "error": "File ID not found."}

    file_info = cpp_files[file_id]

    if datetime.now().isoformat() > file_info["expiration"]:
        logging.info(f"File ID {file_id} has expired. Cleaning up.")
        del cpp_files[file_id]
        os.remove(file_info["source_path"])
        os.remove(file_info["output_path"])
        save_cpp_files()
        return {"success": False, "error": "File ID has expired."}

    start_time = datetime.now()
    try:
        run_result = subprocess.run(
            [file_info["output_path"]],
            input=custom_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        end_time = datetime.now()
        run_time = (end_time - start_time).total_seconds()
        run_time = (end_time - start_time).total_seconds()

        gprof_result = subprocess.run(
            ["gprof", file_info["output_path"], "gmon.out"],
            capture_output=True,
            text=True
        )
        
        # Clean up gmon.out
        if os.path.exists("gmon.out"):
            os.remove("gmon.out")

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out after 10 seconds."}

    diff_result = None
    if expected_output is not None:
        diff = difflib.unified_diff(
            expected_output.splitlines(keepends=True),
            run_result.stdout.splitlines(keepends=True),
            fromfile='expected_output',
            tofile='actual_output',
        )
        diff_result = "".join(diff)

    profiling_report = gprof_result.stdout # 修复：使用 gprof_result.stdout
    profiling_report = profiling_report.replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")[:500] 

    return {
        "success": True,
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
        "diff": diff_result,
        "run_time": run_time,
        "profiling_report": profiling_report
    }

@mcp.tool(description="Runs a compiled program identified by its `file_id`. You can provide `custom_input` and an `expected_output` to check for correctness. The tool returns the program's stdout, stderr, execution time, a diff if `expected_output` is provided, and a gprof profiling report.")
async def run_program(file_id: str, custom_input: str = "", expected_output: Optional[str] = None) -> dict:
    return await _run_program(file_id, custom_input, expected_output)

async def _create_and_run_program(content: str, custom_input: str = "", expected_output: Optional[str] = None):
    """
    Creates, compiles, and runs a C++ program.
    """
    create_response = await _create_program(content=content)
    if not create_response["success"]:
        return create_response

    file_id = create_response["file_id"]
    run_response = await _run_program(file_id=file_id, custom_input=custom_input, expected_output=expected_output)

    # # Clean up the created files immediately
    # if file_id in cpp_files:
    #     file_info = cpp_files.pop(file_id)
    #     os.remove(file_info["source_path"])
    #     os.remove(file_info["output_path"])
    #     save_cpp_files()
    
    # Combine responses
    response = {"create_result": create_response, "run_result": run_response}
    return response

@mcp.tool(description="A convenience tool that combines `create_program` and `run_program`. It compiles the given C++ `content`, runs it with `custom_input`, and returns all results, including the `file_id` for future runs. The created program is not deleted automatically.")
async def create_and_run_program(content: str, custom_input: str = "", expected_output: Optional[str] = None) -> dict:
    return await _create_and_run_program(content, custom_input, expected_output)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=53482)
