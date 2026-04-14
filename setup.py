# -*- coding: utf-8 -*-
# ============================================================
# setup.py — CureBay Auto-Setup & Model Installer
# ============================================================
# Automatically:
#   1. Checks system requirements (RAM, disk space)
#   2. Installs Python dependencies
#   3. Downloads MedGemma Q4_K_M GGUF (~2.7 GB) from HuggingFace
#   4. Warms up MiniLM embedding model cache (~80 MB)
#   5. Initialises the database
#   6. Optionally launches the backend server
#
# No Ollama required — all models run natively in Python.
#
# Usage:
#   python setup.py              — full setup + start server
#   python setup.py --check      — only check what is installed
#   python setup.py --no-server  — setup but don't start server
# ============================================================

import sys
import os
import subprocess
import platform
import shutil
import time
import argparse
import shlex
from pathlib import Path

# ── Terminal colours ──────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"

def ok(msg):   print(f"{C.GREEN}  [OK]  {msg}{C.RESET}")
def warn(msg): print(f"{C.YELLOW}  [!]   {msg}{C.RESET}")
def err(msg):  print(f"{C.RED}  [X]   {msg}{C.RESET}")
def info(msg): print(f"{C.CYAN}  -->   {msg}{C.RESET}")
def hdr(msg):  print(f"\n{C.BOLD}{C.BLUE}{'='*60}\n  {msg}\n{'='*60}{C.RESET}")


# ── OS detection ──────────────────────────────────────────────
OS   = platform.system()          # "Windows" | "Linux" | "Darwin"
ARCH = platform.machine().lower() # "AMD64" | "x86_64" | "arm64" / "aarch64"

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / ".venv"


def _venv_python_path(venv_dir: Path) -> Path:
    if OS == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _is_running_inside_venv(venv_dir: Path) -> bool:
    try:
        exe = Path(sys.executable).resolve()
        vdir = venv_dir.resolve()
        return exe.is_relative_to(vdir)
    except Exception:
        # Conservative fallback
        return str(venv_dir).lower() in str(sys.executable).lower()


def ensure_project_venv_and_reexec(no_venv: bool = False, recreate: bool = False):
    """Ensure setup runs inside BASE_DIR/.venv (reduces Windows install issues)."""
    if no_venv:
        return

    if _is_running_inside_venv(VENV_DIR):
        return

    if recreate and VENV_DIR.exists():
        info(f"Recreating virtual environment: {VENV_DIR}")
        try:
            shutil.rmtree(VENV_DIR, ignore_errors=False)
        except Exception as e:
            err(f"Failed to delete existing venv: {e}")
            err("Close any terminals/apps using the venv and try again.")
            sys.exit(1)

    venv_py = _venv_python_path(VENV_DIR)
    if not venv_py.exists():
        hdr("Bootstrapping Virtual Environment (.venv)")
        info("Creating .venv (first time only)...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True, cwd=str(BASE_DIR))
            ok("Virtual environment created.")
        except subprocess.CalledProcessError:
            err("Failed to create virtual environment.")
            sys.exit(1)

    info(f"Re-launching setup using: {venv_py}")
    filtered_args = [a for a in sys.argv[1:] if a != "--recreate-venv"]
    raise SystemExit(subprocess.call([str(venv_py), str(__file__), *filtered_args], cwd=str(BASE_DIR)))

# ── Model info ────────────────────────────────────────────────
MEDGEMMA_REPO      = "unsloth/medgemma-1.5-4b-it-GGUF"
MEDGEMMA_FILENAME  = "medgemma-1.5-4b-it-Q4_K_M.gguf"
MEDGEMMA_LOCAL_DIR = BASE_DIR / "models" / "medgemma"
MEDGEMMA_LOCAL_PATH = MEDGEMMA_LOCAL_DIR / MEDGEMMA_FILENAME

MINIML_MODEL_NAME  = "all-MiniLM-L6-v2"

MINIMUM_RAM_GB     = 4
MINIMUM_DISK_GB    = 5


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

def get_ram_gb() -> float:
    """Get total system RAM in GB."""
    try:
        import psutil
        return psutil.virtual_memory().total / (1024**3)
    except ImportError:
        # Fallback for systems without psutil
        if OS == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "computersystem", "get", "TotalPhysicalMemory", "/value"],
                    capture_output=True, text=True, check=True,
                )
                for line in result.stdout.strip().split("\n"):
                    if "TotalPhysicalMemory" in line:
                        return int(line.split("=")[1]) / (1024**3)
            except Exception:
                pass
        elif OS in ("Linux", "Darwin"):
            try:
                with open("/proc/meminfo") as f:
                    for line in f:
                        if "MemTotal" in line:
                            return int(line.split()[1]) / (1024**2)
            except Exception:
                pass
    return 0.0


def get_free_disk_gb(path: Path) -> float:
    """Get free disk space in GB for the given path."""
    try:
        usage = shutil.disk_usage(str(path))
        return usage.free / (1024**3)
    except Exception:
        return 0.0


# ════════════════════════════════════════════════════════════
# STEP 1 — Check system requirements
# ════════════════════════════════════════════════════════════

def check_system_requirements():
    hdr("Step 1/5 — Checking System Requirements")

    # RAM check
    ram = get_ram_gb()
    if ram > 0:
        if ram >= MINIMUM_RAM_GB:
            ok(f"RAM: {ram:.1f} GB (minimum {MINIMUM_RAM_GB} GB)")
        else:
            warn(f"RAM: {ram:.1f} GB — below recommended {MINIMUM_RAM_GB} GB")
            warn("MedGemma may run slowly. Consider using a device with more RAM.")
    else:
        warn("Could not detect RAM size.")

    # Disk check
    disk = get_free_disk_gb(BASE_DIR)
    if disk > 0:
        if disk >= MINIMUM_DISK_GB:
            ok(f"Free disk: {disk:.1f} GB (minimum {MINIMUM_DISK_GB} GB)")
        else:
            err(f"Free disk: {disk:.1f} GB — need at least {MINIMUM_DISK_GB} GB!")
            err("Free up disk space before proceeding.")
            sys.exit(1)
    else:
        warn("Could not detect free disk space.")

    # Python version (core stack supports 3.10-3.13)
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if (3, 10) <= sys.version_info < (3, 14):
        ok(f"Python: {py_ver}")
    else:
        err(f"Python: {py_ver} — use Python 3.10, 3.11, 3.12, or 3.13 for this project.")
        err("Reason: several ML dependencies are not validated on this Python version.")
        err("Install Python 3.11 or 3.12 for the most stable experience.")
        sys.exit(1)

    print(f"  OS: {OS} / {ARCH}")


# ════════════════════════════════════════════════════════════
# STEP 2 — Install Python dependencies
# ════════════════════════════════════════════════════════════

def ensure_python_deps():
    hdr("Step 2/5 — Installing Python Dependencies")

    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        warn("requirements.txt not found — skipping pip install.")
        return

    # Install core requirements first so optional heavyweight packages
    # don't block the full setup on platforms missing native build tools.
    core_reqs = []
    optional_reqs = []
    pip_install_options = []

    for raw in req_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0].strip()
        if not line:
            continue
        if line.startswith("-"):
            # Allow pip options in requirements.txt (e.g. --extra-index-url ...)
            # by expanding them into proper argv tokens.
            try:
                pip_install_options.extend(shlex.split(line))
            except ValueError:
                warn(f"Ignoring malformed pip option line in requirements: {line}")
            continue
        core_reqs.append(line)

    default_llama_cpp_index = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
    if "--extra-index-url" not in pip_install_options:
        pip_install_options.extend(["--extra-index-url", default_llama_cpp_index])

    # Optional NeMo dependency for offline ASR.
    # Keep this outside requirements.txt so base install remains robust.
    if (3, 10) <= sys.version_info < (3, 13):
        optional_reqs.append("nemo_toolkit[asr]>=1.22.0")
    else:
        warn("Skipping optional NeMo install on this Python version (requires 3.10-3.12).")

    if core_reqs:
        info("Installing core requirements (this can take several minutes)...")
        # Pre-install setuptools constraint for PyTorch compatibility BEFORE main install
        # This avoids the setuptools upgrade/downgrade churn that triggers WinError 32
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "setuptools<82", "--quiet"],
                check=True,
            )
        except subprocess.CalledProcessError:
            warn("Could not pre-install setuptools constraint; continuing anyway")

        max_retries = 2
        retry_delay = 3  # seconds

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    info(f"Retry attempt {attempt}/{max_retries}...")
                    time.sleep(retry_delay)

                subprocess.run(
                    [
                        sys.executable, "-m", "pip", "install",
                        "--prefer-binary",
                        *pip_install_options,
                        *core_reqs
                    ],
                    check=True,
                )
                ok("Core Python dependencies installed.")
                break  # Success - exit retry loop
            except subprocess.CalledProcessError as e:
                if attempt < max_retries:
                    warn(f"Install failed (attempt {attempt + 1}), retrying in {retry_delay}s...")
                else:
                    err("Core dependency installation failed.")
            if OS == "Windows":
                warn("If the error mentions CMake/NMake or Visual C++, install Build Tools:")
                warn("  https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            if sys.version_info >= (3, 13):
                warn("Python 3.13 has limited wheel support for some ML packages in this project.")
                warn("Use Python 3.11 and rerun setup for best compatibility.")
            err("Run this for detailed logs:")
            err(f"  {sys.executable} -m pip install --prefer-binary -r {req_file} --verbose")
            sys.exit(1)

    # NeMo ASR is optional for offline voice and may require native build tools.
    for req in optional_reqs:
        info(f"Installing optional package: {req}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--prefer-binary", req],
                check=True,
            )
            ok(f"Optional package installed: {req}")
        except subprocess.CalledProcessError:
            warn(f"Optional package skipped: {req}")
            warn("Offline NeMo STT will be unavailable until native build tools are installed.")
            if OS == "Windows":
                warn("Install Microsoft C++ Build Tools, then re-run setup to enable NeMo.")

    ok("Python dependency step completed.")


# ════════════════════════════════════════════════════════════
# STEP 3 — Download MedGemma GGUF
# ════════════════════════════════════════════════════════════

def download_medgemma():
    hdr("Step 3/5 — Downloading MedGemma Q4_K_M GGUF (~2.7 GB)")

    if MEDGEMMA_LOCAL_PATH.exists():
        size_gb = MEDGEMMA_LOCAL_PATH.stat().st_size / (1024**3)
        ok(f"MedGemma already downloaded ({size_gb:.1f} GB)")
        return

    MEDGEMMA_LOCAL_DIR.mkdir(parents=True, exist_ok=True)

    info(f"Repo: {MEDGEMMA_REPO}")
    info(f"File: {MEDGEMMA_FILENAME}")
    info(f"Dest: {MEDGEMMA_LOCAL_PATH}")
    info("This download is resumable — if it stops, run setup.py again.")
    print()

    try:
        from huggingface_hub import hf_hub_download

        downloaded_path = hf_hub_download(
            repo_id=MEDGEMMA_REPO,
            filename=MEDGEMMA_FILENAME,
            local_dir=str(MEDGEMMA_LOCAL_DIR),
            local_dir_use_symlinks=False,
        )

        # Verify file exists
        if Path(downloaded_path).exists():
            size_gb = Path(downloaded_path).stat().st_size / (1024**3)
            ok(f"MedGemma downloaded: {size_gb:.1f} GB")
        else:
            err("Download completed but file not found!")

    except ImportError:
        err("huggingface-hub not installed. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface-hub"], check=True)
        info("Please re-run: python setup.py")
        sys.exit(1)
    except Exception as e:
        err(f"MedGemma download failed: {e}")
        print()
        info("Manual download:")
        info(f"  1. Go to: https://huggingface.co/{MEDGEMMA_REPO}")
        info(f"  2. Download: {MEDGEMMA_FILENAME}")
        info(f"  3. Save to:  {MEDGEMMA_LOCAL_PATH}")


# ════════════════════════════════════════════════════════════
# STEP 4 — Warm up embedding model cache
# ════════════════════════════════════════════════════════════

def warmup_embedding_model():
    hdr("Step 4/5 — Warming Up Embedding Model (~80 MB)")

    try:
        info(f"Loading {MINIML_MODEL_NAME} (auto-downloads on first use)...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MINIML_MODEL_NAME)
        # Quick test
        test_embed = model.encode("test health symptoms")
        ok(f"MiniLM loaded: {MINIML_MODEL_NAME} ({len(test_embed)}-dim)")
    except ImportError:
        warn("sentence-transformers not installed — will download on first app startup.")
    except Exception as e:
        warn(f"Embedding warmup failed: {e} — will retry on first app startup.")


# ════════════════════════════════════════════════════════════
# STEP 5 — Initialise database
# ════════════════════════════════════════════════════════════

def ensure_database():
    hdr("Step 5/5 — Initialising Database")
    try:
        sys.path.insert(0, str(BASE_DIR))
        from database.sqlite_db import init_db
        init_db()
        ok("SQLite database ready.")
    except Exception as e:
        warn(f"Database init skipped: {e}")


# ════════════════════════════════════════════════════════════
# CHECK MODE
# ════════════════════════════════════════════════════════════

def check_status():
    hdr("CureBay v2.0 - System Status Check")

    # System
    ram = get_ram_gb()
    disk = get_free_disk_gb(BASE_DIR)
    if ram > 0:
        ok(f"RAM:           {ram:.1f} GB")
    if disk > 0:
        ok(f"Free disk:     {disk:.1f} GB")
    ok(f"Python:        {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()

    # MedGemma GGUF
    if MEDGEMMA_LOCAL_PATH.exists():
        size_gb = MEDGEMMA_LOCAL_PATH.stat().st_size / (1024**3)
        ok(f"MedGemma GGUF:     downloaded ({size_gb:.1f} GB)")
    else:
        err(f"MedGemma GGUF:     NOT found at {MEDGEMMA_LOCAL_PATH}")
        info("Run: python setup.py")

    # MiniLM
    try:
        from sentence_transformers import SentenceTransformer
        ok(f"MiniLM embed:      available ({MINIML_MODEL_NAME})")
    except ImportError:
        warn("MiniLM embed:      sentence-transformers not installed")

    # llama-cpp-python
    try:
        import llama_cpp
        ok("llama-cpp-python:  installed")
    except ImportError:
        err("llama-cpp-python:  NOT installed")

    # torch + torchvision
    try:
        import torch, torchvision
        ok(f"PyTorch:           {torch.__version__}")
        ok(f"torchvision:       {torchvision.__version__}")
    except ImportError:
        err("PyTorch/torchvision: NOT installed")

    # NeMo (AI4Bharat)
    try:
        import nemo
        ok("NeMo toolkit:      installed (IndicConformer STT)")
    except ImportError:
        warn("NeMo toolkit:      not installed (offline STT unavailable)")

    # OpenCV
    try:
        import cv2
        ok(f"OpenCV:            {cv2.__version__} (rPPG vitals)")
    except ImportError:
        warn("OpenCV:            not installed (rPPG unavailable)")

    # Python deps
    print()
    try:
        import fastapi, sqlalchemy, chromadb
        ok("Core Python deps:  installed")
    except ImportError as e:
        err(f"Python dependencies: missing — {e}")

    # Database
    db_path = BASE_DIR / "curebay.db"
    if db_path.exists():
        ok(f"SQLite database:   exists ({db_path.stat().st_size // 1024} KB)")
    else:
        warn("SQLite database:   not created yet (will be created on first run)")

    # ChromaDB
    chroma_dir = BASE_DIR / "chroma_data"
    if chroma_dir.exists():
        ok("ChromaDB:          data directory exists")
    else:
        warn("ChromaDB:          no data yet (will be seeded on first run)")

    print()


# ════════════════════════════════════════════════════════════
# LAUNCH SERVER
# ════════════════════════════════════════════════════════════

def launch_server():
    hdr("Launching CureBay Backend Server")
    print(f"  {C.BOLD}API:   http://localhost:8000{C.RESET}")
    print(f"  {C.BOLD}Docs:  http://localhost:8000/docs{C.RESET}")
    print(f"\n  Press Ctrl+C to stop the server.\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(BASE_DIR),
        )
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}  Server stopped.{C.RESET}")


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

def main():
    # Enable ANSI colours on Windows
    if OS == "Windows":
        os.system("")

    parser = argparse.ArgumentParser(
        description="CureBay AI Health Assistant — Auto Setup (v2.0, No Ollama)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                # Full setup + start server
  python setup.py --check        # Show what is installed
  python setup.py --no-server    # Setup but don't start server
        """,
    )
    parser.add_argument("--check",     action="store_true", help="Show installation status")
    parser.add_argument("--no-server", action="store_true", help="Setup without starting server")
    parser.add_argument("--no-venv", action="store_true", help="Do not create/use .venv; run in current Python")
    parser.add_argument("--recreate-venv", action="store_true", help="Delete and recreate .venv before installing")
    args = parser.parse_args()

    # Always run installs in a dedicated project venv (unless explicitly disabled).
    # This avoids system-Python pollution and reduces Windows file-lock failures.
    ensure_project_venv_and_reexec(no_venv=args.no_venv, recreate=args.recreate_venv)

    print(f"""
{C.BOLD}{C.CYAN}
+===========================================================+
|       CureBay AI Health Assistant -- Auto Setup v2.0      |
|  Offline-First Healthcare for Rural ASHA Workers          |
|  Architecture: MedGemma + MiniLM + IndicConformer + rPPG  |
|  No Ollama Required                                       |
+===========================================================+
{C.RESET}""")

    if args.check:
        check_status()
        return

    # Full setup flow
    check_system_requirements()
    ensure_python_deps()
    download_medgemma()
    warmup_embedding_model()
    ensure_database()

    print(f"\n{C.BOLD}{C.GREEN}{'='*60}")
    print("  [DONE]  Setup complete! CureBay backend is ready.")
    print(f"  Total model size: ~3.4 GB (down from ~10 GB with Ollama)")
    print(f"{'='*60}{C.RESET}\n")

    if not args.no_server:
        launch_server()
    else:
        info("Run 'python setup.py' (without --no-server) to start the server, or:")
        info("  uvicorn main:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
