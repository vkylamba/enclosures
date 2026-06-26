#!/usr/bin/env python3
"""Temporary HTTP server to receive and apply git patch files.

Usage:
  python scripts/temp_patch_server.py --repo . --port 8787 --token my-secret

Send a patch file (recommended):
  curl -X POST "http://127.0.0.1:8787/apply" \
    -H "X-Auth-Token: my-secret" \
    --data-binary @changes.patch

Create a new text file:
    curl -X POST "http://127.0.0.1:8787/create-file" \
        -H "Content-Type: application/json" \
        -H "X-Auth-Token: my-secret" \
        --data '{"path":"notes/example.txt","content":"hello world"}'

Optional dry-run check only:
  curl -X POST "http://127.0.0.1:8787/apply?dry_run=1" \
    -H "X-Auth-Token: my-secret" \
    --data-binary @changes.patch
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("patch_server")


UI_HTML = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Temp Patch Server</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f5f7fb;
            --panel: #ffffff;
            --text: #1d2433;
            --muted: #5f6b85;
            --accent: #0b6bcb;
            --accent-2: #094f97;
            --border: #d8dfec;
            --ok: #0c7a43;
            --err: #a92e2e;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at 20% 0%, #e9f3ff, var(--bg) 45%);
            color: var(--text);
            padding: 24px;
        }
        .wrap {
            max-width: 980px;
            margin: 0 auto;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            box-shadow: 0 14px 36px rgba(21, 40, 75, 0.1);
            overflow: hidden;
        }
        header {
            padding: 18px 22px;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(90deg, #f8fbff, #ffffff);
        }
        h1 {
            margin: 0;
            font-size: 20px;
            letter-spacing: 0.2px;
        }
        .sub {
            margin-top: 4px;
            font-size: 13px;
            color: var(--muted);
        }
        .content {
            padding: 20px;
            display: grid;
            gap: 14px;
        }
        .panel {
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            background: #fbfcff;
            display: grid;
            gap: 12px;
        }
        .panel h2 {
            margin: 0;
            font-size: 15px;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 220px 120px;
            gap: 10px;
            align-items: center;
        }
        label {
            display: block;
            font-size: 13px;
            color: var(--muted);
            margin-bottom: 6px;
        }
        input[type="password"],
        textarea {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            font: 14px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            color: var(--text);
            background: #fff;
        }
        textarea {
            min-height: 360px;
            resize: vertical;
            white-space: pre;
        }
        input[type="text"] {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            font: 14px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            color: var(--text);
            background: #fff;
        }
        .check {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 22px;
            color: var(--muted);
            font-size: 13px;
        }
        button {
            border: 0;
            border-radius: 10px;
            background: var(--accent);
            color: white;
            padding: 10px 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background .15s ease;
        }
        button:hover { background: var(--accent-2); }
        button:disabled {
            opacity: .6;
            cursor: not-allowed;
        }
        pre {
            margin: 0;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            background: #fbfcff;
            min-height: 120px;
            overflow: auto;
            font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        }
        .status { font-weight: 600; font-size: 14px; }
        .ok { color: var(--ok); }
        .err { color: var(--err); }
        @media (max-width: 880px) {
            .row { grid-template-columns: 1fr; }
            .check { margin-top: 0; }
        }
    </style>
</head>
<body>
    <main class="wrap">
        <header>
            <h1>Temporary Patch Apply UI</h1>
            <div class="sub">Paste a unified diff and apply it with git apply.</div>
        </header>
        <section class="content">
            <div class="row">
                <div>
                    <label for="token">X-Auth-Token</label>
                    <input id="token" type="password" placeholder="Leave empty if server has no token" />
                </div>
                <div style="display:flex;flex-direction:column;gap:6px">
                    <label class="check" for="dryRun" style="margin-bottom:0">
                        <input id="dryRun" type="checkbox" /> Dry run only
                    </label>
                    <label class="check" for="opt3way" style="margin-bottom:0">
                        <input id="opt3way" type="checkbox" /> --3way (three-way merge)
                    </label>
                    <label class="check" for="optReject" style="margin-bottom:0">
                        <input id="optReject" type="checkbox" /> --reject (save .rej files for failed hunks)
                    </label>
                    <label class="check" for="optWhitespace" style="margin-bottom:0">
                        <input id="optWhitespace" type="checkbox" /> --ignore-whitespace
                    </label>
                </div>
                <button id="applyBtn" type="button">Apply Diff</button>
            </div>

            <div class="panel">
                <h2>Create Text File</h2>
                <div>
                    <label for="filePath">File path</label>
                    <input id="filePath" type="text" placeholder="docs/new-note.txt" />
                </div>
                <div>
                    <label for="fileContent">File text</label>
                    <textarea id="fileContent" spellcheck="false" placeholder="Paste the text content here..."></textarea>
                </div>
                <label class="check" for="overwrite" style="margin-top:0">
                    <input id="overwrite" type="checkbox" /> Overwrite if the file already exists
                </label>
                <div>
                    <button id="createBtn" type="button">Create File</button>
                </div>
            </div>

            <div class="panel">
                <h2>Apply Patch</h2>
                <div>
                    <label for="patch">Patch Diff</label>
                    <textarea id="patch" spellcheck="false" placeholder="Paste your diff here..."></textarea>
                </div>
                <div>
                    <button id="applyPatchBtn" type="button">Apply Diff</button>
                </div>
            </div>

            <div id="status" class="status"></div>
            <pre id="output">No request yet.</pre>
        </section>
    </main>

    <script>
        const applyBtn = document.getElementById('applyBtn');
        const applyPatchBtn = document.getElementById('applyPatchBtn');
        const createBtn = document.getElementById('createBtn');
        const tokenEl = document.getElementById('token');
        const dryRunEl = document.getElementById('dryRun');
        const opt3wayEl = document.getElementById('opt3way');
        const optRejectEl = document.getElementById('optReject');
        const optWhitespaceEl = document.getElementById('optWhitespace');
        const filePathEl = document.getElementById('filePath');
        const fileContentEl = document.getElementById('fileContent');
        const overwriteEl = document.getElementById('overwrite');
        const patchEl = document.getElementById('patch');
        const statusEl = document.getElementById('status');
        const outputEl = document.getElementById('output');

        function setStatus(text, ok) {
            statusEl.textContent = text;
            statusEl.className = `status ${ok ? 'ok' : 'err'}`;
        }

        async function sendRequest(url, body, contentType) {
            applyBtn.disabled = true;
            applyPatchBtn.disabled = true;
            createBtn.disabled = true;
            setStatus('Sending request...', true);
            outputEl.textContent = '';

            try {
                const headers = { 'Content-Type': contentType };
                const token = tokenEl.value.trim();
                if (token) {
                    headers['X-Auth-Token'] = token;
                }

                const res = await fetch(url, { method: 'POST', headers, body });
                const text = await res.text();
                let data;
                try {
                    data = JSON.parse(text);
                } catch {
                    data = { raw: text };
                }

                const ok = res.ok && data.ok;
                setStatus(ok ? 'Success' : 'Request failed', ok);
                outputEl.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                setStatus('Network error', false);
                outputEl.textContent = String(err);
            } finally {
                applyBtn.disabled = false;
                applyPatchBtn.disabled = false;
                createBtn.disabled = false;
            }
        }

        applyPatchBtn.addEventListener('click', async () => {
            const patch = patchEl.value;
            if (!patch.trim()) {
                setStatus('Please paste a diff first.', false);
                return;
            }

            const params = new URLSearchParams();
            if (dryRunEl.checked) params.set('dry_run', '1');
            if (opt3wayEl.checked) params.set('three_way', '1');
            if (optRejectEl.checked) params.set('reject', '1');
            if (optWhitespaceEl.checked) params.set('ignore_whitespace', '1');
            const url = '/apply' + (params.toString() ? '?' + params.toString() : '');

            await sendRequest(url, patch, 'text/plain; charset=utf-8');
        });

        createBtn.addEventListener('click', async () => {
            const filePath = filePathEl.value.trim();
            const fileContent = fileContentEl.value;
            if (!filePath) {
                setStatus('Please enter a file path first.', false);
                return;
            }

            await sendRequest(
                '/create-file',
                JSON.stringify({
                    path: filePath,
                    content: fileContent,
                    overwrite: overwriteEl.checked,
                }),
                'application/json; charset=utf-8',
            );
        });
    </script>
</body>
</html>
"""


class PatchHandler(BaseHTTPRequestHandler):
    server_version = "TempPatchServer/1.0"

    def _json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _is_authorized(self) -> bool:
        expected = self.server.auth_token  # type: ignore[attr-defined]
        if not expected:
            return True
        provided = self.headers.get("X-Auth-Token", "")
        return provided == expected

    def _repo_dir(self) -> Path:
        return self.server.repo_dir  # type: ignore[attr-defined]

    def _read_body(self) -> bytes:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("invalid Content-Length")

        max_bytes = self.server.max_bytes  # type: ignore[attr-defined]
        if content_length <= 0:
            raise ValueError("empty request body")
        if content_length > max_bytes:
            raise OverflowError(f"request too large (>{max_bytes} bytes)")
        return self.rfile.read(content_length)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = UI_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/health":
            self._json(HTTPStatus.OK, {"ok": True, "repo": str(self._repo_dir())})
            return
        self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/apply", "/create-file"}:
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
            return

        if not self._is_authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        try:
            body_bytes = self._read_body()
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        except OverflowError as exc:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": str(exc)})
            return

        if parsed.path == "/create-file":
            self._handle_create_file(body_bytes)
            return

        patch_bytes = body_bytes

        qs = parse_qs(parsed.query)
        def _flag(name: str) -> bool:
            return qs.get(name, ["0"])[0] in {"1", "true", "True"}

        dry_run          = _flag("dry_run")
        use_three_way    = _flag("three_way")
        use_reject       = _flag("reject")
        ignore_whitespace = _flag("ignore_whitespace")

        extra_flags: list[str] = []
        if use_three_way:      extra_flags.append("-3")
        if use_reject:         extra_flags.append("--reject")
        if ignore_whitespace:  extra_flags.append("--ignore-whitespace")

        # --reject/--3way are incompatible with --check; skip the pre-flight in that mode
        skip_check = use_reject or use_three_way

        with tempfile.NamedTemporaryFile(prefix="incoming-", suffix=".patch", delete=False) as tf:
            tf.write(patch_bytes)
            patch_path = Path(tf.name)

        try:
            fallback_reason = ""
            if not skip_check:
                check = run_git_apply(self._repo_dir(), patch_path, check_only=True, extra_flags=[])
                if check.returncode != 0:
                    saved = save_failed_patch(self._repo_dir(), patch_bytes)
                    logger.error(
                        "Patch check failed (saved: %s)\nstdout: %s\nstderr: %s",
                        saved, check.stdout.strip(), check.stderr.strip(),
                    )
                    self._json(
                        HTTPStatus.BAD_REQUEST,
                        {
                            "ok": False,
                            "error": "patch check failed",
                            "saved_patch": str(saved),
                            "stdout": check.stdout,
                            "stderr": check.stderr,
                        },
                    )
                    return

            if dry_run:
                self._json(HTTPStatus.OK, {"ok": True, "message": "patch is valid (dry_run=1)"})
                return

            applied = run_git_apply(self._repo_dir(), patch_path, check_only=False, extra_flags=extra_flags)

            # Fallback path for --3way when repository lacks index/blob data.
            if applied.returncode != 0 and "-3" in extra_flags and has_threeway_blob_errors(applied.stderr):
                retry_flags = [f for f in extra_flags if f != "-3"]
                if "--reject" not in retry_flags:
                    retry_flags.append("--reject")
                fallback_reason = "-3 failed due to missing index/blob; retried without -3 and with --reject"
                logger.warning("%s", fallback_reason)
                applied = run_git_apply(self._repo_dir(), patch_path, check_only=False, extra_flags=retry_flags)
                extra_flags = retry_flags

            # Auto-retry: if files already exist, remove them and try again
            if applied.returncode != 0:
                existing = parse_already_exists(applied.stderr)
                if existing:
                    logger.warning(
                        "Removing %d pre-existing file(s) before retry: %s",
                        len(existing), existing,
                    )
                    for rel in existing:
                        target = self._repo_dir() / rel
                        try:
                            target.unlink()
                        except OSError as exc:
                            logger.error("Could not remove %s: %s", target, exc)
                    applied = run_git_apply(self._repo_dir(), patch_path, check_only=False, extra_flags=extra_flags)

            if applied.returncode != 0:
                saved = save_failed_patch(self._repo_dir(), patch_bytes)
                logger.error(
                    "Patch apply failed (flags: %s, saved: %s)\nstdout: %s\nstderr: %s",
                    extra_flags, saved, applied.stdout.strip(), applied.stderr.strip(),
                )
                self._json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {
                        "ok": False,
                        "error": "failed to apply patch (partial apply may have occurred; check .rej files if --reject was used)",
                        "saved_patch": str(saved),
                        "stdout": applied.stdout,
                        "stderr": applied.stderr,
                    },
                )
                return

            logger.info("Patch applied successfully (flags: %s, repo: %s)", extra_flags, self._repo_dir())
            self._json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "message": "patch applied",
                    "repo": str(self._repo_dir()),
                    "flags": extra_flags,
                    "fallback_reason": fallback_reason,
                },
            )
        finally:
            try:
                patch_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _handle_create_file(self, body_bytes: bytes) -> None:
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "request body must be valid JSON"})
            return

        if not isinstance(payload, dict):
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "JSON body must be an object"})
            return

        rel_path = payload.get("path")
        content = payload.get("content", "")
        overwrite = bool(payload.get("overwrite", False))

        if not isinstance(rel_path, str) or not rel_path.strip():
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "path must be a non-empty string"})
            return
        if not isinstance(content, str):
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "content must be a string"})
            return

        repo_dir = self._repo_dir().resolve()
        target = (repo_dir / rel_path).resolve()
        if repo_dir != target and repo_dir not in target.parents:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "path escapes repository root"})
            return

        if target.exists() and not overwrite:
            self._json(HTTPStatus.CONFLICT, {"ok": False, "error": "file already exists"})
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger.info("Created text file %s", target)
        self._json(
            HTTPStatus.OK,
            {
                "ok": True,
                "message": "file created",
                "repo": str(repo_dir),
                "path": str(target.relative_to(repo_dir)),
                "overwrite": overwrite,
            },
        )

    def log_message(self, format: str, *args) -> None:
        logger.info("%s %s", self.address_string(), format % args)


def save_failed_patch(repo_dir: Path, patch_bytes: bytes) -> Path:
    """Persist a failed patch to <repo>/failed_patches/ for later retry."""
    import datetime
    failed_dir = repo_dir / "failed_patches"
    failed_dir.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dest = failed_dir / f"failed_{ts}.patch"
    dest.write_bytes(patch_bytes)
    logger.warning("Failed patch saved to %s", dest)
    return dest


def parse_already_exists(stderr: str) -> list[str]:
    """Extract filenames from 'error: <file>: already exists in working directory'."""
    import re
    return re.findall(r"^error: (.+): already exists in working directory", stderr, re.MULTILINE)


def has_threeway_blob_errors(stderr: str) -> bool:
    """Detect known 3-way merge failures that should trigger a non-3way retry."""
    needles = [
        "does not exist in index",
        "cannot read the current contents",
        "repository lacks the necessary blob to perform 3-way merge",
    ]
    lower = stderr.lower()
    return any(n.lower() in lower for n in needles)


def run_git_apply(
    repo_dir: Path,
    patch_path: Path,
    check_only: bool,
    extra_flags: list[str] | None = None,
) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", str(repo_dir), "apply"]
    if check_only:
        cmd.append("--check")
    if extra_flags:
        cmd.extend(extra_flags)
    cmd.append(str(patch_path))
    return subprocess.run(cmd, capture_output=True, text=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Temporary git patch receiver server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8787, help="Bind port (default: 8787)")
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository directory where patches are applied (default: current directory)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("PATCH_SERVER_TOKEN", ""),
        help="Auth token expected in X-Auth-Token header (optional)",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=2 * 1024 * 1024,
        help="Maximum patch size in bytes (default: 2097152)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_dir = Path(args.repo).resolve()

    if not (repo_dir / ".git").exists():
        print(f"Error: {repo_dir} is not a git repository (.git not found)")
        return 2

    server = ThreadingHTTPServer((args.host, args.port), PatchHandler)
    server.repo_dir = repo_dir  # type: ignore[attr-defined]
    server.auth_token = args.token  # type: ignore[attr-defined]
    server.max_bytes = args.max_bytes  # type: ignore[attr-defined]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info(
        "Temp patch server listening on http://%s:%s for repo %s",
        args.host, args.port, repo_dir,
    )
    if args.token:
        logger.info("Auth: enabled via X-Auth-Token")
    else:
        logger.warning("Auth: disabled (no token configured)")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
