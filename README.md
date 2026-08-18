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

1. **`Query Planner` (`src/query_planner.py`)**:
   - Evaluates the user's natural language question alongside conversation history and system datetime.
   - Uses Pydantic (`QueryPlan`) for strict schema validation.
   - Produces a structured JSON query plan (`filter`, `list`, `count`, `unique`).
   - **No arbitrary Python code generation!**

2. **`Pandas Query Executor` (`src/query_executor.py`)**:
   - Executes the structured JSON query plan safely using pre-defined Pandas filtering methods.
   - Supports case-insensitive string matching, numeric range comparison, date/time filtering, sorting, limits, counts, and unique value extractions.

3. **`Validator Node` (`src/validator.py`)**:
   - Validates that the query plan exists and executed without exceptions.
   - If execution fails due to invalid parameters or schema mismatches, routes state back to the `Query Planner` for a retry attempt (up to 3 retries).

4. **`Answer Generator` (`src/answer_generator.py`)**:
   - Takes the original question, query plan, and executed data summary to compose a friendly, accurate, natural language response.

---

## 🛠️ Project Structure

```text
Student-CSV-AI-Assistant/
│
├── app.py                      # Main Streamlit web application UI
├── data/
│   └── student_schedule_synthetic_1250.csv  # Included sample dataset
├── src/
│   ├── __init__.py             # Module initialization
│   ├── llm_client.py           # Dedicated Mistral AI LLM client factory
│   ├── state.py                # LangGraph state schema definition
│   ├── graph.py                # Parameterless LangGraph workflow compilation
│   ├── query_planner.py        # Query Planner node (JSON plan & Pydantic schema)
│   ├── query_executor.py       # Safe Pandas query executor node
│   ├── validator.py            # Validation node & conditional routing edge
│   ├── answer_generator.py     # Answer Generator node
│   ├── prompts.py              # System prompts & date/time resolution instructions
│   ├── data_loader.py          # CSV loader & cached schema extractor
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
```

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
- **Pydantic Validation**: Automatically validates plan structure and handles null/default list conversions gracefully.
- **Natural Date/Time Handling**: Resolves relative dates like *today*, *tomorrow*, *next Monday*, and *5 PM* dynamically using standard Python `datetime`.
- **Zero API Key Leakage**: API keys are excluded from all logs and loaded via `.env`.