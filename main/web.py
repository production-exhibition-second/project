# 音声を扱う
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import io
import glob
import os
import shutil

import streamlit as st

def conversion_mp3_mp4(sound_data, file_name):
    """ 
    sound_data : アップロードされた音声ファイル
    file_name : アップロードされた音声ファイル名
    """
    # print(os.path.splitext(file_name))
    if "mp3" in file_name:
        # print("mp3")
        sound = AudioSegment.from_file(sound_data, "mp3")
        print(sound)
        return sound, io.BufferedRandom(sound.export(format="wav"))
    elif "mp4" in file_name:
        # print("mp4")
        sound = AudioSegment.from_file(sound_data, "mp4")
        return sound, io.BufferedRandom(sound.export(format="wav"))
    else:
        # print("wav")
        sound = AudioSegment.from_file(sound_data, "wav")
        return sound, io.BufferedRandom(sound.export(format="wav"))

st.title("タイトル")
st.write("説明")

st.title("①ファイルから文字起こし")
st.write("説明")
file = st.file_uploader("", type=["mp3", 'wav'])
if file:
    st.audio(file)
    start_one = st.button("①開始")
    if start_one == True:
        conversion = conversion_mp3_mp4(file, file.name)
        # print(conversion[0])
        # print(conversion[1])
        chunks = split_on_silence(conversion[0], min_silence_len=2000, silence_thresh=-40, keep_silence=1000)
        # print(chunks)
        z = [ io.BufferedRandom(chunk.export(format="wav")) for i, chunk in enumerate(chunks)]
        # print(z)
        r = sr.Recognizer()
        texts = []
        for i in z:
            with sr.AudioFile(i) as source:

                audio = r.record(source)

            text = r.recognize_google(audio, language='ja-JP', show_all=False)
            texts.append(text)
        text = "\n".join(texts)
        st.write(text)
        
        contents_one = f"ファイルから文字起こしファイルから文字起こしファイルから文字起こし"
        download_one = st.download_button("①ダウンロード", text)


st.title("②リアルタイムで文字起こし")
st.write("説明")
start_two = st.button("②開始")
if start_two:
    contents_two = f"リアルタイムで文字起こしリアルタイムで文字起こしリアルタイムで文字起こし"
    download_two = st.download_button("②ダウンロード", contents_two)
    st.write(f"結果表示\n\n{contents_two}")
