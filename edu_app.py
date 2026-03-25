import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect("edu_data.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS study_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    O INTEGER,
    M INTEGER,
    P INTEGER
)
''')

conn.commit()

# =========================
# SEED DATA
# =========================
def seed_data():
    count = c.execute("SELECT COUNT(*) FROM study_plan").fetchone()[0]
    if count == 0:
        sample = [
            ("Python Basics", 1, 2, 4),
            ("Data Cleaning", 2, 4, 8),
            ("Machine Learning", 3, 6, 12)
        ]
        c.executemany("INSERT INTO study_plan (topic, O, M, P) VALUES (?, ?, ?, ?)", sample)
        conn.commit()

seed_data()

# =========================
# APP
# =========================
st.title("Student Success Probability Predictor")

n = st.number_input("Number of Topics", min_value=1, value=3)

data = []

for i in range(n):
    st.subheader(f"Topic {i+1}")
    name = st.text_input(f"Topic Name {i}", f"Topic {i+1}")
    O = st.number_input(f"O {i}", value=1)
    M = st.number_input(f"M {i}", value=2)
    P = st.number_input(f"P {i}", value=3)

    TE = (O + 4*M + P) / 6
    Var = ((P - O)/6)**2

    data.append([name, O, M, P, TE, Var])

df = pd.DataFrame(data, columns=["Topic", "O", "M", "P", "TE", "Var"])
st.write(df)

total_TE = df["TE"].sum()
total_var = df["Var"].sum()
sigma = np.sqrt(total_var)

st.subheader("Summary")
st.write(f"Total Expected Time: {round(total_TE,2)}")
st.write(f"Std Dev: {round(sigma,2)}")

target = st.number_input("Target Time")

if target > 0:
    Z = (target - total_TE) / sigma
    prob = 0.5 * (1 + np.math.erf(Z / np.sqrt(2)))

    st.write(f"Z-score: {round(Z,2)}")
    st.write(f"Probability: {round(prob*100,2)}%")

# Save
if st.button("Save Topics"):
    for row in data:
        c.execute("INSERT INTO study_plan (topic, O, M, P) VALUES (?, ?, ?, ?)",
                  (row[0], row[1], row[2], row[3]))
    conn.commit()
    st.success("Saved!")

# Show dataset
st.subheader("Saved Topics")
df_db = pd.read_sql_query("SELECT * FROM study_plan", conn)
st.write(df_db)

# Insight
hardest = df.loc[df["Var"].idxmax()]
st.subheader("Most Challenging Topic")
st.write(hardest["Topic"])