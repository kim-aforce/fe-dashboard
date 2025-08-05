import streamlit as st
import pandas as pd
import snowflake.connector

@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        client_session_keep_alive=True
    )
# クエリ実行関数
@st.cache_data(ttl=600)
def run_query(query):
    try:
        conn = init_connection()
        # 連携テスト
        conn.cursor().execute("SELECT 1")
        return pd.read_sql(query, conn)
    except:
        # 連携失敗の場合キャッシュクリア後はre-try
        st.cache_resource.clear()
        conn = init_connection()
        return pd.read_sql(query, conn)
    finally:
        if 'conn' in locals():
            conn.close()
    
st.title("基本情報技術者 学習ダッシュボード")

# サイドバーのメニュー
menu = st.sidebar.radio("表示するページを選択", [
    "1. 試験回ごとの正解率",
    "2. 月別 学習サマリー",
    "3. 問題別 学習履歴",
    "4. 試験回の概要"
])

try:
    # 試験回ごとの正解率
    if menu == "1. 試験回ごとの正解率":
        df = run_query("SELECT * FROM EXAM_TERM_ATTEMPT_STATS")
        if not df.empty:
            exam_terms = df["EXAM_TERM"].unique()
            selected = st.selectbox("試験回を選んでください", exam_terms)
            filtered = df[df["EXAM_TERM"] == selected]
            st.line_chart(filtered.set_index("ATTEMPT_NO")["ACCURACY"])
            st.metric("平均正解率", f"{filtered['AVERAGE_ACCURACY'].iloc[0]}%")
            st.dataframe(filtered)
        else:
            st.warning("データを見つかりませんでした。")

    # 月別 学習サマリー
    elif menu == "2. 月別 学習サマリー":
        df = run_query("SELECT * FROM MONTHLY_OVERVIEW")
        if not df.empty:
            selected = st.selectbox("月を選んでください", df["STUDY_MONTH"].unique())
            row = df[df["STUDY_MONTH"] == selected].iloc[0]
            st.metric("正解率", f"{row['ACCURACY']}%")
            st.metric("問題数", int(row['TOTAL']))
            st.line_chart(df.set_index("STUDY_MONTH")["ACCURACY"])
        else:
            st.warning("データを見つかりませんでした。")

    # 問題別 学習履歴
    elif menu == "3. 問題別 学習履歴":
        df = run_query("SELECT * FROM QUESTION_DETAIL_WITH_ATTEMPT")
        if not df.empty:
            selected = st.selectbox("試験回を選択", df["EXAM_TERM"].dropna().unique())
            st.dataframe(df[df["EXAM_TERM"] == selected])
        else:
            st.warning("データを見つかりませんでした。")

    # 試験回の概要
    elif menu == "4. 試験回の概要":
        df = run_query("SELECT * FROM EXAM_TERM_ATTEMPT_SUMMARY")
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("データを見つかりませんでした。")
            
except Exception as e:
    st.error(f"エラーが発生しました。: {str(e)}")
    st.info("Snowflake連係情報をテーブルを確認してください。")