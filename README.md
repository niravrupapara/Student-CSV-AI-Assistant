# 🎓 Student CSV AI Assistant

A simple, clean, and modular **Student CSV AI Agent** built with **Python**, **Streamlit**, **LangGraph**, **LangChain**, and **Mistral AI**.

This application allows students and administrators to upload a CSV containing student schedules/attendance data and ask natural-language questions about lectures, teachers, classrooms, timings, and schedules.

---

## 🏗️ LangGraph Architecture

The system uses a stateful **LangGraph** workflow that guarantees safe, validated query generation without executing arbitrary Python or Pandas code.

```text
User Question
      ↓
Query Planner (Mistral)
      ↓
Pandas Query Executor
      ↓
Validator Node
      ↓
 ┌────┴────┐
 │         │
Valid    Invalid
 │         │
 ↓         ↓
Answer   Retry/Planner Loop (up to 3 retries)
Generator
 │
 ↓
END
```

### LangGraph Nodes Breakdown:

1. **`Query Planner` (Mistral)**:
   - Evaluates the user's natural language question alongside conversation history and current system date/time.
   - Inspects the uploaded CSV's column names, data types, distinct sample values, and sample rows.
   - Produces a structured, validated JSON `QueryPlan` specifying allowed operations (`filter`, `list`, `count`, `unique`), filters, columns, sorting, limits, or target columns.
   - **No arbitrary Python code generation!**

2. **`Pandas Query Executor`**:
   - Executes the structured JSON query plan safely using pre-defined Pandas filtering methods.
   - Supports case-insensitive string matching, date/time filtering, sorting, limits, counts, and unique value extractions.

3. **`Validator`**:
   - Checks if the query plan was generated without structure errors and executed without exceptions.
   - If execution fails due to invalid parameters or schema mismatches, routes state back to the `Query Planner` for a retry attempt with error feedback (up to 3 retries).
   - If no rows match, it is treated as a valid query result rather than a system error.

4. **`Answer Generator` (Mistral)**:
   - Takes the original question, query plan, and executed data summary to compose a friendly, accurate, natural language response for the student.

---

## 🛠️ Project Structure

```text
Student-CSV-AI-Assistant/
│
├── app.py                      # Main Streamlit web application
├── data/
│   └── student_schedule_synthetic_1250.csv  # Included sample student schedule dataset
├── src/
│   ├── __init__.py
│   ├── state.py                # LangGraph state schema definition
│   ├── graph.py                # LangGraph workflow compilation & node routing
│   ├── query_planner.py        # Query Planner node (JSON plan generator)
│   ├── query_executor.py       # Safe Pandas query executor module
│   ├── answer_generator.py     # Answer Generator node (natural language responses)
│   ├── prompts.py              # LLM system prompts & date/time resolution rules
│   ├── data_loader.py          # CSV loading & schema metadata extractor
│   └── logger.py               # Centralized logging module
│
├── logs/
│   └── app.log                 # Rotating file logs (created automatically)
├── .env                        # Local environment variables
├── .env.example                # Example environment setup
├── .gitignore                  # Git ignore configuration
├── requirements.txt            # Project Python dependencies
└── README.md                   # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Copy `.env.example` to `.env` and add your **Mistral API Key**:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-latest
```
*(Alternatively, you can enter your API Key directly in the Streamlit sidebar at runtime).*

### 4. Run the Application
Launch the Streamlit app:
```bash
streamlit run app.py
```

---

## 💡 Example Questions

- `"What lecture do I have tomorrow at 5 PM?"`
- `"Who teaches Machine Learning?"`
- `"Where is my Natural Language Processing lecture?"`
- `"How many lectures do I have on Thursday?"`
- `"Who teaches the last lecture of the day?"` *(Understands context & relative ordering)*

---

## 🛡️ Security & Reliability Features

- **No Code Execution Injection**: The LLM output is strictly parsed as a JSON query plan and executed against pre-defined DataFrame operations.
- **Natural Date/Time Handling**: Resolves relative dates like *today*, *tomorrow*, *next Monday*, and *5 PM* dynamically using standard Python `datetime`.
- **Zero API Key Leakage**: API keys are excluded from all logs.