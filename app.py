import io
import pandas as pd
import requests
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="CSV 資料查看器", layout="wide")
st.title("CSV 資料查看器")

DEFAULT_URL = "https://mopsfin.twse.com.tw/opendata/t187ap46_L_1.csv"  # 換連結


@st.cache_data(ttl=3600, show_spinner="下載資料中...")
def load_data(url: str) -> pd.DataFrame:
    response = requests.get(url, verify=False, timeout=30)
    response.raise_for_status()
    return pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")


with st.sidebar:
    st.header("設定")
    url = st.text_input("CSV 連結", value=DEFAULT_URL)
    drop_na = st.checkbox("移除含有空值的列 (dropna)", value=True)
    if st.button("重新下載"):
        load_data.clear()

try:
    df = load_data(url)
except Exception as e:
    st.error(f"下載或讀取失敗：{e}")
    st.stop()

if drop_na:
    df = df.dropna()

keyword = st.text_input("關鍵字搜尋（所有欄位）")
if keyword:
    mask = df.astype(str).apply(
        lambda col: col.str.contains(keyword, case=False, na=False)
    ).any(axis=1)
    df = df[mask]

st.caption(f"共 {len(df)} 筆、{df.shape[1]} 個欄位")
st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "下載 CSV",
    data=df.to_csv(index=False).encode("utf-8-sig"),
    file_name="data01.csv",
    mime="text/csv",
)
