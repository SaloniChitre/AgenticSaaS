# AgenticSaaS: Privacy-First Autonomous Business Intelligence 🚀
🚀 A Privacy-First AI Business Analyst using Llama 3 &amp; LangChain. Transforms natural language into SQL queries and autonomous Python/Plotly visualizations. Local-first architecture via Ollama &amp; PostgreSQL. 📊🧠

**AgenticSaaS** is an intelligent hub that transforms natural language questions into complex data insights. Built with **Llama 3** and **LangChain**, it features a **ReAct (Reason + Act)** agent that autonomously decides whether to query a PostgreSQL database or execute Python code to generate real-time visualizations.

---

## 🛡️ Why This Project?

Most AI dashboards send sensitive data to the cloud. **AgenticSaaS** is built with a **Privacy-First** philosophy:
* **100% Local Execution:** Powered by Llama 3 via **Ollama**. No data ever leaves your machine.
* **Secure Data Access:** Connects directly to a local **PostgreSQL** instance. Your financial records are never exposed to external APIs.
* **On-Premise Reasoning:** All trend analysis and data joins happen behind your firewall, meeting strict data residency requirements.

---

## ✨ Key Features

* **🧠 Multi-Tool Reasoning:** The agent identifies when it needs SQL for data extraction and when it needs Python for high-level computation.
* **📊 Autonomous Plotting:** On-the-fly generation of **Plotly and Streamlit charts**. The agent writes the code, fixes its own errors, and renders the result.
* **📈 Market Intelligence:** Built-in logic to join internal subscription revenue with external market indicators (e.g., Salesforce/CRM stock performance).
* **⚙️ Self-Correction:** Uses a ReAct loop to handle real-world complexities like SQL `Decimal` type serialization and data type mismatches.

---

## 🏗️ Technical Stack

| Category | Technology |
| :--- | :--- |
| **LLM** | Llama 3 (via Ollama) |
| **Orchestration** | LangChain (AgentExecutor, ReAct Logic) |
| **Database** | PostgreSQL |
| **Frontend** | Streamlit |
| **Data/Viz** | Pandas, Plotly, NumPy |

---

## 🧠 The Agentic Logic Flow

1.  **Question:** *"Show me monthly revenue trends for 2025 as a bar chart."*
2.  **Thought:** I need to pull monthly totals from the `subscriptions` table.
3.  **Action (SQL):** Generates and executes a SQL query. 
4.  **Observation:** Receives raw data. 
5.  **Thought:** I have the data; now I need to visualize it as requested.
6.  **Action (Python):** Writes a script to create a Plotly bar chart.
7.  **Final Result:** Displays an interactive chart directly in the UI.

---

## 🚀 Getting Started

### Prerequisites
* [Ollama](https://ollama.com/) installed and running (`ollama pull llama3`)
* [PostgreSQL](https://www.postgresql.org/) installed and running

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)[your-username]/AgenticSaaS.git
   cd AgenticSaaS
