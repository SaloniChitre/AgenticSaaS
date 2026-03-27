import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
# --- NEW UPDATES START ---
from langchain_experimental.utilities import PythonREPL
try:
    from langchain.tools import Tool
except ImportError:
    try:
        from langchain_core.tools import Tool
    except ImportError:
        from langchain.agents import Tool

# --- NEW UPDATES END ---

# 1. Database & AI Setup
engine = create_engine('postgresql://deepam@localhost:5432/saas_analytics')
db = SQLDatabase.from_uri("postgresql://deepam@localhost:5432/saas_analytics")

llm = ChatOllama(model="llama3", temperature=0)

# --- NEW UPDATES START ---
# Initialize the Python Tool with a "Decimal-Safe" wrapper
python_repl = PythonREPL()

def safe_python_run(code: str):
    # This pre-code handles the 2026 syntax and Decimal conversion automatically
    # so the AI doesn't have to remember to do it every time.
    setup_code = """
import pandas as pd
import streamlit as st
from decimal import Decimal
def clean_data(obj):
    if isinstance(obj, list): return [clean_data(i) for i in obj]
    if isinstance(obj, tuple): return tuple(clean_data(i) for i in obj)
    if isinstance(obj, Decimal): return float(obj)
    return obj
"""
    return python_repl.run(setup_code + code)

repl_tool = Tool(
    name="python_repl_tool", # Matches the prefix name now
    description="A Python shell. Use this to execute python commands to create plots/graphs with Streamlit. Input should be valid python code.",
    func=safe_python_run,
)
# --- NEW UPDATES END ---

# Initialize the Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 2. The "Business Owner Override" Prompt
custom_prefix = """
You are a PostgreSQL Expert for AgenticSaaS.
You MUST always start your response with 'Thought: I need to check the tables...' 

TABLES AVAILABLE:
- subscriptions: contains sales data (amount, payment_date, status)
- market_intelligence: contains stock data (ticker, price, last_trading_day)

CRITICAL RULES:
1. Never provide an 'Action' and a 'Final Answer' in the same response.
2. If you are using 'python_repl_tool' to create a graph, your response must END after the Action Input.
3. When fetching data from SQL, always CAST numeric values to FLOAT in your query (e.g., SELECT amount::FLOAT).

STREAMLIT 2026 SYNTAX:
- ALWAYS use width='stretch' instead of use_container_width=True in all plotting functions.
CRITICAL RULES:
1. When using 'python_repl_tool', you MUST explicitly write the data into the code. 
   Example: data = [(100, 1), (200, 2)]; df = pd.DataFrame(data, columns=['Amount', 'Month'])
2. NEVER use placeholders like 'your_data' or 'data_from_sql'. 
3. After the Action Input, STOP. Do not provide a Final Answer until you see the Observation.

STRICT FORMAT:
Thought: I have the data, now I will write the Python code including the raw data.
Action: python_repl_tool
Action Input: import pandas as pd; import streamlit as st; data = <PASTE_DATA_HERE>; df = pd.DataFrame(data); st.line_chart(df, width='stretch')

STRICT FORMAT:
Thought: [Your reasoning]
Action: [tool_name]
Action Input: [Input for the tool]
Observation: [Result]
... (Repeat until you have the final answer)
Final Answer: [Direct answer to the user]

GRAPHING RULE:
If the user asks for a 'graph', 'chart', or 'plot', first use SQL to get the data, 
then use the 'python_repl_tool' to create the visualization.
"""

# 2. Ensure your Agent Initialization is "Standardized"
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="zero-shot-react-description",
    handle_parsing_errors=True,
    prefix=custom_prefix,
    # --- NEW UPDATES START ---
    extra_tools=[repl_tool], 
    # --- NEW UPDATES END ---
    max_iterations=15, 
    max_execution_time=60 
)

# 3. Page Configuration
st.set_page_config(page_title="SaaS Intelligence Hub", layout="wide")
st.title("🚀 SaaS Executive Intelligence Hub")

# --- SIDEBAR ---
st.sidebar.header("System Status")
st.sidebar.success("Local LLM: Llama 3 (ReAct Mode)")
st.sidebar.info("Connected to: PostgreSQL")
st.sidebar.write(f"User: **Deepam**")

# --- SECTION 1: AI BUSINESS ANALYST ---
st.header("🤖 AI Business Analyst")
st.markdown("*Ask questions like: 'What is the total revenue?' or 'Which plan has more users?'*")

user_question = st.text_input("Enter your business question:")

if user_question:
    with st.spinner("Llama 3 is thinking and querying..."):
        try:
            # Use .run() for the ReAct Agent type
            response = agent_executor.run(user_question)
            
            st.write("### 💡 AI Analysis:")
            st.success(response)
            
        except Exception as e:
            st.error(f"I ran into an issue. Error: {e}")

st.markdown("---")

# --- SECTION 2: CORE METRICS (PANDAS) ---
col1, col2, col3 = st.columns(3)

with col1:
    df_mrr = pd.read_sql("SELECT SUM(amount) as mrr FROM subscriptions WHERE payment_date > CURRENT_DATE - INTERVAL '30 days'", engine)
    mrr_val = df_mrr['mrr'][0] if df_mrr['mrr'][0] else 0
    st.metric("Current MRR", f"${mrr_val:,.2f}")

with col2:
    df_users = pd.read_sql("SELECT COUNT(DISTINCT user_id) as users FROM users", engine)
    st.metric("Total Customers", df_users['users'][0])

with col3:
    st.metric("Retention Goal", "85%", "+2.4%")

# --- SECTION 3: VISUALIZATIONS ---
tab1, tab2 = st.tabs(["📈 Growth & Revenue", "📊 Retention Matrix"])

with tab1:
    st.subheader("Monthly Revenue Trend")
    query_rev = "SELECT DATE_TRUNC('month', payment_date)::date as month, SUM(amount) as revenue FROM subscriptions GROUP BY 1 ORDER BY 1"
    df_rev = pd.read_sql(query_rev, engine)
    fig_rev = px.area(df_rev, x='month', y='revenue', title="Revenue over Time")
    # Updated to 2026 Syntax
    st.plotly_chart(fig_rev, width='stretch')

with tab2:
    st.subheader("Customer Retention (Cohort View)")
    try:
        df_cohort = pd.read_sql("SELECT * FROM v_customer_retention_matrix", engine)
        # Updated to 2026 Syntax
        st.dataframe(df_cohort, width='stretch')
    except:
        st.warning("View 'v_customer_retention_matrix' not found. Run the CREATE VIEW script in DBeaver.")

# --- SECTION 4: AT-RISK USERS ---
st.markdown("---")
st.subheader("⚠️ At-Risk Customers (Zombie Alert)")
query_zombies = """
    SELECT user_id, MAX(payment_date)::date as last_payment, CURRENT_DATE - MAX(payment_date)::date as days_inactive
    FROM subscriptions GROUP BY 1
    HAVING MAX(payment_date) < CURRENT_DATE - INTERVAL '45 days'
    ORDER BY days_inactive DESC LIMIT 5
"""
df_zombies = pd.read_sql(query_zombies, engine)
st.table(df_zombies)