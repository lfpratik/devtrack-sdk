
<p align="center">
  <a href="https://github.com/swanadvi/devtrack-sdk" rel="noopener">
    <img width="200px" height="200px" src="../static/DevTrack.png" alt="DevTrack Logo">
  </a>
</p>

<h1 align="center">🚀 DevTrack SDK</h1>

<p align="center">
  Plug-and-play request tracking middleware for FastAPI apps. <br>
  <i>Built for devs who care about API usage, performance, and observability.</i>
</p>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/mahesh-solanke/devtrack-sdk.svg)](https://github.com/mahesh-solanke/devtrack-sdk/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/mahesh-solanke/devtrack-sdk.svg)](https://github.com/mahesh-solanke/devtrack-sdk/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

## 🧭 Table of Contents

- [🧐 About](#about)
- [🏁 Getting Started](#getting_started)
- [🚀 Deployment](#deployment)
- [🎈 Usage](#usage)
- [📊 Logged Fields](#logged_fields)
- [🧪 Testing](#tests)
- [⛏️ Built Using](#built_using)
- [✅ TODO](#todo)
- [🤝 Contributing](#contributing)
- [✍️ Authors](#authors)
- [🎉 Acknowledgements](#acknowledgement)

---

## 🧐 About <a name="about"></a>

**DevTrack SDK** is a powerful and lightweight middleware for FastAPI apps that automatically logs HTTP requests. Track path, method, status, duration, user agent, and more — right from your app with no extra configuration.

---

## 🏁 Getting Started <a name="getting_started"></a>

### 🧰 Prerequisites

```bash
python >= 3.8
pip install fastapi httpx starlette
```

### 📥 Installation

```bash
git clone https://github.com/mahesh-solanke/devtrack-sdk.git
cd devtrack-sdk
pip install -e .
```

### 🧩 Middleware Integration

```python
from fastapi import FastAPI
from devtrack_sdk.middleware import DevTrackMiddleware
from devtrack_sdk.devtrack_routes import router as devtrack_router

app = FastAPI()
app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware, api_key="dummy-key")
```

---

## 🚀 Deployment <a name="deployment"></a>

```bash
uvicorn examples.fastapi_example:app --reload
```

Then test with:

```bash
curl http://localhost:8000/__devtrack__/stats
```

---

## 🎈 Usage <a name="usage"></a>

All tracked data is stored in memory and served via:

```
GET /__devtrack__/stats
```

---

## 📊 Logged Fields <a name="logged_fields"></a>

Each request is logged with these fields:

- `path`: request endpoint
- `method`: HTTP method (GET, POST, etc.)
- `status_code`: HTTP response code
- `timestamp`: ISO timestamp (UTC)
- `client_ip`: origin IP address
- `duration_ms`: time taken for request to complete
- `user_agent`: browser/client making the request
- `referer`: previous page (if any)
- `query_params`: any query string data
- `request_body`: POST/PUT payload (filtered)
- `response_size`: response size in bytes
- `user_id`, `role`: if available from headers or token
- `trace_id`: unique ID for each request

---

## 🧪 Testing <a name="tests"></a>

```bash
pip install -r requirements.txt
pytest tests
```

#### ✅ Example test:

```python
def test_stats_endpoint():
    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
```

---

## ⛏️ Built Using <a name="built_using"></a>

- 🔹 [FastAPI](https://fastapi.tiangolo.com/)
- 🔹 [Starlette](https://www.starlette.io/)
- 🔹 [httpx](https://www.python-httpx.org/)

---

## ✅ TODO <a name="todo"></a>

- [x] In-memory logging
- [x] Full request metadata (duration, headers, etc.)
- [ ] DB persistence (SQLite/PostgreSQL)
- [ ] Rich dashboard UI with charts and filters

---

## 🤝 Contributing <a name="contributing"></a>

We ❤️ contributions! Please:

1. Fork this repo
2. Create your branch (`git checkout -b feat/awesome-feature`)
3. Commit your changes (`git commit -m '✨ Add awesome feature'`)
4. Push to the branch (`git push origin feat/awesome-feature`)
5. Open a Pull Request

Run `pre-commit run --all-files` before committing 🙏

---

## ✍️ Authors <a name="authors"></a>

- [Mahesh Solanke](https://github.com/swanadvi) - Core Dev & Maintainer

---

## 🎉 Acknowledgements <a name="acknowledgement"></a>

- ✨ Inspired by FastAPI's middleware design
- 💡 Thanks to the open-source community for tooling and inspiration
