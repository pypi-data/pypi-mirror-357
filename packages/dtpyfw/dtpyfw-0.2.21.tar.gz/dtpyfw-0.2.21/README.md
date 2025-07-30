# DealerTower Python Framework (dtpyfw)

**DealerTower Framework** provides reusable building blocks for microservices. It is organized into modular sub-packages focused on different domains: Core, API, Database, Bucket, FTP, Redis, Kafka, Worker, Log, and Encryption.

---

## 🚀 Installation

Requires **Python 3.11** or newer.

### Base package & Core

```bash
pip install dtpyfw
```

### Package Metadata

Query the installed version programmatically:

```python
import dtpyfw
print(dtpyfw.__version__)
```

### Optional Extras

Install just the features you need; extras can be combined, for example `pip install dtpyfw[api,db]`.

| Sub-Package | Description | Install Command | Docs |
| ----------- | ----------- | --------------- | ---- |
| **core**    | Env, errors, async bridge, utils | included in base | [Core Docs](docs/CORE.MD) |
| **api**     | FastAPI middleware & routing helpers | `pip install dtpyfw[api]` | [API Docs](docs/API.MD) |
| **db**      | SQLAlchemy sync/async & search tools | `pip install dtpyfw[db]` | [DB Docs](docs/DB.MD) |
| **bucket**  | S3-compatible file management | `pip install dtpyfw[bucket]` | [Bucket Docs](docs/BUCKET.MD) |
| **ftp**     | FTP and SFTP convenience wrappers | `pip install dtpyfw[ftp]` | [FTP Docs](docs/FTP.MD) |
| **redis**   | Redis clients & Streams consumer | `pip install dtpyfw[redis]` | [Redis Docs](docs/REDIS.MD) |
| **kafka**   | Kafka messaging utilities | `pip install dtpyfw[kafka]` | [Kafka Docs](docs/KAFKA.MD) |
| **worker**  | Celery task & scheduler setup | `pip install dtpyfw[worker]` | [Worker Docs](docs/WORKER.MD) |
| **log**     | Structured logging helpers | included in base | [Log Docs](docs/LOG.MD) |
| **encrypt** | Password hashing & JWT utilities | `pip install dtpyfw[encrypt]` | [Encryption Docs](docs/ENCRYPT.MD) |
| **slim-task** | DB, Redis, Worker | `pip install dtpyfw[slim-task]` | — |
| **slim-api**  | API, DB | `pip install dtpyfw[slim-api]` | — |
| **normal**    | API, DB, Redis, Worker | `pip install dtpyfw[normal]` | — |
| **all**       | Everything above | `pip install dtpyfw[all]` | — |

---

## 📦 Sub-Package Summaries

### Core

Essential utilities for environment management, error handling, async bridging and general helpers. [Core Docs](docs/CORE.MD)

### API

FastAPI application factory, middleware and routing helpers. [API Docs](docs/API.MD)

### Database

Sync and async SQLAlchemy orchestration with search helpers. [DB Docs](docs/DB.MD)

### Bucket

S3-compatible storage convenience functions. [Bucket Docs](docs/BUCKET.MD)

### FTP/SFTP

Unified clients for FTP and SFTP operations. [FTP Docs](docs/FTP.MD)

### Redis & Streams

Redis caching utilities and Streams consumers/senders. [Redis Docs](docs/REDIS.MD)

### Kafka

Producer and consumer wrappers for Kafka messaging. [Kafka Docs](docs/KAFKA.MD)

### Worker

Helpers for configuring Celery workers and schedules. [Worker Docs](docs/WORKER.MD)

### Log

Structured logging configuration and helpers. [Log Docs](docs/LOG.MD)

### Encryption

Password hashing and JWT helpers. [Encryption Docs](docs/ENCRYPT.MD)

---

## 📄 License

DealerTower Python Framework is proprietary. See [LICENSE](LICENSE) for terms.
