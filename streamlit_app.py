import streamlit as st
from supabase import create_client

# StreamlitのSecretsから設定を読み込む（GitHubには書かない情報）
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Todoアプリ")

# 1. データの追加
new_todo = st.text_input("タスクを入力")
if st.button("追加"):
    supabase.table("todos").insert({"task": new_todo}).execute()
    st.rerun()

# 2. データの表示
rows = supabase.table("todos").select("*").execute()
for row in rows.data:
    st.write(f"・ {row['task']}")
