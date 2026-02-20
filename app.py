import streamlit as st
import pandas as pd
from io import StringIO
import datetime

# --- 初期設定 ---
if 'df' not in st.session_state:
    raw_data = """ウーリー安城マジックショー＆見学会,2025/12/29,10:00,15:00,ウーリー安城
ウーリー安城作業体験会,2026/01/10,13:00,15:00,ウーリー安城
ららぽーと安城販売会,2026/01/31,10:00,16:00,三井ショッピングモールららぽーと安城
桜井公民館まつり販売会,2026/02/14,10:00,15:00,桜井公民館
あんぷくフェスティバル販売会,2026/03/07,10:00,16:00,アンフォーレ"""
    st.session_state.df = pd.read_csv(StringIO(raw_data), names=['イベント名', '日付', '開始', '終了', '場所'])

# 削除対象のインデックスを保持する変数を初期化
if 'delete_idx' not in st.session_state:
    st.session_state.delete_idx = None

# --- 削除実行用ダイアログ ---
@st.dialog("イベントを削除しますか？")
def confirm_delete_dialog():
    idx = st.session_state.delete_idx
    event_name = st.session_state.df.iloc[idx]['イベント名']
    
    st.write(f"「**{event_name}**」をリストから削除します。よろしいですか？")
    
    col1, col2 = st.columns(2)
    if col1.button("はい、削除します", type="primary", use_container_width=True):
        # データの削除
        st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
        st.session_state.delete_idx = None # リセット
        st.rerun()
    
    if col2.button("キャンセル", use_container_width=True):
        st.session_state.delete_idx = None
        st.rerun()

# --- メイン画面 ---
st.title("📅 イベント登録・管理")

# --- 新規追加フォーム ---
with st.form("event_form", clear_on_submit=True):
    st.subheader("新しいイベントを追加")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("イベント名")
        date = st.date_input("日付", value=datetime.date(2026, 2, 18))
        location = st.text_input("場所")
    with col2:
        start_time = st.time_input("開始時間", value=datetime.time(10, 0))
        end_time = st.time_input("終了時間", value=datetime.time(15, 0))
    
    if st.form_submit_button("リストに追加"):
        if name:
            new_data = {
                'イベント名': name,
                '日付': date.strftime('%Y/%m/%d'),
                '開始': start_time.strftime('%H:%M'),
                '終了': end_time.strftime('%H:%M'),
                '場所': location
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
            st.rerun()
        else:
            st.error("イベント名を入力してください")

# --- イベント一覧表示（削除ボタン付き） ---
st.subheader("現在のイベントリスト")

# ヘッダー
h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
h1.caption("イベント名")
h2.caption("日付 / 場所")
h3.caption("時間")
h4.caption("削除")

# 各行の表示
for index, row in st.session_state.df.iterrows():
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    
    c1.write(f"**{row['イベント名']}**")
    c2.write(f"{row['日付']}\n\n{row['場所']}")
    c3.write(f"{row['開始']} ~ {row['終了']}")
    
    # ゴミ箱ボタン
    if c4.button("🗑️", key=f"del_btn_{index}"):
        st.session_state.delete_idx = index
        confirm_delete_dialog()

# --- ソースコード出力エリア ---
st.divider()
updated_csv_text = st.session_state.df.to_csv(index=False, header=False, lineterminator='\n').strip()
st.subheader("📋 Webソースコード用（コピー用）")
st.code(f"const rawData = `\n{updated_csv_text}\n`;", language='javascript')

import os
from ftplib import FTP

def upload_to_server():
    # CSVを一旦ファイルとして保存
    st.session_state.df.to_csv(
        "events.csv",
        index=False,
        header=False,
        encoding="utf-8-sig"
    )

    try:
        ftp = FTP("sv11005.star.ne.jp")
        # Secretsからパスワードを取得
        pw = st.secrets["mouse_P-5"] 
        ftp.login("brescia0218@yahoo.co.jp", pw)
        ftp.cwd("/public_html/")

        with open("events.csv", "rb") as f:
            ftp.storbinary("STOR events.csv", f)

        ftp.quit()
        st.success("サーバーへ自動アップロード完了！")
    except Exception as e:
        st.error(f"FTPアップロード失敗: {e}")

# 最後にこの関数を実行する
upload_to_server()
