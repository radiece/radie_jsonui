#!/usr/bin/env bash
# verify.sh – Production-ready verification with caching, task selection, and structured logs.
# Features:
# - Tasks: quality | format | ruff | flake8 | isort | mypy | pyright | deprecations | circular | unit | e2e | tests
# - Flags: --skip-tests (skip unit/e2e) | --no-cache (disable caching) | -h/--help
# - Deterministic Python-based hashing (no eval, no GNU sort), includes tool versions in cache key.
# - Robust error handling with traps and JSON status for AI agents (.cache/verify/last_run.json).

set -euo pipefail

# Resolve script directory and run from repo root
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Logging and state
CACHE_DIR=".cache/verify"
LOG_DIR="$CACHE_DIR/logs"
RUN_JSON="$CACHE_DIR/last_run.json"
mkdir -p "$LOG_DIR"

# Global run metadata
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
START_EPOCH="$(date -u +%s)"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"; }

# Structured error handler for AI agents
_run_status="{}"
_json_escape() { python3 - <<'PY' "$1"
import json,sys
print(json.dumps(sys.argv[1]))
PY
}
append_status() {
  # name status start end exit_code log_file command
  local name="$1"; shift
  local status="$1"; shift
  local start="$1"; shift
  local end="$1"; shift
  local code="$1"; shift
  local logf="$1"; shift
  local cmd="$*"
  local esc_cmd; esc_cmd=$(_json_escape "$cmd")
  local esc_log; esc_log=$(_json_escape "$logf")
  python3 - "$RUN_JSON" "$name" "$status" "$start" "$end" "$code" "$esc_log" "$esc_cmd" <<'PY'
import json,sys,os
path,name,status,start,end,code,logf,cmd = sys.argv[1:]
start=int(start); end=int(end); code=int(code)
entry={"name":name,"status":status,"start":start,"end":end,"exit_code":code,"log":json.loads(logf),"command":json.loads(cmd)}
run={}
if os.path.exists(path):
    try:
        with open(path,"r") as f: run=json.load(f)
    except Exception:
        run={}
if "run_id" not in run: run["run_id"] = os.environ.get("RUN_ID","")
if "started_at" not in run: run["started_at"] = int(os.environ.get("START_EPOCH","0"))
steps=run.get("steps",[])
# replace if same name exists
steps=[s for s in steps if s.get("name")!=name]
steps.append(entry)
run["steps"]=steps
with open(path,"w") as f: json.dump(run,f,sort_keys=True)
print()
PY
}

handle_error() {
  local exit_code=$?
  local line_no=${BASH_LINENO:-0}
  local cmd="${BASH_COMMAND:-unknown}"
  echo ""
  echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Command failed at line ${line_no}: ${cmd} (exit ${exit_code})"
  # Mark run end
  python3 - "$RUN_JSON" <<'PY'
import json,os,sys,time
p=sys.argv[1]
try:
    with open(p,"r") as f: run=json.load(f)
except Exception:
    run={}
run["finished_at"]=int(time.time())
run["status"]="failed"
with open(p,"w") as f: json.dump(run,f,sort_keys=True)
print()
PY
  exit "$exit_code"
}

finish_ok() {
  python3 - "$RUN_JSON" <<'PY'
import json,os,sys,time
p=sys.argv[1]
try:
    with open(p,"r") as f: run=json.load(f)
except Exception:
    run={}
run["finished_at"]=int(time.time())
run["status"]="success"
with open(p,"w") as f: json.dump(run,f,sort_keys=True)
print()
PY
}

trap 'handle_error' ERR
trap 'finish_ok' EXIT

usage() {
  cat <<'EOF'
Usage:
  verify.sh [PACKAGE] [--skip-tests] [--no-cache] [task ...]
Arguments:
  PACKAGE        Package name (e.g., config-service) - optional, runs in workspace root if not provided
Tasks:
  quality | format | ruff | flake8 | isort | mypy | pyright | deprecations | circular | unit | e2e | tests
Flags:
  --skip-tests   Skip unit/e2e test execution
  --no-cache     Disable hashing cache (force selected tasks)
  -h, --help     Show help
EOF
}

# Flags and package
RUN_TESTS=1
USE_CACHE=1
TASKS=()
PACKAGE=""

# Parse first positional arg as package name if it doesn't start with --
if [ $# -gt 0 ] && [[ "$1" != --* ]] && [[ "$1" != -* ]]; then
  PACKAGE="$1"
  shift
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-tests) RUN_TESTS=0; shift ;;
    --no-cache)   USE_CACHE=0; shift ;;
    -h|--help)    usage; exit 0 ;;
    --)           shift; break ;;
    -* )          echo "Unknown option: $1"; usage; exit 2 ;;
    * )           TASKS+=("$1"); shift ;;
  esac
done

# If package specified, change to package directory
if [ -n "$PACKAGE" ]; then
  PACKAGE_DIR=""
  if [ -d "platform/$PACKAGE" ]; then
    PACKAGE_DIR="platform/$PACKAGE"
  elif [ -d "backend/$PACKAGE" ]; then
    PACKAGE_DIR="backend/$PACKAGE"
  elif [ -d "$PACKAGE" ]; then
    PACKAGE_DIR="$PACKAGE"
  else
    echo "ERROR: Package '$PACKAGE' not found in platform/, backend/, or current directory"
    exit 1
  fi

  log "📦 Verifying package: $PACKAGE (in $PACKAGE_DIR)"
  cd "$PACKAGE_DIR" || exit 1
  # Reset CACHE_DIR and LOG_DIR to be relative to package
  CACHE_DIR=".cache/verify"
  LOG_DIR="$CACHE_DIR/logs"
  RUN_JSON="$CACHE_DIR/last_run.json"
  mkdir -p "$LOG_DIR"
else
  log "📦 Verifying workspace root"
fi


# Activate venv
# Activate venv
log "Step 1: Activate virtual environment"
if [ -f ".venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
  log "✅ Virtual environment activated (local)"
elif [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.venv/bin/activate"
  log "✅ Virtual environment activated (workspace)"
else
  echo "{}" > "$RUN_JSON"
  error_exit() { echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1"; exit 1; }
  error_exit "Virtual environment activation script not found in .venv or $SCRIPT_DIR/.venv"
fi

# Python-based hashing (portable, deterministic)
py_hash_scope() {
  # args: scope_name (quality|unit|e2e)
  python3 - "$1" <<'PY'
import hashlib, os, sys, fnmatch, subprocess, json, pathlib
scope=sys.argv[1]
root=os.getcwd()

def version(cmd):
    try:
        out=subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return out.decode("utf-8","ignore").strip()
    except Exception:
        return ""

# Inputs per scope
include_dirs=[]
if os.path.isdir("src"): include_dirs.append("src")
if os.path.isdir("app"): include_dirs.append("app")
if os.path.isdir("tests"): include_dirs.append("tests")
include_globs=["*.py"]
exclude_dirnames={".git",".venv","__pycache__",".mypy_cache",".ruff_cache",".pytest_cache"}
extra_top_files=["pyproject.toml","setup.cfg","tox.ini",".flake8","mypy.ini","ruff.toml","requirements.txt","requirements-dev.txt","main.py"]

if scope=="unit":
    e2e_prefix=os.path.join("tests","e2e")+os.sep
elif scope=="e2e":
    e2e_prefix=None
else:
    e2e_prefix=None

h=hashlib.sha256()
def add(b): h.update(b if isinstance(b,(bytes,bytearray)) else str(b).encode())

# Tool version fingerprint
if scope=="quality":
    versions=[("python",version("python --version")),
              ("black",version("black --version")),
              ("ruff",version("ruff --version")),
              ("flake8",version("flake8 --version")),
              ("isort",version("isort --version")),
              ("mypy",version("mypy --version")),
              ("pyright",version("pyright --version || basedpyright --version || true"))]
elif scope in ("unit","e2e"):
    versions=[("python",version("python --version")),
              ("pytest",version("pytest --version"))]
else:
    versions=[]

add(("VERSIONS",tuple(versions)).__repr__())

files=[]
for d in include_dirs:
    if not os.path.isdir(d): continue
    for rootdir, dirs, fs in os.walk(d):
        # prune excluded dirs
        dirs[:]=[x for x in dirs if x not in exclude_dirnames]
        # prune e2e for unit scope during hashing (so unit cache doesn't depend on e2e)
        if scope=="unit" and (rootdir+os.sep).startswith(os.path.join("tests","e2e")+os.sep):
            dirs[:] = []
            fs = []
        if scope=="e2e" and not (rootdir+os.sep).startswith(os.path.join("tests","e2e")+os.sep) and rootdir.startswith("tests"):
            # only include e2e tests for e2e scope from tests/, but always include src
            pass
        for f in fs:
            rel=os.path.join(rootdir,f)
            if any(fnmatch.fnmatch(f, pat) for pat in include_globs):
                if scope=="unit" and rel.startswith(os.path.join("tests","e2e")+os.sep):
                    continue
                if scope=="e2e" and rel.startswith("tests") and not rel.startswith(os.path.join("tests","e2e")+os.sep):
                    continue
                files.append(rel)

# Add extra config files for quality scope
if scope=="quality":
    for f in extra_top_files:
        if os.path.isfile(f): files.append(f)

# Deterministic order
files=sorted(set(files))
add(("COUNT",len(files)).__repr__())

for p in files:
    add(("PATH",p).__repr__())
    try:
        with open(p,"rb") as fp:
            while True:
                chunk=fp.read(1<<20)
                if not chunk: break
                h.update(chunk)
    except Exception:
        # If unreadable, still include its path in the hash to force rerun
        add(("UNREADABLE",p).__repr__())

print(h.hexdigest())
PY
}

# Cache helpers
skip_if_unchanged() {
  local scope="$1"; local cur_hash
  cur_hash="$(py_hash_scope "$scope")"
  eval "${scope^^}_HASH=\"$cur_hash\""
  [ "$USE_CACHE" -eq 0 ] && return 1
  local hf="$CACHE_DIR/$scope.hash"
  local okf="$CACHE_DIR/$scope.ok"
  if [ -f "$hf" ] && [ -f "$okf" ] && [ "$cur_hash" = "$(cat "$hf")" ]; then
    local saved_file="$CACHE_DIR/${scope}.time"
    local saved_sec=""
    if [ -f "$saved_file" ]; then
      saved_sec="$(cat "$saved_file" 2>/dev/null || true)"
    fi
    if [ -n "$saved_sec" ]; then
      log "🧠 Cache hit for '$scope' — result served from cache, ⏱️ saved ${saved_sec}s."
    else
      log "🧠 Cache hit for '$scope' — result served from cache."
    fi
    # record a skipped step entry for visibility
    local log_file="$LOG_DIR/${scope}.log"; : > "$log_file"
    local now_ts; now_ts=$(date -u +%s)
    append_status "$scope" "cached" "$now_ts" "$now_ts" 0 "$log_file" "cache-hit saved=${saved_sec}s"
    return 0
  fi
  echo "$cur_hash" > "$hf"
  return 1
}
mark_ok() { touch "$CACHE_DIR/$1.ok"; }

# Runner with per-step logs and JSON status
run_step() {
  local name="$1"; shift
  local log_file="$LOG_DIR/${name}.log"
  : > "$log_file"
  local start_ts end_ts exit_code
  start_ts=$(date -u +%s)
  if "$@" > >(tee -a "$log_file") 2> >(tee -a "$log_file" >&2); then
    exit_code=0
  else
    exit_code=$?
  fi
  end_ts=$(date -u +%s)
  append_status "$name" "$([ "$exit_code" -eq 0 ] && echo success || echo failed)" "$start_ts" "$end_ts" "$exit_code" "$log_file" "$*"
  if [ "$exit_code" -ne 0 ]; then
    echo "Step '$name' failed. See: $log_file"
    return "$exit_code"
  fi
}

# Individual task functions
# Individual task functions with flexible directory detection
get_python_dirs() {
  local dirs=()
  [ -d "src" ] && dirs+=("src/")
  [ -d "app" ] && dirs+=("app/")
  [ -d "tests" ] && dirs+=("tests/")
  [ -f "main.py" ] && dirs+=("main.py")
  echo "${dirs[@]}"
}

task_format() {
  local dirs; dirs=$(get_python_dirs)
  [ -z "$dirs" ] && { log "⚠️ No Python directories found; skipping format"; return 0; }
  log "Run black on: $dirs"
  run_step format uv run black $dirs
}

task_ruff() {
  local dirs; dirs=$(get_python_dirs)
  [ -z "$dirs" ] && { log "⚠️ No Python directories found; skipping ruff"; return 0; }
  log "Run ruff --fix on: $dirs"
  run_step ruff uv run ruff check $dirs --fix
}

task_flake8() {
  local dirs; dirs=$(get_python_dirs)
  [ -z "$dirs" ] && { log "⚠️ No Python directories found; skipping flake8"; return 0; }
  log "Run flake8 on: $dirs"
  run_step flake8 uv run flake8 $dirs
}

task_isort() {
  local dirs; dirs=$(get_python_dirs)
  [ -z "$dirs" ] && { log "⚠️ No Python directories found; skipping isort"; return 0; }
  log "Run isort on: $dirs"
  run_step isort uv run isort $dirs
}

task_mypy() {
  log "Run mypy via uv (to use correct Python environment)"
  if [ -f "mypy.ini" ] || [ -f "pyproject.toml" ]; then
    # Use uv run to ensure mypy sees the correct virtual environment
    run_step mypy uv run mypy .
  else
    log "⚠️ No mypy config found; skipping mypy"
  fi
}

task_pyright() {
  local dirs; dirs=$(get_python_dirs)
  [ -z "$dirs" ] && { log "⚠️ No Python directories found; skipping pyright"; return 0; }
  log "Run pyright on: $dirs"
  run_step pyright uv run pyright $dirs --level error
}

task_deprecations() {
  log "Run memestra (if installed)"
  if command -v memestra >/dev/null 2>&1; then
    # Skip memestra on Python >= 3.13 due to known upstream crash (beniget/ast incompatibility)
    PY_MAJ_MIN=$(python - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)
    case "$PY_MAJ_MIN" in
      3.13|3.14|3.15)
        log "⚠️ Skipping memestra on Python $PY_MAJ_MIN due to known upstream issues"
        local now_ts; now_ts=$(date -u +%s)
        local log_file="$LOG_DIR/deprecations.log"; : > "$log_file"
        append_status deprecations skipped "$now_ts" "$now_ts" 0 "$log_file" "memestra skipped on Python $PY_MAJ_MIN"
        ;;
      *)
        run_step deprecations bash -c "memestra main.py && find src tests -name '*.py' -print0 | xargs -0 -n1 memestra"
        ;;
    esac
  else
    log "⚠️ memestra not found; skipping deprecations"
  fi
}
task_circular() {
  log "Check circular dependencies"
  cat > check_circular.py <<'EOPY'
import os, sys
from collections import defaultdict
class DependencyGraph:
    def __init__(self): self.graph = defaultdict(set)
    def add_dependency(self, m, d): self.graph[m].add(d)
    def _visit(self, m, temp, perm, stack):
        if m in perm: return False
        if m in temp:
            cycle = stack[stack.index(m):] + [m]
            print(f"Circular dependency detected: {' -> '.join(cycle)}"); return True
        temp.add(m); stack.append(m)
        for d in self.graph.get(m, []):
            if self._visit(d, temp, perm, stack): return True
        temp.remove(m); perm.add(m); stack.pop(); return False
    def has_circular_dependency(self):
        temp, perm = set(), set()
        for n in self.graph:
            if self._visit(n, temp, perm, []): return True
        return False
def find_python_files(start):
    for r,dirs,fs in os.walk(start):
        for ex in ('.git','.venv','__pycache__','.mypy_cache','.ruff_cache','.pytest_cache'):
            if ex in dirs: dirs.remove(ex)
        for f in fs:
            if f.endswith('.py'): yield os.path.join(r,f)
def parse_imports(fp):
    imports=set()
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s=line.strip()
            if s.startswith('import '):
                parts=s.split()
                if len(parts)>=2:
                    mod=parts[1].split(',')[0]
                    mod=mod.split('as')[0].strip()
                    imports.add(mod)
            elif s.startswith('from '):
                parts=s.split()
                if len(parts)>=4 and parts[2]=='import':
                    imports.add(parts[1].strip())
    return imports
base="src"; g=DependencyGraph()
mods={f: os.path.relpath(f,base).replace(os.sep,".").rstrip('.py') for f in find_python_files(base)}
mods={f: (m[:-3] if m.endswith('.py') else m) for f,m in mods.items()}
for fp,m in mods.items():
    for imp in parse_imports(fp):
        if imp in mods.values(): g.add_dependency(m, imp)
if g.has_circular_dependency():
    print("❌ Circular dependencies found."); sys.exit(1)
else:
    print("✅ No circular dependencies detected.")
EOPY
  run_step circular python check_circular.py
  rm -f check_circular.py
}

task_quality() {
  if skip_if_unchanged "quality"; then
    log "✅ Quality phase up-to-date"; return
  fi
  local __start_ts __end_ts
  __start_ts=$(date -u +%s)
  task_isort
  task_format
  task_ruff
  task_flake8
  task_mypy
  task_pyright
  task_deprecations
  task_circular
  mark_ok "quality"
  __end_ts=$(date -u +%s)
  echo "$((__end_ts-__start_ts))" > "$CACHE_DIR/quality.time"
}

task_unit() {
  if [ "$RUN_TESTS" -eq 0 ]; then log "⏭️  --skip-tests active; skipping unit"; return; fi
  if skip_if_unchanged "unit"; then
    log "✅ Unit tests up-to-date"; return
  fi
  log "Run unit tests (excluding tests/e2e) with coverage check"
  local __start_ts __end_ts
  __start_ts=$(date -u +%s)
  run_step unit uv run pytest --maxfail=1 --disable-warnings --ignore=tests/e2e tests
  mark_ok "unit"
  __end_ts=$(date -u +%s)
  echo "$((__end_ts-__start_ts))" > "$CACHE_DIR/unit.time"
}

task_e2e() {
  if [ "$RUN_TESTS" -eq 0 ]; then log "⏭️  --skip-tests active; skipping e2e"; return; fi
  if [ ! -d "tests/e2e" ]; then log "ℹ️ tests/e2e not found; skipping e2e"; return; fi
  if skip_if_unchanged "e2e"; then
    log "✅ e2e tests up-to-date"; return
  fi
  log "Run e2e tests (tests/e2e)"
  local __start_ts __end_ts
  __start_ts=$(date -u +%s)
  run_step e2e uv run pytest -q --maxfail=1 --disable-warnings tests/e2e
  mark_ok "e2e"
  __end_ts=$(date -u +%s)
  echo "$((__end_ts-__start_ts))" > "$CACHE_DIR/e2e.time"
}

task_tests() { task_unit; task_e2e; }

run_selected_task() {
  case "$1" in
    quality) task_quality ;;
    format) task_format ;;
    ruff) task_ruff ;;
    flake8) task_flake8 ;;
    isort) task_isort ;;
    mypy) task_mypy ;;
    pyright) task_pyright ;;
    deprecations) task_deprecations ;;
    circular) task_circular ;;
    unit) task_unit ;;
    e2e) task_e2e ;;
    tests) task_tests ;;
    *) echo "Unknown task: $1"; usage; exit 2 ;;
  esac
}

log "👉 Starting verification (run_id=$RUN_ID)"
python3 - "$RUN_JSON" <<'PY'
import json,os,sys,time
p=sys.argv[1]
run={"run_id": os.environ.get("RUN_ID",""),
     "started_at": int(os.environ.get("START_EPOCH","0")),
     "status": "running",
     "steps": []}
with open(p,"w") as f: json.dump(run,f,sort_keys=True)
print()
PY

if [ "${#TASKS[@]}" -gt 0 ]; then
  for t in "${TASKS[@]}"; do run_selected_task "$t"; done
else
  task_quality
  task_tests
fi

log "✅ Verification process completed successfully"
