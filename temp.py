# 네이버 검색 API예제는 블로그를 비롯 전문자료까지 호출방법이 동일하므로 blog검색만 대표로 예제를 올렸습니다.
# 네이버 검색 Open API 예제 - 블로그 검색
import requests
import random
import tensorflow as tf
import pymysql
import numpy as np

from keras.layers import *
from keras.models import *

from keras.utils import *
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

# MySQL 아이디와 비밀번호는 본인의 환경에 맞게 설정
conn = pymysql.connect(
    host="localhost", user="root", password="As731585!", db="stock_data", charset="utf8"
)
curs = conn.cursor()
sql = """select name, code from stock_master order by code"""
curs.execute(sql)
res = curs.fetchall()  # fetchall 실행결과얻기
gamma_x = np.asarray(res)  # 행렬로 가져오기
print(gamma_x)
word = []
code = []
for i in range(len(gamma_x)):
    word.append(gamma_x[i][0])
    code.append(gamma_x[i][1])

max_word = 20

for i in range(len(gamma_x)):

    file = "./textfile/" + str(code[i]) + ".txt"
    text = ""
    textarr = []
    with open(file, encoding="utf8") as f:
        lines = f.readlines()
        text = text.join(lines)

    for t in text.split("\n"):
        textarr.append(t)

    textarr = np.array(textarr)

    # 케라스 문서 : https://keras.io/ko/preprocessing/text/
    # 각 텍스트를 (딕셔너리 내 하나의 정수가 한 토큰의 색인 역할을 하는) 정수 시퀀스로,
    # 혹은 단어 실셈이나 tf-idf 등을 기반으로 각 토큰의 계수가 이진인 벡터로 변환하여 말뭉치를 벡터화할 수 있도록 해줍니다.
    # filter : 쓸데없는 특수기호는 다 제거한다.
    token = Tokenizer(
        lower=False,
        split=" ",
        filters="!@#$%^&*()[]<>,.?\"'■…▶·◆‘’◇“”ⓒ【】=@<b></b>quot;apos",
    )
    # 각 단어의 인덱스를 구축
    token.fit_on_texts(textarr)

    # 문자열을 정수 인덱스의 리스트로 변환
    seq = token.texts_to_sequences(textarr)

    # 문장 길이를 동일하게 만들기 위한 패딩
    seq = pad_sequences(seq, maxlen=max_word)
    print(seq.shape)

    # 신경망에 입력하기 위한 차원변환
    X = seq
    Y = np.vstack((X[1:], X[0]))

    X = X.reshape(-1, max_word, 1)
    Y = Y.reshape(-1, max_word, 1)

    # 원/핫 인코딩으로 변환
    Y = to_categorical(Y)

    with tf.device("/cpu:0"):
        model = Sequential()

        model.add(LSTM(128, return_sequences=True, input_shape=(max_word, 1)))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dense(len(token.word_index) + 1, activation="softmax"))
        model.summary()
        model.compile(
            loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
        )

        path = str("./models/") + str(code[i])
        saved = path + ".hdf5"

        # 모델평가 : 테스트 모드에서의 모델의 손실 값과 측정항목 값을 반환합니다.
        # 즉 학습한 모델에 대한 정확도를 평가하는 값으로 간주(loss 와 accuracy)
        # 케라스문서 : https://keras.io/ko/models/model/
        score = model.evaluate(X, Y, verbose=1)

        maxepoch = 0

        while score[1]:

            history = model.fit(
                X, Y, batch_size=1, epochs=1
            )  # 학습할 양도 얼마되지 않으니 배치사이즈는 1로 해주자.
            score = model.evaluate(X, Y, verbose=1)
            model.save_weights(saved)
            maxepoch += 1

            if (
                score[1] > 0.95
            ):  # 정확도가 95% 만 넘어가도 그냥 나와라.(학습중단) -> 정확도도 80% 정도면 괜찮지 않을까한다.
                break
            if maxepoch > 50:  # 95% 못넘기고 50 번 이상 반복하면 그냥 나와라.(학습중단) -> 횟수는 임의 조정이 가능하다.
                break
