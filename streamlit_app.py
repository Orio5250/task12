import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Supabaseの接続設定（Secretsから読み込み）
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("💰 簡易経費メモアプリ")

# --- 入力フォーム ---
with st.form("expense_form", clear_on_submit=True):
    st.subheader("新しい経費を入力")
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("日付")
        category = st.selectbox("カテゴリー", ["食費", "交通費", "備品代", "交際費", "その他"])
    with col2:
        item_name = st.text_input("項目名（例：タクシー代）")
        amount = st.number_input("金額（円）", min_value=0, step=100)
    
    submit_button = st.form_submit_button("保存する")

    if submit_button:
        if item_name and amount > 0:
            # データの挿入
            data = {
                "date": str(date),
                "category": category,
                "item_name": item_name,
                "amount": amount
            }
            response = supabase.table("expense_logs").insert(data).execute()
            st.success(f"保存しました: {item_name}")
        else:
            st.error("項目名と金額を入力してください。")

# --- 履歴の表示 ---
st.subheader("📊 経費の履歴")

# データの取得
response = supabase.table("expense_logs").select("*").order("date", desc=True).execute()
data = response.data

if data:
    df = pd.DataFrame(data)
    
    # 合計金額の表示
    total_amount = df["amount"].sum()
    st.metric("合計金額", f"{total_amount:,} 円")
    
    # テーブル表示（不要なIDなどは除外）
    display_df = df[["date", "category", "item_name", "amount"]]
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("データがまだありません。")
