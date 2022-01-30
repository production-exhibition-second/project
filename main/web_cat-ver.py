# 音声を扱う
from re import T
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import io, time, datetime
import streamlit as st

import wave
import struct
import math
from scipy import fromstring, int16
import numpy
import os
import glob

# 自然数ソート
from natsort import natsorted

# ファイルの分割
def wav_cut(directory, time, filesave):

    for i in directory:
        file_name, exe = os.path.splitext(os.path.basename(i))
        # print(file_name)
        # ファイルを読み出し
        wavf = i
        wr = wave.open(wavf, 'r')
    
        # waveファイルが持つ性質を取得
        ch = wr.getnchannels()
        width = wr.getsampwidth()
        fr = wr.getframerate()
        fn = wr.getnframes()
        total_time = 1.0 * fn / fr
        integer = math.floor(total_time) # 小数点以下切り捨て
        t = int(time)  # 秒数[sec]
        frames = int(ch * fr * t)
        num_cut = int(math.ceil(integer/t))

        # waveの実データを取得し、数値化
        data = wr.readframes(wr.getnframes())
        wr.close()
        X = numpy.frombuffer(data, dtype=int16)
        # print(X)
    
        for i in range(num_cut):
            # print(i)
            # 出力データを生成
            outf = f"{filesave}/{file_name}-{str(i)}.wav"
            start_cut = i*frames
            end_cut = i*frames + frames
            # print(f'スタート{start_cut}')
            # print(f'エンド{end_cut}')
            Y = X[start_cut:end_cut]
            outd = struct.pack("h" * len(Y), *Y)
 
            # 書き出し
            ww = wave.open(outf, 'w')
            ww.setnchannels(ch)
            ww.setsampwidth(width)
            ww.setframerate(fr)
            ww.writeframes(outd)
            ww.close()


def conversion_mp3_mp4(sound_data, file_name, save_dri):
    """ 音声ファイルをwavに変換する
    sound_data : アップロードされた音声ファイル
    file_name : アップロードされた音声ファイル名
    """

    # print(os.path.splitext(file_name))
    if "mp3" in file_name:
        # print("mp3")
        sound = AudioSegment.from_file(sound_data, "mp3")
        # print(sound)
        sound.export(f"{save_dri}/output1.wav", format="wav")
        # return sound, io.BufferedRandom(sound.export(format="wav"))
    elif "mp4" in file_name:
        # print("mp4")
        sound = AudioSegment.from_file(sound_data, "mp4")
        sound.export(f"{save_dri}/output1.wav", format="wav")
        # return sound, io.BufferedRandom(sound.export(format="wav"))
    else:
        # print("wav")
        sound = AudioSegment.from_file(sound_data, "wav")
        sound.export(f"{save_dri}/output1.wav", format="wav")
        # return sound, io.BufferedRandom(sound.export(format="wav"))

# ディレクトリーたち
directory = os.path.dirname(__file__)
# save_audio = r"main\TEMP\audio" # wav変換ファイル一時保存
# audio_cat = r"main\TEMP\cat"    # ファイルカット一時保存
save_audio = os.path.join(directory, r"TEMP/audio") # wav変換ファイル一時保存
audio_cat = os.path.join(directory, r"TEMP/cat")    # ファイルカット一時保存

y = glob.glob(f'{save_audio}/*')
y2 = glob.glob(f'{audio_cat}/*')
for i in y:
    os.remove(i)
for i in y2:
    os.remove(i)

# 切り取りタイム
cut_time = 60

st.set_page_config(
    page_title="らくらく文字起こし",
    # layout="wide", # 全画面か中央表示か
)

st.title("らくらく文字起こし")
st.write("会議の議事録作成、インタビュー・動画の音声をテキスト化などにご活用いただけます。")

st.write("<hr>", unsafe_allow_html=True)
st.header("ファイルから文字起こし")
st.write("音声・動画ファイルをアップロードするだけでテキストに変換")
file = st.file_uploader("", type=["mp3", 'wav', "mp4"])

if file:
    st.audio(file)
    start_one = st.button("1開始")
    if start_one == True:
        texts = []
        dt = time.time() # 経過時間計測

        placeholder = st.empty()
        placeholder2 = st.empty()
        placeholder.warning("処理中・・・")

        conversion = conversion_mp3_mp4(file, file.name, save_audio)
        audio_dri = glob.glob(f'{save_audio}/*')
        wav_cut(audio_dri, cut_time, audio_cat)
        datas = natsorted(glob.glob(f'{audio_cat}/*'))

        r = sr.Recognizer()
        for i in datas:
            with sr.AudioFile(i) as source:

                audio = r.record(source)

            try:
                # テキストに変換
                text = r.recognize_google(audio, language='ja-JP', show_all=False) # 英語にも太陽出来るようにできればする
                texts.append(text)
                answer = '変換完了'
            except:
                # placeholder2.write("一部変換できませんでした")
                placeholder2.warning("一部変換できませんでした") # ボックス追加
                answer = '変換できなかった'
            
            # 何が変換されたかチェック用
            print(f'{i} {answer}')

        # placeholder.write('<span style="color:blue;">完了！</span>', unsafe_allow_html=True)
        placeholder.success('完了！')


        if len(texts) != 0:
            text = "\n".join(texts) # テキストファイル用
            view = "".join(texts) # 表示用
            text = text.replace(" ", "").replace("です", "です\n").replace("ます", "ます\n")
            view = view.replace(" ", "").replace("です", "です\n\n").replace("ます", "ます\n\n")
            # st.write(view)
            st.info(view)

            now = datetime.datetime.now()
            now = f"{now:%Y-%m-%d:%H-%M-%S}"
            download_one = st.download_button("①ダウンロード", text, f"file_{now}.txt")
            st.balloons()

            elapsed_time = time.time() - dt # 経過時間計測
            st.write(f'ラップ{elapsed_time:.2f}')
            # print(f'ラップ{elapsed_time:.2f}')



st.write("<hr>", unsafe_allow_html=True)
st.header("リアルタイムで文字起こし")
st.write("マイク入力にてその場でテキストに変換\n\n「停止、ストップ、終了、終わり」いずれかで終了")

col1, col2 = st.columns(2)
# 開始ボタン
with col1:
    start_two = st.button("2開始")

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
        # st.write('<span style="color:red;">マイクを接続してください</span>', unsafe_allow_html=True)
        st.error('マイクを接続してください')
    else: # エラーが無ければ処理に入る
        # マイクの入力の繰り返し
        texts = []
        past = time.time()
        texts.append(f"{datetime.date.today()}\n")
        processing = True
        stop = True
        while stop: # time.time() - past <= 60: # 両方がTrueの場合処理されるようになっている
            contents_two = ''
            if processing: # エラー処理がされても連続で表示されないように
                placeholder = st.empty()
                placeholder.write("入力待ち・・・")

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
                    # placeholder.write('終了しました')
                    placeholder.success('終了しました') # ボックス追加
                    contents_two_l = "\n".join(texts)
                    stop = False
                    # download_two = st.download_button("②ダウンロード", contents_two_l)
                    with col2:
                        now = datetime.datetime.now()
                        now = f"{now:%Y-%m-%d:%H-%M-%S}"
                        download_two = st.download_button("②ダウンロード", contents_two_l, f"file_{now}.txt")
                    break

                elif contents_two:
                    placeholder.write(contents_two)
                    # placeholder.info(contents_two) # ボックス追加
                    contents_two = f"{now} {contents_two}"
                    texts.append(contents_two)
                
