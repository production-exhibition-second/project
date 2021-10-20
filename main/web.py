import streamlit as st
st.title("タイトル")
st.write("説明")

st.title("①ファイルから文字起こし")
st.write("説明")
file = st.file_uploader("", type="mp3")
if file:
    st.audio(file, format="audio/mp3")
    start_one = st.button("①開始")
    if start_one == True:
        contents_one = f"ファイルから文字起こしファイルから文字起こしファイルから文字起こし"
        download_one = st.download_button("①ダウンロード", contents_one)


st.title("②リアルタイムで文字起こし")
st.write("説明")
start_two = st.button("②開始")
if start_two:
    contents_two = f"リアルタイムで文字起こしリアルタイムで文字起こしリアルタイムで文字起こし"
    download_two = st.download_button("②ダウンロード", contents_two)
    st.write(f"結果表示\n\n{contents_two}")
