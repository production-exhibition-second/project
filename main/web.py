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

st.title("らくらく文字起こし")
st.write("会議の議事録作成、インタビュー・動画の音声をテキスト化などにご活用いただけます。")

st.write("<hr>", unsafe_allow_html=True)
st.header("ファイルから文字起こし")
st.write("音声・動画ファイルをアップロードするだけでテキストに変換")
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
            view = "".join(texts) # 表示用
            text = text.replace(" ", "").replace("です", "です\n").replace("ます", "ます\n")
            view = view.replace(" ", "").replace("です", "です\n\n").replace("ます", "ます\n\n")
            st.write(view)
            now = datetime.datetime.now()
            now = f"{now:%Y-%m-%d:%H-%M-%S}"
            download_one = st.download_button("①ダウンロード", text, f"file_{now}.txt")


st.write("<hr>", unsafe_allow_html=True)
st.header("リアルタイムで文字起こし")
st.write("マイク入力にてその場でテキストに変換\n\n「停止、ストップ、終了、終わり」いずれかで終了")

col1, col2 = st.columns(2)
# 開始ボタン
with col1:
    start_two = st.button("②開始")

# 開始が押下されたとき
if start_two:
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
        while time.time() - past <= 60: # 両方がTrueの場合処理されるようになっている
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
                # print('Error1')
            except sr.RequestError as e:
                processing = False
                # print('Error2')
            else: # エラーが無ければ処理に入る
                processing = True

                # 停止
                if contents_two in ["停止", "ストップ", "終了", "終わり"]: # これだとコードが少なくできた
                # if contents_two == "停止" or contents_two == "ストップ" or contents_two == "終了" or contents_two == "終わり":
                # if contents_two == ("停止" or "ストップ" or "終了" or "終わり"): これは出来なかった
                    placeholder.write('終了しました')
                    contents_two_l = "\n".join(texts)
                    # download_two = st.download_button("②ダウンロード", contents_two_l)
                    with col2:
                        now = datetime.datetime.now()
                        now = f"{now:%Y-%m-%d:%H-%M-%S}"
                        download_two = st.download_button("②ダウンロード", contents_two_l, f"file_{now}.txt")
                    break

                elif contents_two:
                    placeholder.write(contents_two)
                    contents_two = f"{now} {contents_two}"
                    texts.append(contents_two)
                
