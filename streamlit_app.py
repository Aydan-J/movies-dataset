import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tempfile
from PIL import Image
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyA3x_E0nKnSq1BZjZnenwRL1t2vXSkR5no")

# Streamlit setup
st.set_page_config(page_title="CSVision - A Simple Graphing Tool", page_icon="📊")
st.title("CSVision: A Simple Graphing Tool")
st.subheader("Welcome to CSVision, a simple yet powerful graphing tool. This tool allows you to generate graphs, either from your own CSV data or from data in our database. Additionally, this tool allows you to generate an AI explanation using Google Gemini of the graph.")
st.write("Upload a CSV or use the built-in dataset. Select two columns to visualize and AI can explain the graph.")

# Selection
use_uploaded_file = st.radio("Choose a dataset:", ["Use built-in student performance data", "Upload your own CSV"])

if use_uploaded_file == "Upload your own CSV":
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ CSV loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading CSV: {e}")
            st.stop()
    else:
        st.info("Please upload a CSV file to continue.")
        st.stop()
else:
    df = pd.read_csv("data/StudentPerformanceFactors.csv")

# Select columns
numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

if len(numeric_columns) < 2:
    st.warning("Need at least two numeric columns.")
    st.stop()

x_col = st.selectbox("Select X-axis", numeric_columns)
y_options = [col for col in numeric_columns if col != x_col]
y_col = st.selectbox("Select Y-axis", y_options)

# Plot the chart
fig, ax = plt.subplots()
sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
ax.set_title(f"{y_col} vs {x_col}")
st.pyplot(fig)

# Save image for Gemini
temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
fig.savefig(temp_file.name, bbox_inches="tight")
image_path = temp_file.name

# AI Explanation Button
if st.button("🔍 Ask Gemini to explain this graph"):
    try:
        image = Image.open(image_path)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = [
            image,
            f"This is a chart showing {y_col} vs {x_col}. Please explain the trend, any correlations, and insights you can derive."
        ]
        response = model.generate_content(prompt)
        st.subheader("🤖 Gemini's Explanation")
        st.write(response.text)

        st.download_button(
            label="📥 Download AI Explanation",
            data=response.text,
            file_name="gemini_analysis.txt",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"⚠️ Gemini API error: {e}")
