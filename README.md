# 🎓 Student CSV AI Assistant

A clean, modular, and optimized **Student CSV AI Agent** built with **Python**, **Streamlit**, **LangGraph**, **LangChain**, and **Mistral AI**.

This application allows students and administrators to upload a CSV file containing academic schedules or student records and ask natural-language questions about lectures, teachers, classrooms, timings, and attendance.

---

## 🏗️ LangGraph Architecture & Workflow

The core agent workflow is orchestrated using **LangGraph** to ensure predictable, structured query generation without executing arbitrary Python/Pandas scripts.

```text
       ┌────────────────────────┐
       │     User Question      │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │      Query Planner     │  (Mistral LLM extracts filters & target columns as JSON)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │     Query Executor     │  (Pandas safely executes filters on the uploaded CSV DataFrame)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │    Answer Generator    │  (Mistral LLM synthesizes execution records into natural text)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │     Final Answer       │
       └────────────────────────┘
```

### 🧩 Node Breakdown:

1. **`Query Planner` (`src/query_planner.py`)**:
   - Inspects the user's natural language question, current date/time, and the CSV schema metadata (column names, types, sample values).
   - Calls **Mistral AI** (`ChatMistralAI`) to produce a structured JSON query plan containing `filters` and target `columns`.
   - Validates that only existing columns from the DataFrame are included in the query plan.

2. **`Query Executor` (`src/query_executor.py`)**:
   - Takes the structured JSON query plan and applies filtering logic directly against the loaded Pandas `DataFrame`.
   - Performs case-insensitive matching for string columns and exact matching for values.
   - Formats the resulting records and summary string for downstream consumption.

3. **`Answer Generator` (`src/answer_generator.py`)**:
   - Takes the original question and the filtered query result.
   - Prompts Mistral to formulate a concise, natural-language response for the user.
   - Handles empty/zero-match cases gracefully without treating them as system failures.

---

## 🛠️ Project Structure

```text
Student-CSV-AI-Assistant/
│
├── app.py                      # Streamlit UI & chat interface
├── data/
│   └── student_schedule_synthetic_1250.csv  # Sample student schedule dataset
│
├── src/
│   ├── __init__.py             # Package initializer
│   ├── state.py                # LangGraph AgentState TypedDict schema
│   ├── graph.py                # LangGraph StateGraph workflow & runner helper
│   ├── query_planner.py        # Planner node (generates JSON query plan)
│   ├── query_executor.py       # Safe Pandas query execution node
│   ├── answer_generator.py     # Answer synthesis node
│   ├── prompts.py              # System prompts for planner & answer generator
│   ├── data_loader.py          # CSV loader & cached schema extractor
│   ├── llm_client.py           # Dedicated Mistral AI client factory
│   └── logger.py               # Centralized logging module (logs to app.log)
│
├── logs/
│   └── app.log                 # Application log file
├── .env                        # Local environment variables (MISTRAL_API_KEY)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python package dependencies
└── README.md                   # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed.
- A **Mistral AI API Key** from [console.mistral.ai](https://console.mistral.ai).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 🧪 Verified Test Questions & Evaluations

The system has been tested against various natural language queries on the synthetic schedule dataset.

> 🔗 **Shared Test Chat & Verification Reference**:  
> [https://chatgpt.com/share/6a853ee7-7340-83ee-a8eb-4837c30fef57](https://chatgpt.com/share/6a853ee7-7340-83ee-a8eb-4837c30fef57)

### Sample Test Questions:

| # | Question | Expected Output / Context |
| :--- | :--- | :--- |
| 1 | *"Who teaches Machine Learning?"* | Identifies faculty (`Dr. Amit Shah`) mapped to `Machine Learning` subject. |
| 2 | *"Who teaches Deep Learning?"* | Returns `Dr. Priya Mehta`. |
| 3 | *"Who teaches Natural Language Processing?"* | Returns `Dr. Neha Patel`. |
| 4 | *"What lectures do I have on August 13, 2026?"* | Filters by `lecture_date` = `2026-08-13` and returns scheduled subjects, times, and classrooms. |
| 5 | *"How many lectures are scheduled on Monday?"* | Filters by `day_of_week` = `Monday` and provides record counts and schedule details. |
| 6 | *"Where is the Web Technology lab conducted?"* | Identifies classroom / lab location (`Lab-2` / `Technology Block`). |

---

## 🛡️ Key Features & Design Highlights

- **No Code Injection / Arbitrary Execution**: The LLM outputs strict JSON filters rather than executable Python code, ensuring maximum security and execution safety.
- **Dynamic Date & Time Resolution**: Uses the system date/time to resolve relative references (*today*, *tomorrow*, *yesterday*).
- **Stateful Conversation History**: Follow-up questions maintain conversational context through `st.session_state` and LangGraph message states.
- **Cached Schema Metadata**: Uses Streamlit's `@st.cache_data` for schema inspection, eliminating repeated DataFrame loops.
- **Dedicated Logging**: Tracks questions, query plans, execution outputs, and answers in `logs/app.log` without leaking sensitive API tokens.