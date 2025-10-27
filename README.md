# 🧪 pytest-enhanced

[![PyPI version](https://img.shields.io/pypi/v/pytest-enhanced.svg?color=blue\&label=PyPI)](https://pypi.org/project/pytest-enhanced/)
[![Python version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/pgnikolov/pytest-enhanced/actions/workflows/pytest-enhanced.yml/badge.svg)](https://github.com/pgnikolov/pytest-enhanced/actions)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Pytest Enhanced** — a smarter `pytest` companion that adds analytics, stability tracking,
> and CLI reports for developers who want insights, not just pass/fail output.

---

## 🚀 Why pytest-enhanced?

| Feature                        | ✅ pytest-enhanced | ⚪ vanilla pytest    |
| :----------------------------- | :---------------- | :------------------ |
| Detect flaky tests             | ✅ Yes             | ❌ No                |
| Show slowest tests             | ✅ Yes             | ⚪ Basic timing only |
| Pass-rate history              | ✅ Yes             | ❌ No                |
| Persistent history (SQLite)    | ✅ Yes             | ❌ No                |
| CSV / JSON export              | ✅ Yes             | ❌ No                |
| Rich CLI reports               | ✅ Yes             | ❌ Plain text        |
| CI-ready analytics             | ✅ Yes             | ⚪ Limited           |
| HTML / dashboard (coming soon) | 🚧 Planned        | ❌ No                |

> 🧠 *Built for developers who care about test reliability, not just test counts.*

---

## 🧩 Features

* 📊 **Analytics for your tests**

  * Detect flaky or unstable tests automatically
  * Identify slow tests and performance bottlenecks
  * View historical pass-rate trends
* ⚡ **Zero configuration**

  * Just run `pytest --enhanced`
  * Works with any test suite, immediately
* 💾 **SQLite storage**

  * Keeps history across multiple runs
  * Simple local database, no external services
* 🧮 **Export your test history**

  * Export all test data to CSV or JSON
  * Perfect for CI pipelines or dashboards
* 🎨 **Beautiful CLI reports**

  * Powered by [`rich`](https://github.com/Textualize/rich)

---

## 📦 Installation

```bash
pip install pytest-enhanced
```

Or for development:

```bash
git clone https://github.com/pgnikolov/pytest-enhanced.git
cd pytest-enhanced
pip install -e .[dev]
```

---

## 🧠 Usage

Run your tests with enhanced tracking:

```bash
pytest --enhanced
```

Then view analytics:

```bash
pytest-enhanced report
```

Or inspect specific metrics:

```bash
pytest-enhanced slow
pytest-enhanced flaky
pytest-enhanced export --format csv
```

---

### 📈 Example output

```
📊 Pytest Enhanced Report — Run #5
────────────────────────────────────────────
Total tests: 8
Passed: 7  |  Failed: 1  |  Skipped: 0
Pass rate: 87.5%

🐢 Slowest tests:
  demo_tests/test_sample.py::test_slow_one      1.24s
  demo_tests/test_sample.py::test_api_latency   0.93s

🔥 Flaky tests:
  test_random_fail                             2 fails / 10 runs (20.0%)

📈 Pass rate trend:
  Run 5: 87.5%
  Run 4: 100.0%
  Run 3: 90.0%
  Run 2: 100.0%
  Run 1: 95.0%
```

---

## ⚙️ CLI Commands

| Command                  | Description                            |
| ------------------------ | -------------------------------------- |
| `pytest-enhanced report` | Show full analytics for the latest run |
| `pytest-enhanced slow`   | Display the slowest tests              |
| `pytest-enhanced flaky`  | List flaky or unstable tests           |
| `pytest-enhanced export` | Export results to CSV or JSON          |

---

## 📤 Exporting test data

Export full history to CSV:

```bash
pytest-enhanced export --format csv --output results.csv
```

Or JSON:

```bash
pytest-enhanced export --format json --limit 100
```

Artifacts can be uploaded automatically in CI pipelines.

---

## 🗂️ Project Structure

```
pytest-enhanced/
├── pytest_enhanced/
│   ├── plugin.py          # pytest hooks
│   ├── storage.py         # SQLite logic
│   ├── analysis.py        # metrics & stats
│   ├── cli.py             # Typer CLI commands
│   ├── report.py          # rich output formatting
│   └── utils.py           # helpers
├── demo_tests/            # example test files
└── tests/                 # internal tests
```

---

## ⚙️ CI Integration

✅ Includes a workflow: `.github/workflows/pytest-enhanced.yml`

Automatically:

* runs tests with `pytest --enhanced`
* exports analytics to CSV
* uploads report as a GitHub Action artifact

View data in **Actions → Artifacts**.

---

## 🧩 Roadmap

✅ CSV / JSON export command
☑️ GitHub Action for CI analytics
⬜ FastAPI-based web dashboard
⬜ HTML reports (rich → static)
⬜ Slack / Teams notifications for flaky tests

---

## 🤝 Contributing

Contributions welcome!
You can:

* Submit pull requests
* Propose new analytics features
* Open issues or ideas

---

## 📄 License

Licensed under the [MIT License](LICENSE).

---

## 💬 About

Created by **Plamen Nikolov** —
Python engineer, developer tooling enthusiast, and maker of things that improve test quality.

---

> ⚡ *“You can’t fix what you don’t measure — pytest-enhanced helps you see the real picture.”*

---