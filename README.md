# Academic Support Request & Policy Management System

## 1. Project Overview

The Academic Support Request & Policy Management System is a Python-based data generation and management project designed to simulate academic support operations.

It generates synthetic academic support tickets, requesters, assignments, messages, service-level agreement (SLA) records, policy documents, and knowledge articles.

SQLite is used for relational data storage, while Python libraries support synthetic data generation, validation, testing, and data exports.

## 2. Project Objectives

- Generate a synthetic academic support dataset.
- Maintain relational database tables and foreign key relationships.
- Generate tickets with different priorities and statuses.
- Create assignment and SLA records.
- Generate policy documents and knowledge articles.
- Validate database integrity and record counts.
- Export datasets into CSV and JSON formats.
- Test important data requirements using pytest.

## 3. Technology Stack

- Python
- SQLite
- Pandas
- NumPy
- Faker
- Pytest
- CSV and JSON

## 4. Dataset Summary

| Entity | Records |
|---|---:|
| Role | 3 |
| Requester | 500 |
| Term | 3 |
| Category | 6 |
| Ticket | 5,000 |
| Assignment | 5,000 |
| SLA | 5,000 |
| Message | 20,000 |
| PolicyDocument | 200 |
| KnowledgeArticle | 200 |
| **Total** | **35,912** |

All generated records are synthetic and intended for demonstration and testing.

## 5. Project Structure

```text
yottaflex_academic_support/
├── data/
│   └── academic_support.db
├── outputs/
│   ├── csv/
│   └── json/
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── data_generator.py
│   ├── validator.py
│   ├── export_data.py
│   ├── ticket_router.py
│   ├── policy_engine.py
│   └── sla_manager.py
├── tests/
│   └── test_validation.py
├── main.py
├── requirements.txt
└── README.md
```

## 6. Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd yottaflex_academic_support
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 7. Running the Project

Create the database:

```bash
python -m src.database
```

Generate synthetic data:

```bash
python -m src.data_generator
```

Validate the database:

```bash
python -m src.validator
```

Export CSV and JSON datasets:

```bash
python -m src.export_data
```

Run automated tests:

```bash
python -m pytest -v
```

## 8. Validation and Testing

The project includes automated validation for:

- Expected record counts.
- Foreign key integrity.
- Ticket status values.
- Ticket priority values.
- Unique policy codes.
- Unique knowledge article codes.
- Required ticket fields.
- Required message fields.

Latest recorded test result: **9 tests passed**.

## 9. Output Files

The project produces:

- SQLite relational database.
- CSV files for generated entities.
- JSON files for generated entities.

## 10. Assumptions and Limitations

- All records are synthetic demonstration data.
- SLA rules and ticket workflows are implemented for demonstration purposes.
- Policy documents and knowledge articles are not official institutional policies.
- The project does not connect to a real university or external institutional system.
- Automated tests cover the documented validation requirements; they do not establish production readiness.
- Additional testing and improvements may be required before real-world deployment.

## 11. AI Assistance Disclosure

AI tools were used to assist with understanding requirements, planning the project structure, generating and reviewing implementation code, explaining errors, and preparing documentation.

The project author ran the application, reviewed implementation behavior, and performed database validation and automated tests. The author is responsible for understanding and explaining the submitted code.

A separate `PROMPT_HISTORY.md` file documents AI prompts and usage.

## 12. Data Disclaimer

This project uses synthetic demonstration data. The policy documents, knowledge articles, tickets, and messages do not represent actual institutional records or official university policies.

## 13. Author

Python Full Stack Developer | Fresher

GitHub: YOUR_GITHUB_PROFILE_URL