# Imagem Completa em Container Único Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma imagem Docker Python 3.10 que execute API Flask e retreinamento automático no mesmo container, conectando-se ao MySQL externo e persistindo os artefatos gerados.

**Architecture:** O container usará Supervisor como processo principal, com Gunicorn para `API.app:app` e um worker baseado em `API.MainServer`. O worker manterá o sinal de atualização até o treinamento completo terminar; o pipeline de treinamento será executado em um subprocesso isolado via `sys.executable`, evitando que imports e falhas do treinamento derrubem a API. Os diretórios `download/` e `Server/MLModels/saved_models/` serão graváveis e montáveis como volumes.

**Tech Stack:** Python 3.10, Flask, Gunicorn, Supervisor, TensorFlow, scikit-learn, skl2onnx, ONNX Runtime, MySQL Connector/Python, pathlib, unittest, Docker.

**Spec:** `docs/superpowers/specs/2026-09-23-full-single-container-design.md`

## Global Constraints

- O MySQL permanece externo ao container.
- O banco é configurado por `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`.
- A imagem inclui as dependências completas de treinamento e os datasets.
- API e worker executam com usuário não-root.
- A API escuta em `0.0.0.0:3000`.
- Os arquivos gerados devem usar caminhos `pathlib.Path`, sem dependência de barras Windows.
- Não alterar nem resolver os conflitos Git preexistentes em modelos, XMLs e bytecodes.
- Não executar o treinamento completo durante o build da imagem.

## Review Focus

- Importar a API sem iniciar treinamento ou conexão prematura com o banco: coberto no Task 1.
- Executar o worker a partir da raiz do projeto e do diretório `Server`: coberto no Task 2.
- Repetir uma solicitação quando o treinamento falhar sem apagar o sinal: coberto no Task 3.
- Gravar XML/JSON/modelos em Linux e em diretório persistente: coberto no Task 4.
- Iniciar os dois processos no container e detectar API indisponível: coberto no Task 5.

---

### Task 1: Criar uma entrada única para o treinamento

**Files:**
- Create: `tests/test_training_entrypoint.py`
- Modify: `Server/MainFunctions.py:1-189`
- Modify: `API/ServerProcessApi.py:69-163`

**Interfaces:**
- Produces `Server/MainFunctions.py::run_retraining() -> dict[str, object]`.
- `run_retraining()` returns `status`, `models`, `graph_xml`, `graph_json`, `optimized_graph_xml`, and `optimized_graph_json`.
- `API.ServerProcessApi.updateGraph() -> dict[str, object]` invokes `run_retraining()` through the current interpreter and raises `subprocess.CalledProcessError` when it fails.

- [ ] **Step 1: Write the failing tests**

Add tests that invoke a controlled training entrypoint through `subprocess.run` and assert that the worker uses `sys.executable`, `Server/MainFunctions.py`, the repository root as the project boundary, and a nonzero subprocess exit is propagated as an exception.

```python
def test_update_graph_uses_current_python_and_training_script(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda command, **kwargs: calls.append((command, kwargs)) or CompletedProcess(command, 0))
    updateGraph()
    assert calls[0][0][0] == sys.executable
    assert calls[0][0][-1].endswith("Server\\MainFunctions.py")
    assert calls[0][1]["check"] is True
```

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_training_entrypoint -v`

Expected: FAIL because `updateGraph()` currently imports the nonexistent `ModelANNTensorflow` module instead of invoking the current training script.

- [ ] **Step 3: Extract the existing top-level workflow**

Move the executable body of `Server/MainFunctions.py` into `run_retraining()`. Keep imports and constants inside the function where they depend on the existing `Server` execution context. Preserve the current sequence: database initialization, dataset loading, preprocessing, ANN/Decision Tree/Random Forest/SVM training, graph insertion, complete XML/JSON generation, optimized XML/JSON generation.

- [ ] **Step 4: Add the script entrypoint**

Add:

```python
if __name__ == "__main__":
    run_retraining()
```

Return artifact paths only after every model and graph file has been generated.

- [ ] **Step 5: Replace the stale worker implementation**

Replace the duplicate `updateGraph()` training body in `API/ServerProcessApi.py` with:

```python
def updateGraph():
    command = [sys.executable, str(PROJECT_ROOT / "Server" / "MainFunctions.py")]
    return subprocess.run(command, cwd=str(PROJECT_ROOT / "Server"), check=True)
```

Import `sys`, `subprocess`, and derive `PROJECT_ROOT` from `__file__`. Remove imports of `ModelANNTensorflow` and `ModelDecisionTreeRandomForestSKLearn`.

- [ ] **Step 6: Run the focused tests**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_training_entrypoint -v`

Expected: PASS, with no TensorFlow training performed by the test.

---

### Task 2: Make the training workflow portable

**Files:**
- Create: `tests/test_runtime_paths.py`
- Modify: `Server/Utilitarios/Constants.py:8-28`
- Modify: `Server/Database/DatabaseConnection.py:6-14`
- Modify: `Server/Database/DBConnection.py:10-18`
- Modify: `Server/MainFunctions.py:23-24,62-63`

**Interfaces:**
- `Constants.projectPath`, `Constants.pathProjectDownloads`, `Constants.pathProjectSaveModels`, and `Constants.pathProjectDataset` are `str` values derived from `Path` objects under the repository root.
- `DatabaseConnection.db_name` defaults to `KnowlegeGraphDB` and honors `DB_NAME`.

- [ ] **Step 1: Write the failing path tests**

Assert that paths use the checked-out repository root, contain no hardcoded repository name, and point to existing `download`, `Server/MLModels/saved_models`, and `Server/Datasets/Source` directories.

```python
def test_constants_resolve_from_repository_root():
    assert Path(Constants.pathProjectDownloads) == REPO_ROOT / "download"
    assert "ClassificationGraphSolutionforIoHT" not in str(REPO_ROOT.parent)
```

- [ ] **Step 2: Run the tests and verify failure**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_runtime_paths -v`

Expected: FAIL because `Constants.py` appends a Windows separator and a fixed repository name.

- [ ] **Step 3: Use pathlib for all configured paths**

Set `REPO_ROOT = Path(__file__).resolve().parents[2]`, derive the three project directories with `/`, and convert to strings only at the legacy API boundary. Keep `load_dotenv()` for local execution but never require a `.env` file in the image.

- [ ] **Step 4: Honor database environment variables**

Add `db_name = os.environ.get("DB_NAME") or "KnowlegeGraphDB"` and `db_port = int(os.environ.get("DB_PORT", "3306"))`. Pass the port and configured database name to `mysql.connector.connect`.

- [ ] **Step 5: Normalize MainFunctions dataset paths**

Build dataset paths from `Path(Constants.pathProjectDataset) / "Dataset1"` and `Path(Constants.pathProjectDataset) / "D2_ADL_Dataset" / "HMP_Dataset" / "All_data"`, then pass strings to legacy dataset classes.

- [ ] **Step 6: Run path and import tests**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_runtime_paths tests.test_api_smoke -v`

Expected: PASS without opening a server or running training.

---

### Task 3: Make the update protocol retryable

**Files:**
- Create: `tests/test_update_protocol.py`
- Modify: `API/app.py:22-50`
- Modify: `API/ServerProcessApi.py:16-67`
- Modify: `API/MainServer.py:1-12`

**Interfaces:**
- `GET /UpdateGraphRequest/0` returns `idle`, `graph_update`, `graph_running`, or `graph_failed`.
- `GET /UpdateGraphRequest/1` clears a completed request.
- `GET /UpdateGraphRequest/2` creates a pending request.
- `ServerProcessApi.execute(0)` only clears the request after `updateGraph()` succeeds.

- [ ] **Step 1: Write failing protocol tests**

Test that a pending request remains pending when `updateGraph()` raises and is cleared after it returns successfully. Test that the polling loop uses a configurable interval and request timeout.

- [ ] **Step 2: Run the tests and verify failure**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_update_protocol -v`

Expected: FAIL because `execute()` clears the API state before training starts and `requests.get()` has no timeout.

- [ ] **Step 3: Add explicit status transitions**

Add status helpers in `API/app.py` and transition `graph_update → graph_running → idle` on success or `graph_failed` on failure. Keep the last error in process memory for diagnostics.

- [ ] **Step 4: Add worker resilience**

Use `requests.get(..., timeout=10)`, catch `requests.RequestException`, log the failure, and retry on the next polling cycle. Use `API_BASE_URL`, `WORKER_POLL_SECONDS`, and `WORKER_REQUEST_TIMEOUT` environment variables.

- [ ] **Step 5: Fix timing**

Replace the hardcoded five-second sleep and incorrect `1440` counter with `time.sleep(float(os.getenv("WORKER_POLL_SECONDS", "5")))`. Keep forced daily retraining as a timestamp-based check only if it is still required by the application.

- [ ] **Step 6: Run protocol tests**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_update_protocol -v`

Expected: PASS, including the failure-and-retry case.

---

### Task 4: Correct model export and artifact publication

**Files:**
- Create: `tests/test_model_export_contract.py`
- Modify: `Server/MLModels/MLModels/SkLearn/DecisionTreeSkLearn.py:48-69,108-130`
- Modify: `Server/MLModels/MLModels/SkLearn/RandomForestSKLearn.py:56-122,158-212`
- Modify: `Server/XMLCreate.py:8-91`
- Modify: `Server/JSONConverter.py:5-35`

**Interfaces:**
- ACC model converters declare `FloatTensorType([None, 9])`.
- ACC+GYR model converters declare `FloatTensorType([None, 18])`.
- XML and JSON writers accept a filename and return a `Path` under the configured download directory.

- [ ] **Step 1: Write failing export contract tests**

Test that model export commands use `sys.executable`, verify `returncode == 0`, and that XML/JSON output paths remain inside the configured download directory.

- [ ] **Step 2: Run tests and verify failure**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_model_export_contract -v`

Expected: FAIL because converters declare one input feature, use the string `python`, and writers concatenate Windows backslashes.

- [ ] **Step 3: Correct feature dimensions and subprocess execution**

Use the actual feature counts and `subprocess.run([sys.executable, "-m", ...], check=True, capture_output=True, text=True)`. Remove shell-dependent `copy`, `mv`, and `del` operations in favor of `shutil.copy2` and `Path.unlink`.

- [ ] **Step 4: Normalize XML/JSON output paths**

Use `Path(Constants.pathProjectDownloads) / f"{fileName}.xml"` and the equivalent JSON path. Create the parent directory before writing. Return the resulting `Path` as a string only where legacy callers require it.

- [ ] **Step 5: Run export and API route tests**

Run: `venv\Scripts\python.exe -B -m unittest tests.test_model_export_contract tests.test_api_smoke -v`

Expected: PASS without retraining.

---

### Task 5: Build the complete single-container image

**Files:**
- Create: `.dockerignore`
- Create: `docker/supervisord.conf`
- Modify: `Dockerfile:1-27`
- Modify: `Requirements.txt`

**Interfaces:**
- `docker build -t classification-graph:full .` produces the image.
- The image exposes TCP port `3000`.
- Supervisor starts `api` and `trainer` programs as the non-root `graph` user.

- [ ] **Step 1: Add Docker-specific dependency**

Add `gunicorn` and `supervisor` to `Requirements.txt` with versions available for Python 3.10.

- [ ] **Step 2: Add `.dockerignore`**

Exclude `.git`, `.idea`, `.env`, `venv`, `__pycache__`, `*.pyc`, `tests`, and temporary files. Keep `Server/Datasets/Source`, `Server/MLModels/saved_models`, and `download` because the complete image must support training and artifact serving.

- [ ] **Step 3: Add Supervisor configuration**

Create programs with these commands:

```ini
[program:api]
command=gunicorn --bind 0.0.0.0:3000 --workers 1 --threads 4 --timeout 120 API.app:app
autorestart=true

[program:trainer]
command=python -B API/MainServer.py
autorestart=true
```

Send logs to stdout/stderr and stop both programs with the container.

- [ ] **Step 4: Replace Dockerfile**

Use `python:3.10-slim`, install `libgomp1`, copy `Requirements.txt` before `pip install -r`, copy `API`, `Server`, and `download`, create the `graph` user, create writable artifact directories, set `USER graph`, expose port 3000, add a Python-based healthcheck for `/`, and run `supervisord -n -c /app/docker/supervisord.conf`.

- [ ] **Step 5: Run Dockerfile static checks**

Run: `docker build --no-cache -t classification-graph:full .`

Expected: exit code 0 and an image tagged `classification-graph:full`.

---

### Task 6: Validate the running image against external MySQL

**Files:**
- Modify: `README.md:24-82`
- Create: `docker/run-full.ps1`

- [ ] **Step 1: Document container variables and volumes**

Document `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `API_BASE_URL`, `WORKER_POLL_SECONDS`, and the two artifact volumes. Explicitly state that `localhost` inside the container is not the host MySQL address.

- [ ] **Step 2: Add a local run helper**

Create a PowerShell helper that runs:

```powershell
docker run --rm --name classification-graph `
  -p 3000:3000 `
  -e DB_HOST=$env:DB_HOST `
  -e DB_PORT=$env:DB_PORT `
  -e DB_USER=$env:DB_USER `
  -e DB_PASSWORD=$env:DB_PASSWORD `
  -e DB_NAME=$env:DB_NAME `
  -v classification-download:/app/download `
  -v classification-models:/app/Server/MLModels/saved_models `
  classification-graph:full
```

- [ ] **Step 3: Start the image and verify the health endpoint**

Run: `Invoke-WebRequest http://localhost:3000/`

Expected: HTTP 200 with body `execute`.

- [ ] **Step 4: Verify artifact routes**

Request `/GraphRequest`, `/OptimizeGraphRequest/acc_gyr`, `/OptimizeGraphRequest/acc/50`, and one `/saved_model/...` path. Assert HTTP 200, valid XML for graph routes, and the expected content disposition.

- [ ] **Step 5: Trigger and observe retraining**

Request `/UpdateGraphRequest/2`, follow worker logs, and assert that the worker reaches `graph_running` and then `idle`, with refreshed XML/JSON/model timestamps. Do not run this step against a production database without a backup.

---

### Task 7: Full verification and handoff

**Files:**
- Test: `tests/`
- Review: all files changed by Tasks 1-6

- [ ] **Step 1: Run the Python test suite**

Run: `venv\Scripts\python.exe -B -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 2: Validate dependency consistency**

Run: `venv\Scripts\python.exe -m pip check`

Expected: `No broken requirements found.`

- [ ] **Step 3: Build and start the image again from a clean Docker cache**

Run: `docker build --no-cache -t classification-graph:full .`

Expected: exit code 0.

- [ ] **Step 4: Review scope and conflicts**

Run: `git status --short` and confirm that only intended Docker/application files are part of the work. Do not stage or resolve existing `UU`, `DU`, or `AD` entries.

- [ ] **Step 5: Report residual risk**

Report the actual Docker image size, training duration, MySQL host used, route results, and any training/model conversion failures observed. Do not claim full retraining works until Task 6 Step 5 completes successfully.
