import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Supabaseの接続設定（Secretsから読み込み）
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("💰 簡易家計簿アプリ")

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

# --- 履歴と分析 ---
st.subheader("📊 経費の分析")

# データの取得
response = supabase.table("expense_logs").select("*").order("date", desc=True).execute()
data = response.data

if data:
    df = pd.DataFrame(data)
    # 日付列を日付型に変換
    df['date'] = pd.to_datetime(df['date'])
    # 「年月」の列を作成（例: 2023-10）
    df['年月'] = df['date'].dt.strftime('%Y-%m')

    # --- 月別集計 ---
    monthly_summary = df.groupby('年月')['amount'].sum().reset_index()
    
    # グラフと表を横並びで表示
    col_chart, col_table = st.columns([2, 1])
    
    with col_chart:
        st.write("月別支出推移")
        st.bar_chart(data=monthly_summary, x='年月', y='amount')
        
    with col_table:
        st.write("月別合計金額")
        # 金額を読みやすくフォーマット
        monthly_summary['amount'] = monthly_summary['amount'].map('{:,}円'.format)
        st.dataframe(monthly_summary, hide_index=True)

    st.divider()

    # --- 全データ詳細 ---
    st.subheader("📝 詳細履歴")
    # 表示用に日付を文字列に戻す
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(df[["date", "category", "item_name", "amount"]], use_container_width=True)

else:
    st.info("データがまだありません。")
