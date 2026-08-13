# 🇰🇪 Kenya Wealth Agent - Project Master Roadmap

This is the single source of truth for the development, security, and evolution of the Kenya Wealth Agent.

## 📊 Project Health Dashboard
| Category | Status | Open Issues | Priority Focus |
| :--- | :--- | :--- | :--- |
| **Security** | ⚠️ Attention Required | 10 | 🔴 Critical XSS Fix |
| **UI/UX** | ✅ Stable/Improving | 7 | 🟡 Streaming Backend |
| **Core Logic** | 🟢 Healthy | 3 | 🟢 Type Hinting |

---

## 🛠 Technical Debt & Security (The "Fix" List)
*Consolidated from `TODO_SECURITY.md` and `TODO_SECURITY_FIXES.txt`*

### 🔴 CRITICAL - Immediate Action
| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **XSS Vulnerability** | `templates/html.py` | Arbitrary JS execution in reports | Use `html.escape()` on user content | [ ] PENDING |

### 🟠 HIGH - Fix Within 1 Week
| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Unsafe Subprocess** | `agent.py` | Shell injection via `os.system` | Replace with `subprocess.run()` | [ ] PENDING |
| **Duplicate Config** | `config/loader.py` | Unpredictable behavior/settings | Keep dataclass version, delete duplicate | [ ] PENDING |

### 🟡 MEDIUM - Fix Within 1 Month
| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Input Validation** | `agent.py` | DoS via oversized/null input | Add length and type checks in `chat()` | [ ] PENDING |
| **Monolithic main()** | `main.py` | Low maintainability | Extract to `CLIHandler` class | [ ] PENDING |
| **Financial Disclaimer**| `templates/html.py`| Legal liability | Add disclaimer to HTML report footer | [ ] PENDING |

### 🟢 LOW - Schedule as Time Permits
| Issue | Impact | Action | Status |
| :--- | :--- | :--- | :--- |
| **Test Suite** | Quality/Regressions | Create `tests/` directory with pytest | [ ] PENDING |
| **Magic Numbers** | Readability | Move hardcoded tax rates to `constants.py` | [ ] PENDING |
| **Unused Imports** | Code Noise | Remove `import re` in `html.py` | [ ] PENDING |
| **Type Hinting** | DX/Stability | Standardize `Optional` and type hints across project | [ ] PENDING |

---

## 🎨 User Experience & Interface (The "Polish" List)
*Consolidated from `UI_IMPROVEMENTS.md` and `IMPROVEMENTS_SUMMARY.md`*

### ✅ Implemented (Successes)
- **Layout Fix**: `flex-shrink: 0` on sidebar prevents disappearing.
- **Interactivity**: Collapsible sidebar with `localStorage` persistence.
- **Navigation**: "Jump to Bottom" button for long conversations.
- **Accessibility**: ARIA labels, keyboard navigation, and contrast improvements.
- **Performance**: Message virtualization (max 50 visible) to prevent DOM lag.

### 🚀 Planned Improvements
- [ ] **Backend Streaming**: Implement true server-sent events for "typing" effect.
- [ ] **Offline Support**: Service workers for basic offline access.
- [ ] **Theming**: Formal Light/Dark mode toggle.
- [ ] **i18n**: Support for Swahili and other local languages.
- [ ] **User Preferences**: Persistent settings for risk tolerance and goals.

---

## 🚀 Feature Evolution (The "Growth" List)
*High-level strategic goals*

- [ ] **Persistent Profiles**: Migrate from session-based memory to a database (SQLite/PostgreSQL) to remember users.
- [ ] **Real-time Market Data**: Integrate with NSE (Nairobi Securities Exchange) API for live stock/bond prices.
- [ ] **Multi-Agent Orchestration**: Separate the "Tax Specialist" from the "Investment Expert" using specialized sub-agents.
- [ ] **Export Formats**: Add PDF and CSV export options for financial reports.

---

## 📂 Archive Reference
The following files have been deprecated and moved to `.archive/`:
- `TODO_SECURITY.md`
- `TODO_SECURITY_FIXES.txt`
- `UI_IMPROVEMENTS.md`
- `IMPROVEMENTS_SUMMARY.md`
