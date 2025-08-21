#  Store Monitoring System

A **comprehensive backend API system** for monitoring restaurant store uptime and generating detailed reports.
Built with **FastAPI**, **SQLAlchemy**, and advanced **business hours logic**.

---

## 📌 Table of Contents

* [Architecture](#-system-architecture)
* [Data Flow](#-data-flow-diagram)
* [API Sequences](#-api-sequences)
* [Features](#-features)
* [Project Structure](#-project-structure)
* [API Endpoints](#-api-endpoints)
* [Setup Instructions](#-setup-instructions)
* [Testing](#-testing)
* [Key Features Explained](#-key-features-explained)
* [Performance Considerations](#-performance-considerations)
* [Error Handling](#-error-handling)
* [Sample Output](#-sample-output)
* [Future Improvements](#-improvements-for-production)

---

## 🏗 System Architecture

![System Flow](https://github.com/user-attachments/assets/f0469a4f-46a1-4557-ba09-f37fda7b2dba)

---

## 🔄 Data Flow Diagram

![Data Flow](https://github.com/user-attachments/assets/4bfe5208-1881-4e60-83d5-a16daea5e5a7)

---

## 📡 API Sequences

![API Sequence](https://github.com/user-attachments/assets/f32bec5d-d4c1-49d9-8d9d-92c88885ac82)

---

## ✨ Features

* ⚡ **Async Report Generation** – trigger reports & poll for completion
* 🕒 **Business Hours Support** – including overnight operations
* 🌍 **Timezone Conversion** – with DST handling
* 📊 **Data Interpolation** – extrapolates uptime/downtime from sparse polling data
* 📑 **CSV Export** – validated reports with statistics & formatting
* 🛠 **RESTful API** – clean FastAPI endpoints with robust error handling

---

## 📂 Project Structure

```bash
store-monitoring/
├── main.py                    # FastAPI app & routes
├── models.py                  # SQLAlchemy models
├── database.py                # DB config & session
├── data_processor.py          # Data import logic
├── report_generator.py        # Core reporting engine
├── report_service.py          # Service layer
├── business_hours_utils.py    # Business hours logic
├── csv_export_utils.py        # CSV utilities
├── data_import_script.py      # Data ingestion script
├── run_server.py              # App entrypoint
├── tests/                     # Unit & API tests
│   ├── test_api.py
│   └── test_business_hours.py
├── requirements.txt
├── start_server.sh
├── data/                      # CSV input files
└── reports/                   # Generated CSV reports
```

---

## 🔌 API Endpoints

### 1️⃣ Trigger Report

```http
POST /trigger_report
```

**Response:**

```json
{ "report_id": "uuid-string" }
```

**Example:**

```bash
curl -X POST http://localhost:8000/trigger_report
```

---

### 2️⃣ Get Report Status / Download

```http
GET /get_report/{report_id}
```

**Running Response:**

```json
{ "status": "Running", "created_at": "timestamp" }
```

**Completed Response:** Downloads CSV

```csv
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
```

---

### 3️⃣ Health Check

```http
GET /health
```

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Place CSV files in the `data/` folder:

* `store_status.csv`
* `business_hours.csv`
* `store_timezones.csv`

### 3. Import Data

```bash
python data_import_script.py
```

### 4. Start Server

```bash
python run_server.py
# OR
./start_server.sh
```

API available at 👉 `http://localhost:8000`

---

## 🧪 Testing

```bash
# Run API tests
pytest tests/test_api.py

# Test business hours logic
pytest tests/test_business_hours.py

# Generate sample reports
python generate_sample_report.py
```

---

## 🔍 Key Features Explained

### 🕒 Business Hours Logic

* Supports **normal** (9 AM – 5 PM) and **overnight** (10 PM – 6 AM) schedules
* Handles **timezone conversion + DST**
* Defaults: **24/7** if hours missing, **America/Chicago** if timezone missing

### 📊 Report Algorithm

1. Collects store status data (last hour/day/week)
2. Converts UTC → local store time
3. Filters by business hours
4. Interpolates uptime/downtime
5. Aggregates by time period
6. Exports validated CSV

---

## 📉 Sample Output

```csv
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
store_0001,58.50,22.75,165.25,1.50,1.25,2.75
store_0002,45.25,18.50,142.00,14.75,5.50,26.00
```

---

## 🚀 Improvements for Production

* **Database** → PostgreSQL + indexing + partitioning
* **Caching** → Redis, query result caching
* **Scalability** → Celery + Kubernetes + microservices
* **Monitoring** → Prometheus, OpenTelemetry, structured logs
* **Security** → JWT, RBAC, rate limiting, encryption
* **Advanced Features** → Scheduling, custom ranges, visual dashboards
* **DevOps** → CI/CD, API versioning, feature flags


