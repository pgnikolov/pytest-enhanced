# 🧪 pytest-enhanced

[![PyPI version](https://img.shields.io/pypi/v/pytest-enhanced.svg?color=blue&label=PyPI)](https://pypi.org/project/pytest-enhanced/)
[![Python version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Pytest Enhanced** — a CLI + plugin for `pytest` that adds analytics and insight:  
> flaky tests, slow tests, and pass-rate trends across runs.  
> No CI integration needed — works locally, instantly.

---

## 🚀 Features

- 📊 **Analytics for your tests**
  - Detect flaky or unstable tests automatically  
  - Identify slow tests and bottlenecks  
  - View historical pass-rate trends  
- ⚡ **Zero configuration**
  - Just run `pytest --enhanced`
  - Works with any existing test suite  
- 💾 **SQLite storage**
  - Keeps history across multiple runs  
  - Easy export and analysis  
- 🎨 **Beautiful CLI reports**
  - Built with [`rich`](https://github.com/Textualize/rich)

## 📦 Installation

```bash
pip install pytest-enhanced
````

Or install from source for development:

```bash
git clone https://github.com/<your_username>/pytest-enhanced.git
cd pytest-enhanced
pip install -e .[dev]
```

---

## 🧠 Usage

Run your tests with the `--enhanced` flag:

```bash
pytest --enhanced
```

Then view your analytics:

```bash
pytest-enhanced report
```

### Example output

```
📊 Pytest Enhanced Report — Run #3
────────────────────────────────────────────
Total tests: 3
Passed: 3  |  Failed: 0  |  Skipped: 0
Pass rate: 100.0%

🐢 Slowest tests:
  demo_tests/test_sample.py::test_slow_one      1.20s
  demo_tests/test_sample.py::test_always_pass   0.00s

🔥 Flaky tests:
  No flaky tests detected (min 2 fails in last 20 runs)

📈 Pass rate trend:
  🟩
  Run 3: 100.0%

Tip: Unstable tests usually depend on timing, randomness, or external services.
```

---

## ⚙️ CLI Commands

| Command                  | Description                            |
| ------------------------ | -------------------------------------- |
| `pytest-enhanced report` | Show full analytics for the latest run |
| `pytest-enhanced slow`   | Show slowest tests                     |
| `pytest-enhanced flaky`  | List tests that failed intermittently  |

---

## 🗂️ Project Structure

```
pytest-enhanced/
├── pytest_enhanced/
│   ├── plugin.py          # pytest hooks
│   ├── storage.py         # SQLite logic
│   ├── analysis.py        # metrics & statistics
│   ├── cli.py             # Typer CLI entry
│   ├── report.py          # Rich terminal output
│   └── utils.py
└── tests/
```

---

## 🧩 Roadmap

* [ ] `export` command — CSV / JSON export of historical data
* [ ] GitHub Action for automatic analytics in CI
* [ ] Cloud dashboard (FastAPI backend)
* [ ] HTML reports
* [ ] Slack / Teams notifications for flaky tests

---

## 🤝 Contributing

Contributions are welcome!
Feel free to:

* open pull requests,
* suggest new CLI commands, or
* report issues via GitHub.

---

## 📄 License

Licensed under the [MIT License](LICENSE).

---

## 💬 About

Created by **Plamen Nikolov** — developer tools enthusiast & Python practitioner.
