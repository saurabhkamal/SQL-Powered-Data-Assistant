import streamlit as st
from sqlalchemy import create_engine
from src.config import DATABASE_URI
from src.utils import get_db_schema, call_euri_llm, execute_sql

import speech_recognition as sr
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SQL Assistant", layout="wide")
st.title("💡 SQL-Powered Data Retrieval Assistant")

# ----------------------------
# Step 1: Choose Input Language
# ----------------------------
st.subheader("🌐 Choose Language for Speech Recognition")
language_map = {
    "English (US)": "en-US",
    "Hindi (India)": "hi-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Chinese (Mandarin)": "zh-CN",
    "Arabic": "ar-SA",
    "Bengali": "bn-IN",
    "Japanese": "ja-JP",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN"
}

selected_language = st.selectbox("Select a Language:", list(language_map.keys()))
language_code = language_map[selected_language]


# ----------------------------
# Step 2: Speech Input
# ----------------------------
st.subheader("🎙️ Speak Your SQL Query")
nl_query = ""
if st.button("🎤 Start Listening"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening in {selected_language}... Speak Now!")
        audio = recognizer.listen(source, timeout=6)

    try:
        nl_query = recognizer.recognize_google(audio, language=language_code)
        st.success(f"You said: {nl_query}")
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio. Please try again.")
    except sr.RequestError as e:
        st.error(f"Speech recognition API error: {e}")
else:
    nl_query = st.text_input("Or type your question about the database:")


# ----------------------------
# Step 3: Process Natural Language Query  # Proceed with SQL generation and execution
# ----------------------------
if nl_query:
    engine = create_engine(DATABASE_URI)
    schema = get_db_schema(engine)

    with open("src/prompt_template.txt") as f:
        template = f.read()
    prompt = template.format(schema=schema, question=nl_query)

    with st.spinner("🧠 Generating SQL using GLOBEFT LLM..."):
        sql_query = call_euri_llm(prompt)

    st.code(sql_query, language="sql")

    try:
        results, columns = execute_sql(engine, sql_query)
        if results:
            df = pd.DataFrame(results, columns=columns)
            st.subheader("📊 Query Results:")
            st.dataframe(df, use_container_width=True)

            # ----------------------------
            # Step 4: Auto Visualization
            # ----------------------------
            st.subheader("📈 Visualization")

            # Helper: try to parse first column as date
            first_col = df.columns[0]
            first_dtype = df[first_col].dtype

            # Time-series if first column is date/time and second is numeric
            if ("date" in first_col.lower() or "time" in first_col.lower()) and df.shape[1] >= 2:
                # If there are more than 2 columns, user might want to choose which numeric column — for now take second
                fig = px.area(df, x=first_col, y=df.columns[1], title="Time Series (Area Chart)")
                st.plotly_chart(fig, use_container_width=True)

            elif df.shape[1] == 2:
                col0, col1 = df.columns[0], df.columns[1]
                # categorical → values  => treat as categories
                if df[col0].dtype == "object" or df[col0].dtype.name == "category":
                    # If number of categories small → pie or bar
                    n_categories = df[col0].nunique()
                    if n_categories <= 10:
                        fig = px.pie(df, names=col0, values=col1,
                                    title=f"Pie Chart of {col1} by {col0}")
                    else:
                        fig = px.bar(df, x=col0, y=col1, title=f"Bar Chart of {col1} by {col0}")
                else:
                    # numeric x → bar chart
                    fig = px.bar(df, x=col0, y=col1, title="Bar Chart")
                st.plotly_chart(fig, use_container_width=True)

            elif df.shape[1] == 3:
                # scatter: maybe color-coded
                fig = px.scatter(df, x=df.columns[0], y=df.columns[1],
                                color=df.columns[2], title="Scatter Plot")
                st.plotly_chart(fig, use_container_width=True)

            elif df.shape[1] == 1:
                col = df.columns[0]
                # Show histogram + density (via violin) + boxplot
                fig_hist = px.histogram(df, x=col, title="Histogram")
                st.plotly_chart(fig_hist, use_container_width=True)

                fig_box = px.box(df, y=col, title="Box Plot")
                st.plotly_chart(fig_box, use_container_width=True)

                fig_violin = px.violin(df, y=col, box=True, points="all",
                                    title="Violin Plot (distribution + density)")
                st.plotly_chart(fig_violin, use_container_width=True)

            else:
                # More than 3 columns — attempt a correlation heatmap if numeric, or let user choose columns
                # First check if all columns numeric
                if all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns):
                    corr = df.corr()
                    fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 More than 3 columns and mixed types: please select relevant columns for visualization.")


    except Exception as e:
        st.error(f"❌ Error running query: {e}")
            
        