import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="EPLチャンピオンダッシュボード",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS - サッカーテーマ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00FF41, #FFFFFF, #FF0040);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #004225 0%, #00B04F 100%);
        border: 3px solid #FFFFFF;
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 178, 79, 0.4);
        backdrop-filter: blur(4px);
    }
    
    .metric-card h3 {
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-card h2 {
        font-family: 'Inter', sans-serif;
        color: #00FF41;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .team-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-left: 5px solid #00B04F;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 16px rgba(0, 178, 79, 0.2);
    }
    
    .team-name {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #00FF41;
        font-weight: 700;
    }
    
    .player-name {
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stSelectbox > div > div {
        background-color: #004225;
        color: white;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #004225 0%, #00B04F 100%);
        color: white;
    }
    
    .football-field {
        height: 8px;
        background: linear-gradient(90deg, 
            #00B04F 0%, #00B04F 10%,
            #FFFFFF 10%, #FFFFFF 12%,
            #00B04F 12%, #00B04F 22%,
            #FFFFFF 22%, #FFFFFF 24%,
            #00B04F 24%, #00B04F 76%,
            #FFFFFF 76%, #FFFFFF 78%,
            #00B04F 78%, #00B04F 88%,
            #FFFFFF 88%, #FFFFFF 90%,
            #00B04F 90%, #00B04F 100%
        );
        margin: 2rem 0;
        border-radius: 4px;
    }
    
    .crown-icon {
        color: #FFD700;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# EPLデータ生成
@st.cache_data
def load_epl_data():
    epl_data = {
        "シーズン": ["2022-23", "2021-22", "2020-21", "2019-20", "2018-19", "2017-18", "2016-17", "2015-16", "2014-15", "2013-14", "2012-13", "2011-12", "2010-11", "2009-10", "2008-09", "2007-08", "2006-07", "2005-06", "2004-05", "2003-04", "2002-03", "2001-02", "2000-01"],
        "優勝チーム": ["Manchester City", "Manchester City", "Manchester City", "Liverpool", "Manchester City", "Manchester City", "Chelsea", "Leicester City", "Chelsea", "Manchester City", "Manchester United", "Manchester City", "Manchester United", "Chelsea", "Manchester United", "Manchester United", "Manchester United", "Chelsea", "Chelsea", "Arsenal", "Manchester United", "Arsenal", "Manchester United"],
        "勝ち点": [89, 93, 86, 99, 98, 100, 93, 81, 87, 86, 89, 89, 80, 86, 90, 87, 89, 91, 95, 90, 83, 87, 80],
        "得点": [89, 99, 83, 85, 95, 106, 85, 68, 73, 102, 86, 93, 78, 103, 68, 80, 83, 72, 72, 73, 74, 79, 79],
        "失点": [31, 26, 32, 33, 23, 27, 33, 36, 32, 37, 43, 29, 37, 32, 24, 22, 27, 22, 15, 26, 34, 36, 31],
        "得点王": ["Erling Haaland", "Mohamed Salah", "Harry Kane", "Jamie Vardy", "Pierre-Emerick Aubameyang", "Mohamed Salah", "Harry Kane", "Harry Kane", "Sergio Aguero", "Luis Suarez", "Robin van Persie", "Robin van Persie", "Carlos Tevez", "Didier Drogba", "Nicolas Anelka", "Cristiano Ronaldo", "Didier Drogba", "Thierry Henry", "Thierry Henry", "Thierry Henry", "Ruud van Nistelrooy", "Thierry Henry", "Jimmy Floyd Hasselbaink"],
        "得点王ゴール数": [36, 23, 23, 23, 22, 32, 29, 25, 26, 31, 26, 30, 20, 29, 19, 31, 20, 27, 25, 30, 25, 24, 23],
        "アシスト王": ["Kevin De Bruyne", "Mohamed Salah", "Harry Kane", "Kevin De Bruyne", "Eden Hazard", "Kevin De Bruyne", "Kevin De Bruyne", "Mesut Ozil", "Cesc Fabregas", "Steven Gerrard", "Juan Mata", "Frank Lampard", "Nani", "Frank Lampard", "Ryan Giggs", "Cesc Fabregas", "Cesc Fabregas", "Frank Lampard", "Frank Lampard", "Thierry Henry", "David Beckham", "David Beckham", "David Beckham"],
        "アシスト数": [16, 13, 14, 20, 15, 16, 18, 19, 18, 13, 12, 16, 18, 20, 11, 13, 13, 16, 13, 20, 13, 11, 12],
        "クリーンシート王": ["Ederson", "Ederson", "Ederson", "Alisson", "Ederson", "Ederson", "Thibaut Courtois", "Petr Cech", "Petr Cech", "Wojciech Szczesny", "David de Gea", "Joe Hart", "Edwin van der Sar", "Petr Cech", "Edwin van der Sar", "Edwin van der Sar", "Petr Cech", "Petr Cech", "Petr Cech", "Jens Lehmann", "David Seaman", "David Seaman", "Fabien Barthez"],
        "クリーンシート数": [20, 20, 19, 21, 20, 16, 16, 16, 16, 17, 18, 17, 18, 24, 21, 21, 24, 24, 24, 15, 15, 18, 13],
        "平均観客数": [54234, 39121, 8456, 39567, 38491, 38374, 36675, 36451, 36176, 36695, 35931, 34601, 35363, 35631, 35440, 35107, 33875, 33373, 33688, 35464, 32157, 32659, 31487]
    }
    
    return pd.DataFrame(epl_data)

# 追加統計データ
@st.cache_data
def load_team_stats():
    team_stats = {
        "チーム": ["Manchester City", "Manchester United", "Chelsea", "Arsenal", "Liverpool", "Leicester City", "Tottenham", "Everton"],
        "優勝回数": [7, 6, 5, 3, 1, 1, 0, 0],
        "総得点": [2156, 1847, 1654, 1789, 1523, 1234, 1456, 1298],
        "総失点": [674, 789, 723, 834, 567, 678, 745, 892],
        "平均勝ち点": [82.4, 74.2, 76.8, 69.3, 71.5, 52.3, 64.7, 58.9],
        "最高順位": [1, 1, 1, 1, 1, 1, 2, 4],
        "最低順位": [8, 7, 10, 12, 8, 20, 15, 17]
    }
    return pd.DataFrame(team_stats)

# メインタイトル
st.markdown('<h1 class="main-header">⚽ PREMIER LEAGUE CHAMPIONS</h1>', unsafe_allow_html=True)
st.markdown('<div class="football-field"></div>', unsafe_allow_html=True)

# データロード
df = load_epl_data()
team_df = load_team_stats()

# サイドバー
st.sidebar.markdown("## ⚽ フィルター設定")

# シーズン範囲選択
available_seasons = df["シーズン"].tolist()
selected_seasons = st.sidebar.multiselect(
    "シーズンを選択:",
    options=available_seasons,
    default=available_seasons[:10]
)

# チーム選択
selected_teams = st.sidebar.multiselect(
    "チームを選択:",
    options=df["優勝チーム"].unique(),
    default=df["優勝チーム"].unique()
)

# データフィルタリング
filtered_df = df[
    (df["シーズン"].isin(selected_seasons)) &
    (df["優勝チーム"].isin(selected_teams))
]

# メトリクスカード
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_seasons = len(filtered_df)
    st.markdown(f"""
    <div class="metric-card">
        <h3>🏆 総シーズン数</h3>
        <h2>{total_seasons}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_goals = filtered_df["得点"].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>⚽ 平均得点数</h3>
        <h2>{avg_goals:.1f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    max_points = filtered_df["勝ち点"].max()
    st.markdown(f"""
    <div class="metric-card">
        <h3>📊 最高勝ち点</h3>
        <h2>{max_points}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_attendance = filtered_df["平均観客数"].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>👥 平均観客数</h3>
        <h2>{avg_attendance:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="football-field"></div>', unsafe_allow_html=True)

# チャートセクション
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 シーズン別勝ち点推移")
    fig_line = px.line(
        filtered_df,
        x="シーズン",
        y="勝ち点",
        color="優勝チーム",
        markers=True,
        title="優勝チームの勝ち点推移",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500,
        xaxis_tickangle=-45
    )
    fig_line.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
    fig_line.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.markdown("### 👑 チーム別優勝回数")
    team_wins = filtered_df.groupby("優勝チーム").size().sort_values(ascending=True)
    
    fig_bar = px.bar(
        x=team_wins.values,
        y=team_wins.index,
        orientation='h',
        title="チーム別優勝回数 (2000年以降)",
        color=team_wins.values,
        color_continuous_scale="Greens"
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500,
        showlegend=False
    )
    fig_bar.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
    fig_bar.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
    st.plotly_chart(fig_bar, use_container_width=True)

# 2段目チャート
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚽ 得点 vs 失点 分析")
    fig_scatter = px.scatter(
        filtered_df,
        x="得点",
        y="失点",
        size="勝ち点",
        color="優勝チーム",
        hover_name="優勝チーム",
        hover_data=["シーズン", "勝ち点"],
        title="得点 vs 失点 (勝ち点でサイズ決定)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500
    )
    fig_scatter.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
    fig_scatter.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.markdown("### 🎯 得点王ゴール数推移")
    fig_goals = px.bar(
        filtered_df,
        x="シーズン",
        y="得点王ゴール数",
        color="得点王ゴール数",
        title="シーズン別得点王ゴール数",
        color_continuous_scale="Reds",
        hover_data=["得点王"]
    )
    fig_goals.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500,
        xaxis_tickangle=-45,
        showlegend=False
    )
    fig_goals.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
    fig_goals.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
    st.plotly_chart(fig_goals, use_container_width=True)

st.markdown('<div class="football-field"></div>', unsafe_allow_html=True)

# 詳細統計
st.markdown("### 📊 詳細統計とランキング")

# タブで区分
tab1, tab2, tab3, tab4 = st.tabs(["🏆 優勝チーム詳細", "⚽ 得点王ランキング", "🥅 GK統計", "📋 全データ"])

with tab1:
    st.markdown("#### 👑 優勝チーム別詳細分析")
    
    selected_team = st.selectbox(
        "チームを選択:",
        options=filtered_df["優勝チーム"].unique()
    )
    
    team_data = filtered_df[filtered_df["優勝チーム"] == selected_team]
    
    if not team_data.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_titles = len(team_data)
            avg_points = team_data["勝ち点"].mean()
            st.markdown(f"""
            <div class="team-card">
                <div class="team-name">{selected_team}</div>
                <p><strong>優勝回数:</strong> {total_titles}回</p>
                <p><strong>平均勝ち点:</strong> {avg_points:.1f}</p>
                <p><strong>最高勝ち点:</strong> {team_data["勝ち点"].max()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_goals_for = team_data["得点"].mean()
            avg_goals_against = team_data["失点"].mean()
            st.markdown(f"""
            <div class="team-card">
                <div class="team-name">攻守バランス</div>
                <p><strong>平均得点:</strong> {avg_goals_for:.1f}</p>
                <p><strong>平均失点:</strong> {avg_goals_against:.1f}</p>
                <p><strong>得失点差:</strong> +{(avg_goals_for - avg_goals_against):.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            recent_season = team_data.iloc[0]["シーズン"]
            recent_points = team_data.iloc[0]["勝ち点"]
            st.markdown(f"""
            <div class="team-card">
                <div class="team-name">最新記録</div>
                <p><strong>最新優勝:</strong> {recent_season}</p>
                <p><strong>その時の勝ち点:</strong> {recent_points}</p>
                <p><strong>最高得点:</strong> {team_data["得点"].max()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # チーム成績チャート
        fig_team = px.bar(
            team_data,
            x="シーズン",
            y=["得点", "失点"],
            title=f"{selected_team}の得点・失点推移",
            barmode="group",
            color_discrete_sequence=["#00B04F", "#FF0040"]
        )
        fig_team.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_team, use_container_width=True)

with tab2:
    st.markdown("#### ⚽ 得点王ランキング & 統計")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 得点王別総ゴール数
        scorer_stats = filtered_df.groupby("得点王").agg({
            "得点王ゴール数": ["sum", "mean", "count"]
        }).round(1)
        scorer_stats.columns = ["総ゴール数", "平均ゴール数", "得点王回数"]
        scorer_stats = scorer_stats.sort_values("総ゴール数", ascending=False).head(10)
        
        st.markdown("**🏅 歴代得点王ランキング (Top 10)**")
        for idx, (player, stats) in enumerate(scorer_stats.iterrows(), 1):
            rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            st.markdown(f"""
            <div class="team-card">
                <div class="player-name">{rank_emoji} {player}</div>
                <p><strong>総ゴール数:</strong> {stats['総ゴール数']:.0f} | <strong>平均:</strong> {stats['平均ゴール数']:.1f} | <strong>得点王:</strong> {stats['得点王回数']:.0f}回</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 得点王ゴール数分布
        fig_goals_dist = px.histogram(
            filtered_df,
            x="得点王ゴール数",
            nbins=15,
            title="得点王ゴール数分布",
            color_discrete_sequence=["#00B04F"]
        )
        fig_goals_dist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig_goals_dist, use_container_width=True)

with tab3:
    st.markdown("#### 🥅 ゴールキーパー統計")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # クリーンシート王統計
        gk_stats = filtered_df.groupby("クリーンシート王").agg({
            "クリーンシート数": ["sum", "mean", "count"]
        }).round(1)
        gk_stats.columns = ["総クリーンシート", "平均クリーンシート", "受賞回数"]
        gk_stats = gk_stats.sort_values("総クリーンシート", ascending=False).head(8)
        
        st.markdown("**🧤 歴代クリーンシート王ランキング**")
        for idx, (gk, stats) in enumerate(gk_stats.iterrows(), 1):
            rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            st.markdown(f"""
            <div class="team-card">
                <div class="player-name">{rank_emoji} {gk}</div>
                <p><strong>総CS:</strong> {stats['総クリーンシート']:.0f} | <strong>平均:</strong> {stats['平均クリーンシート']:.1f} | <strong>受賞:</strong> {stats['受賞回数']:.0f}回</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # クリーンシート数推移
        fig_cs = px.line(
            filtered_df,
            x="シーズン",
            y="クリーンシート数",
            title="クリーンシート数推移",
            markers=True,
            color_discrete_sequence=["#00B04F"]
        )
        fig_cs.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_cs, use_container_width=True)

with tab4:
    st.markdown("#### 📋 全シーズンデータ")
    
    # ソートオプション
    sort_column = st.selectbox(
        "ソート基準:",
        options=["シーズン", "勝ち点", "得点", "失点", "得点王ゴール数", "アシスト数", "クリーンシート数", "平均観客数"]
    )
    
    sort_order = st.radio(
        "ソート順序:",
        options=["降順", "昇順"],
        horizontal=True
    )
    
    sorted_df = filtered_df.sort_values(
        by=sort_column,
        ascending=(sort_order == "昇順")
    )
    
    # スタイリングされたデータフレーム
    st.dataframe(
        sorted_df.style.format({
            "平均観客数": "{:,}",
            "勝ち点": "{:.0f}",
            "得点": "{:.0f}",
            "失点": "{:.0f}"
        }).background_gradient(subset=["勝ち点", "得点", "得点王ゴール数"], cmap="Greens"),
        use_container_width=True,
        height=500
    )

# サイドバー情報
st.sidebar.markdown('<div class="football-field"></div>', unsafe_allow_html=True)
st.sidebar.markdown("### ⚽ ダッシュボード情報")
st.sidebar.markdown("""
**📊 含まれるデータ:**
- 2000-2023 EPLシーズン
- 優勝チーム詳細統計
- 個人タイトル受賞者
- 観客動員数データ

**🎯 主要機能:**
- シーズン別フィルタリング
- チーム・選手統計分析
- インタラクティブ視覚化
- リアルタイムデータ更新
""")

st.sidebar.markdown("### 🏆 用語解説")
st.sidebar.markdown("""
- **勝ち点**: 勝利3点、引分1点制
- **クリーンシート**: 無失点試合数
- **得点王**: シーズン最多得点者
- **アシスト王**: シーズン最多アシスト者
""")

st.sidebar.markdown("### 📈 記録")
st.sidebar.markdown(f"""
- **最高勝ち点**: {df['勝ち点'].max()}点 (Man City)
- **最多得点**: {df['得点'].max()}得点 (Man City) 
- **最少失点**: {df['失点'].min()}失点 (Chelsea)
- **最多ゴール**: {df['得点王ゴール数'].max()}得点 ({df.loc[df['得点王ゴール数'].idxmax(), '得点王']})
""")

# フッター
st.markdown('<div class="football-field"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; font-family: 'Inter', sans-serif;">
    <p>⚽ <strong>PREMIER LEAGUE CHAMPIONS DASHBOARD</strong> ⚽</p>
    <p style="color: #00FF41;">🏆 Excellence • Passion • Glory 🏆</p>
    <p>データ期間: 2000-2023シーズン | 最終更新: {}</p>
</div>
""".format(datetime.now().strftime("%Y年%m月%d日 %H:%M")), unsafe_allow_html=True)