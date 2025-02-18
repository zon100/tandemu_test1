import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# セッション状態を使ってプロファイルデータを保持
if "profiles" not in st.session_state:
    st.session_state.profiles = []

if "current_step" not in st.session_state:
    st.session_state.current_step = "home"

# ホーム画面
def home():
    st.title("留学生と大学生のマッチングアプリ")
    st.subheader("あなたはどちらですか？")
    user_type = st.radio("選択してください", ("日本人", "留学生"))
    if st.button("次へ"):
        st.session_state.user_type = user_type
        st.session_state.current_step = "profile_input"

# プロフィール入力画面
def profile_input():
    st.title("プロフィール入力")
    profile = {}

    if st.session_state.user_type == "日本人":
        st.subheader("日本語で入力してください")
        profile["type"] = "日本人"
        profile["name"] = st.text_input("名前")
        profile["faculty"] = st.text_input("学部")
        profile["age"] = st.number_input("年齢", min_value=0, max_value=100, step=1)
        profile["target_country"] = st.text_input("行きたい国")
        profile["hobby"] = st.text_input("趣味")
    else:
        st.subheader("Please fill in your information in English")
        profile["type"] = "留学生"
        profile["name"] = st.text_input("Name")
        profile["faculty"] = st.text_input("Faculty")
        profile["country"] = st.text_input("Country of origin")
        profile["hobby"] = st.text_input("Hobby")
    
    if st.button("プロフィールを登録"):
        # 入力内容をセッション状態に保存
        st.session_state.profiles.append(profile)
        st.success("プロフィールを登録しました！")
        st.session_state.current_step = "matching"

# マッチング画面
def matching():
    st.title("マッチング結果")

    # プロフィールデータを表示
    if st.session_state.profiles:
        df = pd.DataFrame(st.session_state.profiles)
        st.write("登録されたプロフィール:")
        st.dataframe(df)
    else:
        st.info("まだプロフィールが登録されていません。")
        return

    if len(st.session_state.profiles) > 1:
        # AIを用いた簡易マッチング例 (TF-IDF + コサイン類似度)
        vectorizer = TfidfVectorizer()
        hobby_vectors = vectorizer.fit_transform([p["hobby"] for p in st.session_state.profiles])
        similarities = cosine_similarity(hobby_vectors)

        st.subheader("マッチング結果（趣味の類似度に基づく）:")
        for i, profile in enumerate(st.session_state.profiles):
            similar_profiles = [
                (j, round(sim, 2)) 
                for j, sim in enumerate(similarities[i]) 
                if i != j
            ]
            similar_profiles.sort(key=lambda x: -x[1])
            top_match = similar_profiles[0] if similar_profiles else None

            st.write(f"- {profile['name']} の最も近いマッチ: {st.session_state.profiles[top_match[0]]['name']} (類似度: {top_match[1]})")
    else:
        st.info("マッチングを行うには、少なくとも2人のプロフィールが必要です。")

# 現在のステップに応じて適切な関数を呼び出す
if st.session_state.current_step == "home":
    home()
elif st.session_state.current_step == "profile_input":
    profile_input()
elif st.session_state.current_step == "matching":
    matching()
