import pandas as pd
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

def load_data(file_path="student_data.csv"):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error("Error: student_data.csv not found.")
        return None

def apply_rbac(df, role):
    filtered_df = df.copy()
    for key, value in role.items():
        if key in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[key] == value]
        else:
            st.warning(f"Column {key} not found in dataset.")
    return filtered_df

def process_query(query, df, llm):
    prompt = PromptTemplate(
        input_variables=["query", "columns"],
        template="Given the query '{query}' and dataset columns {columns}, suggest a Python Pandas query to fetch the relevant data. Return only the Pandas query as a string, e.g., 'df[df[\"column\"] == value]'."
    )
    columns = df.columns.tolist()
    prompt_text = prompt.format(query=query, columns=columns)
    try:
        pandas_query = llm(prompt_text).strip()
        if pandas_query.startswith("df["):
            result = eval(pandas_query, {"df": df})
            return result
        else:
            # Fallback: Keyword-based query processing
            if "haven't submitted" in query.lower():
                return df[df["submission_status"].isin(["Pending","Missing"])]
            elif "grade A" in query.lower() and "last week" in query.lower():
                return df[(df["grade"].isin(["A"])) & (df["quiz_date"] >= "2025-07-21") & (df["quiz_date"] <= "2025-07-27")]
            elif "upcoming quizzes" in query.lower():
                return df[df["quiz_date"] > "2025-07-28"]
            else:
                return "Query not recognized. Please try another."
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return "Error processing query."

def run_streamlit():
    st.title("Dumroo Admin Panel Query System")

    df = load_data()
    if df is None:
        return

    # Dynamic RBAC: Let admin select their scope
    st.sidebar.header("Set Your Admin Scope")
    grade_options = sorted(df["grade"].dropna().unique())
    class_options = sorted(df["class"].dropna().unique())
    # If you have region, add: region_options = sorted(df["region"].dropna().unique())

    grade = st.sidebar.selectbox("Grade", options=["All"] + list(grade_options))
    class_num = st.sidebar.selectbox("Class", options=["All"] + list(class_options))
    # region = st.sidebar.selectbox("Region", options=["All"] + list(region_options))

    admin_role = {}
    if grade != "All":
        admin_role["grade"] = grade
    if class_num != "All":
        admin_role["class"] = class_num
    # if region != "All":
    #     admin_role["region"] = region

    restricted_df = apply_rbac(df, admin_role)
    if restricted_df.empty:
        st.warning("No data available for your role/scope.")
        return

    st.subheader("Your Student Data")
    st.dataframe(restricted_df)

    llm = HuggingFacePipeline.from_model_id(
        model_id="gpt2",
        task="text-generation",
        pipeline_kwargs={"max_length": 512, "truncation": True}
    )

    query = st.text_input("Enter your query (e.g., 'Which students haven't submitted their homework yet?')")
    if query:
        result = process_query(query, restricted_df, llm)
        st.subheader("Query Result")
        if isinstance(result, pd.DataFrame):
            st.dataframe(result)
        else:
            st.write(result)
    
    

if __name__ == "__main__":
    run_streamlit()