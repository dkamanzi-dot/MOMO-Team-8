# MoMo Transaction Analytics System

## Team 8

### Team Members

1. **Olivier Dusabamahoro**
2. **Daniel Kenny Kamanzi**
3. **Divin Manzi Mulinda Elvis**

---

## Project Description

The **MoMo Transaction Analytics System** is an enterprise-level full-stack application designed to process Mobile Money (MoMo) SMS data stored in XML format.

The system will extract transaction information from XML data, clean and normalize the information, categorize transactions based on their types, store the processed data in a relational database, and provide a web-based dashboard for analyzing and visualizing the transaction data.

The project aims to transform raw MoMo SMS data into structured and meaningful information that can be used to understand transaction patterns, amounts, transaction types, and other relevant financial insights.

### Main Objectives

* Parse MoMo SMS data from XML format.
* Clean and normalize transaction data.
* Categorize transactions according to their types.
* Store structured transaction data in a relational database.
* Generate useful transaction analytics.
* Provide a web dashboard for data visualization.
* Follow a collaborative Agile development workflow.

---

## System Architecture

The planned system follows an ETL-based architecture:

```text
MoMo XML Data
      │
      ▼
┌──────────────────┐
│    XML Parser    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ Cleaning & Normalization │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Transaction Categorizing │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────┐
│  SQLite Database │
└────────┬─────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌─────────┐ ┌──────────────┐
│ FastAPI │ │ Dashboard    │
│   API   │ │ JSON Data    │
└────┬────┘ └──────┬───────┘
     │             │
     └──────┬──────┘
            ▼
   ┌──────────────────┐
   │  Web Dashboard   │
   │ Charts & Tables  │
   └──────────────────┘
```

### Architecture Diagram

The detailed architecture diagram is available in:

`docs/architecture.png`

---

## Scrum Board

Team 8 uses a Scrum board to organize project tasks and track progress.

**Scrum Board:** [Insert Scrum Board Link Here]

The board contains the following columns:

* **To Do**
* **In Progress**
* **Done**

---

## Planned Technology Stack

### Backend

* Python
* ElementTree / lxml
* FastAPI

### Database

* SQLite

### Frontend

* HTML
* CSS
* JavaScript
* JavaScript charting library

### Testing

* pytest

### Development Tools

* Git
* GitHub
* Draw.io
* GitHub Projects / Trello / Jira

---

## Project Structure

```text
.
├── README.md
├── .env.example
├── requirements.txt
├── index.html
│
├── web/
│   ├── styles.css
│   ├── chart_handler.js
│   └── assets/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── logs/
│       ├── etl.log
│       └── dead_letter/
│
├── etl/
│   ├── __init__.py
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
│
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── db.py
│   └── schemas.py
│
├── scripts/
│   ├── run_etl.sh
│   ├── export_json.sh
│   └── serve_frontend.sh
│
├── tests/
│   ├── test_parse_xml.py
│   ├── test_clean_normalize.py
│   └── test_categorize.py
│
└── docs/
    └── architecture.png
```

---

## Development Workflow

Team 8 will use GitHub for collaborative development.

Each team member will work on assigned tasks using Git branches. Completed work will be reviewed and merged into the main branch.

The Scrum board will be used to track the progress of tasks from **To Do** to **In Progress** and finally to **Done**.

---

## Team Goal

Team 8 aims to develop a reliable and user-friendly MoMo Transaction Analytics System that transforms raw SMS transaction data into structured information and meaningful visual insights.

