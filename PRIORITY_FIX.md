# PRIORITY_FIX.md

Known bugs, vulnerabilities, and improvements needed for the Kenya Wealth & Finance Agent. Each item includes the problem, where it is, and a fix direction.

---

## Summary

| # | Severity | Area | Description |
|---|----------|------|-------------|
| 1 | CRITICAL | Security | XSS via innerHTML when DOMPurify CDN fails |
| 2 | CRITICAL | Security | No CSP or security headers on API responses |
| 3 | CRITICAL | Security | Session state shared across all users |
| 4 | CRITICAL | Data integrity | Conversation history corrupted on API failure |
| 5 | CRITICAL | Data integrity | Timestamp key leaked into Ollama API messages |
| 6 | CRITICAL | Security | CORS allows all origins with credentials |
| 7 | HIGH | Bug | /api/history always returns empty list |
| 8 | HIGH | Bug | Export endpoint returns filesystem path, not downloadable file |
| 9 | HIGH | Bug | No input validation on numeric API fields |
| 10 | HIGH | Bug | Unbounded conversation history (memory exhaustion) |
| 11 | HIGH | Bug | Streaming frontend code is dead code |
| 12 | MEDIUM | Logic | Tax bracket gaps for non-integer salaries |
| 13 | MEDIUM | Logic | savings_rate is decimal, expense_percentages is percentage |
| 14 | MEDIUM | Logic | Unknown risk_tolerance silently defaults to aggressive |
| 15 | MEDIUM | Logic | Short timeline overrides risk profile completely |
| 16 | MEDIUM | Logic | SHIF floor gives negative net salary at zero income |
| 17 | MEDIUM | UI/UX | Flash of light mode before JS applies dark theme |
| 18 | MEDIUM | UI/UX | Invalid ARIA roles on welcome cards |
| 19 | MEDIUM | UI/UX | No focus indicators on most interactive elements |
| 20 | MEDIUM | UI/UX | iOS zoom triggered by 14.5px input font size |
| 21 | MEDIUM | UI/UX | Toast XSS via error message interpolation |
| 22 | MEDIUM | UI/UX | CDN scripts without Subresource Integrity hashes |
| 23 | MEDIUM | UI/UX | CLI has no retry/timeout/loading feedback |
| 24 | LOW | Quality | Duplicate dependencies in requirements.txt |
| 25 | LOW | Quality | Unused dependencies (python-dotenv, sse-starlette) |
| 26 | LOW | Quality | Dead code: models/user.py enums never wired into services |
| 27 | LOW | Quality | Class constants shadow module imports in agent.py |
| 28 | LOW | Quality | sys.path manipulation in web/app.py |
| 29 | LOW | Quality | start_web.sh kills port 8000 with SIGKILL |
| 30 | LOW | Quality | Budget expense key matching is case/whitespace-sensitive |
| 31 | LOW | Quality | get_config() silently ignores config_path after first call |
| 32 | LOW | Quality | Broad except Exception in CLI swallows debuggable errors |

---

## CRITICAL — Security & Data Integrity

### 1. XSS via innerHTML when DOMPurify CDN fails

**File:** `web/index.html` (lines 1954-1971)

**Problem:** The `render()` function passes LLM output through `marked.parse()` then into `innerHTML`. DOMPurify sanitization only runs if the CDN script loaded successfully (`if (window.DOMPurify)`). If the CDN is unreachable, blocked, or compromised, raw LLM output (which may contain `<script>` tags or event handlers) is injected into the DOM without sanitization. An LLM that outputs malicious HTML will execute arbitrary JavaScript in the user's browser.

Additionally, the `toast()` function (line 2144) interpolates `msg` directly into `innerHTML` without escaping. Server error messages containing HTML will execute as scripts.

**Fix:**
- Add a server-side HTML-escaping fallback in the `render()` function that runs before `marked.parse()`, similar to what `templates/html.py:_HTML_TAG_RE` already does for the HTML report.
- Escape `msg` in `toast()` before inserting into `innerHTML`, or use `textContent` for the message span.
- Add Subresource Integrity (SRI) hashes to CDN `<script>` tags as a supply-chain mitigation (see item #22).
- Consider inlining a minified DOMPurify build so the app never runs without it.

---

### 2. No CSP or security headers on API responses

**File:** `web/app.py`

**Problem:** The FastAPI app sets no `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, or any other security headers. Without CSP, XSS vulnerabilities (see item #1) cannot be mitigated at the browser level. No `X-Frame-Options` means the app is vulnerable to clickjacking. No `X-Content-Type-Options: nosniff` means MIME-type confusion attacks are possible.

**Fix:** Add a Starlette middleware that injects security headers on all responses:

```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline'"
    )
    return response
```

---

### 3. Session state shared across all users

**File:** `web/app.py` (lines 46-51)

**Problem:** `SessionState` is a global singleton. All users connecting to the web server share the same `session.messages` and `session.started_at`. This means:
- Any user's chat messages are visible to all others via `/api/history`.
- One user's `/api/reset` clears everyone's session.
- Race conditions under concurrent access (list mutations during iteration).

**Fix:**
- For single-user local deployment: add a comment documenting this limitation.
- For multi-user: replace the global `SessionState` with per-session storage keyed by a session cookie or UUID. Use a dict like `sessions: Dict[str, SessionState]` and create a new session on each new connection.
- Add a lock (`threading.Lock`) around session mutations if uvicorn uses multiple threads.

---

### 4. Conversation history corrupted on API failure

**File:** `agent.py` (lines 73-86)

**Problem:** In `chat()`, the user message is appended to `conversation_history` (line 73-76) *before* the `client.chat()` API call (line 79-85). If the API call raises an exception (network error, model not found, timeout), the user message remains in history with no assistant response. On the next call, this orphaned user message is sent to the LLM, producing confused responses.

**Fix:** Move the user message append *after* the successful API call, or wrap in try/except and remove on failure:

```python
def chat(self, user_message: str) -> str:
    user_msg = {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()}
    try:
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "system", "content": get_system_prompt()}] + self.conversation_history + [user_msg],
        )
    except Exception:
        raise  # Don't append user message on failure
    assistant_message = response["message"]["content"]
    self.conversation_history.append(user_msg)
    self.conversation_history.append({"role": "assistant", "content": assistant_message, "timestamp": datetime.now().isoformat()})
    return assistant_message
```

---

### 5. Timestamp key leaked into Ollama API messages

**File:** `agent.py` (lines 73-84)

**Problem:** Each conversation history entry includes a `timestamp` key (e.g., `{"role": "user", "content": "...", "timestamp": "2024-01-01T12:00:00"}`). When this history is spread into the `messages` parameter of `client.chat()` (line 83), every entry carries the extra `timestamp` key into the Ollama API call. The Ollama chat API expects only `role` and `content`. While the current Python client may silently ignore extra keys, this is undocumented and could break with any library update.

**Fix:** Strip non-standard keys before passing to the API:

```python
messages=[{"role": "system", "content": get_system_prompt()}] + [
    {"role": m["role"], "content": m["content"]} for m in self.conversation_history
]
```

---

### 6. CORS allows all origins with credentials

**File:** `web/app.py` (lines 34-40)

**Problem:** `allow_origins=["*"]` combined with `allow_credentials=True` is a dangerous configuration. Browsers block `Access-Control-Allow-Origin: *` when `credentials: include` is used, but the intent is clearly permissive. If the server is exposed beyond localhost (e.g., on a network), any website can make cross-origin requests to the API.

**Fix:** Restrict origins to localhost:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## HIGH — Functional Bugs

### 7. /api/history always returns empty

**File:** `web/app.py` (lines 46-51, 151-165)

**Problem:** `SessionState.messages` is never populated. The `/api/chat` endpoint calls `agent.chat()` which stores messages in the agent's internal `conversation_history`, but `session.messages` stays empty. The `/api/history` endpoint reads from `session.messages`, so it always returns `[]`.

**Fix:** Have `/api/history` read from the agent's actual conversation history:

```python
@app.get("/api/history", response_model=ConversationHistory)
async def get_history():
    agent = get_agent()
    messages = [
        Message(role=m["role"], content=m["content"], timestamp=m.get("timestamp", ""))
        for m in agent.get_conversation_history()
    ]
    return ConversationHistory(messages=messages, started_at=session.started_at.isoformat() if session.started_at else None)
```

Or alternatively, populate `session.messages` in `/api/chat`.

---

### 8. Export endpoint returns filesystem path, not downloadable file

**File:** `web/app.py` (lines 200-217)

**Problem:** `/api/export` calls `save_html_report()` which writes a file to disk and returns the filesystem path. The web UI shows this raw path in a toast, which is meaningless to a browser user who cannot access the server's filesystem. There is no mechanism to download the file.

**Fix:** Either:
- (a) Return the HTML content directly with `HTMLResponse` and a `Content-Disposition: attachment` header so the browser downloads it.
- (b) Serve the file via a `FileResponse` with `media_type="text/html"` and `filename="report.html"`.

```python
from fastapi.responses import FileResponse

@app.get("/api/export")
async def export_conversation():
    agent = get_agent()
    from templates.html import save_html_report
    report_path = save_html_report(agent.get_conversation_history(), session.started_at)
    return FileResponse(report_path, media_type="text/html", filename="kenya_wealth_advice.html")
```

---

### 9. No input validation on numeric API fields

**Files:** `web/app.py` (lines 85-92), `services/tax.py`, `services/budget.py`, `services/investment.py`, `services/emergency.py`

**Problem:** The Pydantic models accept any float, including negative values, zero, `NaN`, and `Infinity`. Downstream service functions produce nonsensical results: negative taxes, negative net salary, NaN savings rates, etc.

**Fix:** Add Pydantic field validators:

```python
from pydantic import Field, validator

class BudgetRequest(BaseModel):
    income: float = Field(..., gt=0)
    expenses: Dict[str, float] = Field(...)

    @validator("expenses")
    def validate_expenses(cls, v):
        for key, val in v.items():
            if val < 0:
                raise ValueError(f"Expense '{key}' must be non-negative")
        return v

class TaxRequest(BaseModel):
    gross_salary: float = Field(..., gt=0)
```

Also add guards in each service function for edge cases (negative, zero, NaN).

---

### 10. Unbounded conversation history

**File:** `agent.py` (lines 59, 73-93)

**Problem:** Every `chat()` call appends to `conversation_history` without limit. An attacker sending many large messages will exhaust memory and make LLM calls increasingly expensive (quadratic token growth). The web UI caps at 50 messages client-side (`MAX_M = 50`), but the server has no limit.

**Fix:** Add a maximum history size with a sliding window that keeps the system prompt and the most recent N message pairs:

```python
MAX_HISTORY_PAIRS = 50

def chat(self, user_message: str) -> str:
    # ... after appending messages ...
    if len(self.conversation_history) > MAX_HISTORY_PAIRS * 2:
        # Keep the most recent exchanges
        self.conversation_history = self.conversation_history[-(MAX_HISTORY_PAIRS * 2):]
```

---

### 11. Streaming frontend code is dead code

**File:** `web/index.html` (lines 1859-1878)

**Problem:** The frontend has a `stream()` function that attempts to read a response body as a ReadableStream. However, the backend `/api/chat` endpoint returns a complete JSON response synchronously — there is no SSE or streaming endpoint. The `stream()` code path is unreachable unless the server sends `text/plain` or `text/event-stream` content type, which never happens.

**Fix:** Either:
- (a) Remove the dead `stream()` code and the branching logic that tries to call it.
- (b) Implement an SSE streaming endpoint in `web/app.py` using `sse-starlette` (which is already in `requirements.txt`) and wire the frontend to use it.

---

## MEDIUM — Service Logic

### 12. Tax bracket gaps for non-integer salaries

**Files:** `services/tax.py` (lines 47-53), `config/constants.py`

**Problem:** Tax brackets use non-overlapping integer boundaries (`min: 24001, max: 24000`). For a float salary like `24000.50`, the bracket calculation skips from bracket 1 (0-24000) directly past bracket 2 (24001-32333), leaving the 0.50 KES untaxed. There are 4 such gaps at bracket boundaries.

**Fix:** Make bracket boundaries overlap by using inclusive lower bounds:
```python
TAX_BRACKETS = [
    {"min": 0,      "max": 24000,   "rate": 0.10},
    {"min": 24000,  "max": 32333,   "rate": 0.25},  # was 24001
    {"min": 32333,  "max": 500000,  "rate": 0.30},  # was 32334
    {"min": 500000, "max": 800000,  "rate": 0.325},
    {"min": 800000, "max": float("inf"), "rate": 0.35},
]
```

And adjust the calculation to use `max(0, min(salary, upper) - lower)`.

---

### 13. savings_rate is decimal vs percentage inconsistency

**File:** `services/budget.py` (line 32)

**Problem:** `savings_rate = surplus / income` returns a decimal (e.g., 0.25 for 25%), but `expense_percentages` on lines 36-38 multiplies by 100 to return percentages (e.g., 30 for 30%). The docstring says "Surplus as percentage of income" but the value is a decimal. This inconsistency makes direct comparison confusing.

**Fix:** Either multiply `savings_rate` by 100 to match `expense_percentages`, or update the docstring to say "Surplus as a proportion of income (0-1)" and document the inconsistency. Consistent approach:
```python
savings_rate = round((surplus / income) * 100, 2) if income > 0 else 0
```

---

### 14. Unknown risk_tolerance silently defaults to aggressive

**File:** `services/investment.py` (line 58)

**Problem:** The `else` clause catches any `risk_tolerance` that is not "conservative" or "moderate" and treats it as "aggressive". Typos like `"modrat"` or `"consrvative"` silently produce aggressive investment recommendations.

**Fix:** Validate the input and return a warning for unrecognized values:
```python
valid_risks = {"conservative", "moderate", "aggressive"}
if risk_level not in valid_risks:
    recommendations["warnings"].append(
        f"Unrecognized risk tolerance '{risk_tolerance}'. Defaulting to 'moderate'."
    )
    risk_level = "moderate"
```

---

### 15. Short timeline overrides risk profile completely

**File:** `services/investment.py` (lines 66-75)

**Problem:** When `timeline in ["short", "1-2 years"]`, the entire `suggested_allocations` list is replaced with a conservative 60/40 split regardless of the user's risk profile. An aggressive investor with a short timeline gets the same recommendation as a conservative one.

**Fix:** Blend the risk-profile allocation with a short-timeline safety tilt instead of replacing it entirely. For example, for an aggressive investor with a short timeline, shift 30% from high-risk to low-risk assets rather than replacing everything with MMF/SACCO.

---

### 16. SHIF floor gives negative net salary at zero income

**File:** `services/tax.py` (lines 59-60)

**Problem:** When `gross_salary = 0`: SHIF applies its minimum of KES 300, giving `total_deductions = 300` and `net_salary = -300`. This is technically correct per SHIF rules (minimum contribution), but produces a nonsensical negative result for a zero-income query.

**Fix:** Add a guard at the start of `calculate_tax()`:
```python
if gross_salary <= 0:
    return {
        "gross_salary": 0, "paye": 0, "nhif_shif": 0,
        "nssf": 0, "housing_levy": 0, "total_deductions": 0, "net_salary": 0,
        "warning": "Gross salary must be positive for tax calculation."
    }
```

---

## MEDIUM — UI/UX

### 17. Flash of light mode before JS applies dark theme

**File:** `web/index.html`

**Problem:** Dark mode is applied via `[data-theme="dark"]` toggled by JavaScript on `DOMContentLoaded`. Users who prefer dark mode at the OS level see a flash of light content before the JS runs (FOUC).

**Fix:** Inline a theme-detection script in the `<head>` before any CSS:
```html
<script>
  (function() {
    const saved = localStorage.getItem('theme');
    const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', saved || preferred);
  })();
</script>
```

---

### 18. Invalid ARIA roles on welcome cards

**File:** `web/index.html` (lines 1684-1707)

**Problem:** Welcome cards use `role="listitem button"`. A single element cannot have two ARIA roles — screen readers only honor the first. The "button" semantics are lost.

**Fix:** Use `role="button"` alone (and add `tabindex="0"` + keyboard handler, which already exists via `cardKey`), or make the cards native `<button>` elements styled as cards.

---

### 19. No focus indicators on most interactive elements

**File:** `web/index.html`

**Problem:** While `.wcard:focus-visible` has a style, many other interactive elements (`.panel-btn`, `.rail-btn`, `.sug` suggestion chips, theme toggle, send button) only have `:hover` styles. Keyboard-only users have no visible focus indicator.

**Fix:** Add `:focus-visible` outlines to all interactive elements:
```css
.panel-btn:focus-visible,
.rail-btn:focus-visible,
.sug:focus-visible,
button:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
}
```

---

### 20. iOS zoom triggered by 14.5px input font size

**File:** `web/index.html` (line ~1288)

**Problem:** iOS Safari auto-zooms on inputs with font-size below 16px. The input uses `14.5px`, causing zoom on every focus.

**Fix:** Set the input font-size to 16px on mobile:
```css
@media (max-width: 720px) {
    .input-area textarea,
    .input-area input {
        font-size: 16px;
    }
}
```

---

### 21. Toast XSS via error message interpolation

**File:** `web/index.html` (line 2144)

**Problem:** The `toast()` function interpolates `msg` directly into `innerHTML` without escaping. Server error messages (which may contain HTML) flow into `msg` from `e.message` and `d.error`, enabling reflected XSS.

**Fix:** Escape `msg` before inserting into innerHTML:
```javascript
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
// Then in toast():
t.innerHTML = `...<span>${esc(msg)}</span>...`;
```

Or better: build the DOM with `createElement` and `textContent` instead of innerHTML.

---

### 22. CDN scripts without Subresource Integrity

**File:** `web/index.html` (lines 11-12)

**Problem:** DOMPurify and marked.js are loaded from `cdnjs.cloudflare.com` without `integrity` or `crossorigin` attributes. If the CDN is compromised, malicious scripts replace the legitimate ones. Since DOMPurify is the primary XSS defense, this is a supply-chain risk.

**Fix:** Add SRI hashes:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.6/purify.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

Generate hashes with: `curl -s <url> | openssl dgst -sha384 -binary | openssl base64 -A`

---

### 23. CLI has no retry/timeout/loading feedback

**File:** `main.py` (line 143)

**Problem:** `agent.chat()` blocks synchronously with no timeout or progress indication. If the model is slow (30+ seconds), the user stares at a blank terminal. If Ollama is briefly unreachable mid-conversation, the user must manually re-type their question.

**Fix:**
- Print a "Thinking..." message before the API call and clear it after.
- Catch `ConnectionError` and `TimeoutError` specifically and offer to retry.
- Add a configurable timeout to the Ollama client.

---

## LOW — Code Quality

### 24. Duplicate dependencies in requirements.txt

**File:** `requirements.txt` (lines 5/8, 6/9)

**Problem:** `fastapi>=0.109.0` and `uvicorn>=0.27.0` each appear twice.

**Fix:** Remove duplicate entries. The file should list each package once.

---

### 25. Unused dependencies

**File:** `requirements.txt` (lines 2, 7)

**Problem:** `python-dotenv` is never imported or used (no `load_dotenv()` call anywhere). `sse-starlette` is imported in `requirements.txt` but never used in `web/app.py`.

**Fix:** Remove both from `requirements.txt`. If streaming is implemented later (item #11), re-add `sse-starlette` at that time.

---

### 26. Dead code: models/user.py enums never wired into services

**Files:** `models/user.py`, `agent.py` (line 23), `__init__.py` (line 9)

**Problem:** `FinancialGoal`, `RiskTolerance`, and `UserProfile` are defined and exported but never used. `services/investment.py` uses raw strings for risk tolerance comparison instead of the `RiskTolerance` enum. `agent.py` imports them but never references them.

**Fix:** Either:
- (a) Wire `RiskTolerance` into `get_investment_recommendations()` as input validation, and `UserProfile` into a future user profile feature.
- (b) Remove the imports from `agent.py` and `__init__.py` until they're needed.

---

### 27. Class constants shadow module imports

**File:** `agent.py` (lines 163-165)

**Problem:** `KENYA_CONTEXT`, `INVESTMENT_OPTIONS`, and `TAX_BRACKETS` are imported from `config.constants` at the module level, then re-declared as class attributes on `KenyaWealthAgent`. This creates the impression that these are instance-specific when they are actually global shared data. Mutating `KenyaWealthAgent.TAX_BRACKETS` would mutate the shared constant.

**Fix:** Remove the class-level declarations. Access constants directly via `config.constants.KENYA_CONTEXT` etc., or keep the imports and document that they are shared module-level constants.

---

### 28. sys.path manipulation in web/app.py

**File:** `web/app.py` (line 15)

**Problem:** `sys.path.insert(0, str(Path(__file__).parent.parent))` modifies the global Python path, which is not thread-safe and could cause import conflicts if the module is loaded from different contexts.

**Fix:** Add a proper package structure with `pyproject.toml` and use relative imports, or use a `conftest.py`/`setup.py` for development. As a quick fix, this works for the current single-module deployment, but should be replaced with a proper package layout.

---

### 29. start_web.sh kills port 8000 with SIGKILL

**File:** `start_web.sh` (lines 42-44)

**Problem:** The script forcefully kills any process on port 8000 with `kill -9` (SIGKILL). This terminates processes ungracefully and could disrupt an unrelated service that happens to use the same port.

**Fix:**
- Use `SIGTERM` first (`kill -15`) and wait before resorting to `SIGKILL`.
- Warn the user and ask for confirmation before killing a process.
- Allow a `--port` flag to use a different port.

---

### 30. Budget expense key matching is case/whitespace-sensitive

**File:** `services/budget.py` (lines 59-60)

**Problem:** The function checks for exact keys like `"rent"`, `"transport"`, and `"airtime_data"`. If a caller passes `"Rent"`, `"RENT"`, or `" transport "` (with spaces), these checks fail silently and the corresponding recommendations are skipped.

**Fix:** Normalize expense keys before processing:
```python
expenses = {k.strip().lower(): v for k, v in expenses.items()}
```

---

### 31. get_config() silently ignores config_path after first call

**File:** `config/settings.py` (lines 135-147)

**Problem:** `get_config()` accepts a `config_path` parameter but silently ignores it on all calls after the first. A developer calling `get_config("/custom/path/config.ini")` on a running app would get the originally loaded config instead.

**Fix:** Either:
- (a) Raise a warning if `config_path` differs from the existing config's path.
- (b) Document clearly in the docstring that `config_path` is only used on the first call and point users to `reload_config()` for subsequent changes.

---

### 32. Broad except Exception in CLI swallows debuggable errors

**File:** `main.py` (line 161)

**Problem:** The outer `except Exception as e` catches all exceptions and prints them as user-facing errors. Programming bugs like `AttributeError`, `TypeError`, or `KeyError` are shown as generic errors without a traceback, making debugging difficult.

**Fix:** Catch specific exceptions for known failure modes and let programming bugs crash with tracebacks:
```python
except (ConnectionError, ollama.ResponseError) as e:
    print_error(f"Connection error: {e}")
    print_info("Check that Ollama is running and the model is pulled.")
except KeyboardInterrupt:
    # ... existing handling ...
except Exception as e:
    print_error(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
```