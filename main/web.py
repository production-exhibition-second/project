# 音声を扱う
from re import T
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import io, time, datetime
import streamlit as st


def conversion_mp3_mp4(sound_data, file_name):
    """ 音声ファイルをwavに変換する
    sound_data : アップロードされた音声ファイル
    file_name : アップロードされた音声ファイル名
    """
    # print(os.path.splitext(file_name))
    if "mp3" in file_name:
        # print("mp3")
        sound = AudioSegment.from_file(sound_data, "mp3")
        # print(sound)
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
file = st.file_uploader("", type=["mp3", 'wav', "mp4"])
if file:
    st.audio(file)
    start_one = st.button("①開始")
    if start_one == True:

        placeholder = st.empty()
        placeholder2 = st.empty()
        placeholder.write("処理中・・・")

        conversion = conversion_mp3_mp4(file, file.name)

        # 無音部分のカット
        chunks = split_on_silence(conversion[0], min_silence_len=2000, silence_thresh=-40, keep_silence=1000)

        # カットされた音声をメモリの一時的に保存する
        z = [ io.BufferedRandom(chunk.export(format="wav")) for i, chunk in enumerate(chunks)]

        texts = []
        
        r = sr.Recognizer()
        for i in z:
            with sr.AudioFile(i) as source:

                audio = r.record(source)

            try:
                # テキストに変換
                text = r.recognize_google(audio, language='ja-JP', show_all=False) # 英語にも太陽出来るようにできればする
                texts.append(text)
            except:
                placeholder2.write("一部変換できませんでした")

        placeholder.write("完了！")

        if len(texts) != 0:
            text = "\n".join(texts) # テキストファイル用
            view = "、".join(texts) # 表示用

            st.write(view)

            download_one = st.download_button("①ダウンロード", text)


st.title("②リアルタイムで文字起こし")
st.write("説明")
col1, col2 = st.columns(2)
# 開始ボタン
with col1:
    start_two = st.button("②開始")

# 開始が押下されたとき
if start_two:
    with col2:
        stop_two = st.button("②停止")
    # マイク接続確認
    # """
    # マイクのtryのところをマイクの"check"だけにして
    # マイクがあればelseの処理に行くようにした
    # """
    try:
        check = sr.Microphone()
    except OSError as e:
        st.write('<span style="color:red;">マイクを接続してください</span>', unsafe_allow_html=True)
    else: # エラーが無ければ処理に入る
        # マイクの入力の繰り返し
        texts = []
        past = time.time()
        texts.append(f"{datetime.date.today()}\n")
        processing = True

        while not stop_two and time.time() - past <= 60: # 両方がTrueの場合処理されるようになっている
            contents_two = ''
            if processing: # エラー処理がされても連続で表示されないように
                placeholder = st.empty()
                placeholder.write("処理中・・・")

            r = sr.Recognizer()
            with check as source:
                past = time.time()
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)

            # データ生成
            now = datetime.datetime.now()
            now = f"{now:%H:%M:%S}"

            try: # 変換が出来なかった時のtryを追加
                contents_two = r.recognize_google(audio, language='ja-JP')
            except sr.UnknownValueError:
                processing = False
                print('Error1')
            except sr.RequestError as e:
                processing = False
                print('Error2')
            else: # エラーが無ければ処理に入る
                processing = True

                if contents_two:
                    placeholder.write(contents_two)

                    contents_two = f"{now} {contents_two}"
                    texts.append(contents_two)
                
                # 停止が押下されたとき
                if stop_two == True:
                    contents_two_l = "\n".join(texts)
                    download_two = st.download_button("②ダウンロード", contents_two_l)
