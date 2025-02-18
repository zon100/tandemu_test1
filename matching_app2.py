import streamlit as st
import uuid  # 一意のIDを生成するためのモジュール

# アプリの状態管理
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "home"
# 留学生か日本人かの切換
if "user_type" not in st.session_state:
    st.session_state.user_type = None
# プロフィールデータを保存する変数
if "profile" not in st.session_state:
    st.session_state.profile = None

# ホーム画面
def home():
    st.title("留学生と大学生のマッチングアプリ")
    st.write("日本人または留学生を選択してください。")
    user_type = st.radio("あなたはどちらですか？", ["日本人", "Exchange Student"])
    
    if st.button("次へ"):
        st.session_state.user_type = user_type
        st.session_state.current_mode = "profile"

# プロフィール入力画面
def profile_input():
    st.title("プロフィール入力")
    # 既存のプロフィールを取得（存在しない場合は新しいIDを生成）
    if st.session_state.profile:
        profile = st.session_state.profile
    else:
        profile = {"id": str(uuid.uuid4())}  # 新しいユーザーには一意のIDを割り当て
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
        # `st.session_state.profile` が None の場合のチェック
        if st.session_state.profile is None:  # 初回登録時にIDを生成
            profile["id"] = str(uuid.uuid4())  # ユニークなIDを生成
        else:  # 更新時には既存のIDを保持
            profile["id"] = st.session_state.profile.get("id", str(uuid.uuid4()))

        st.session_state.profile = profile  # プロフィールを保存

        if "all_profiles" not in st.session_state:
            st.session_state.all_profiles = []
        
        # 既存プロフィールの更新または新規登録
        st.session_state.all_profiles = [
            p if p["id"] != profile["id"] else profile for p in st.session_state.all_profiles
        ] + ([profile] if not any(p["id"] == profile["id"] for p in st.session_state.all_profiles) else [])

        st.success("プロフィールが登録されました！")
        st.session_state.current_mode = "menu"  # モード選択画面に切り替える

# モード選択画面
def mode_selection():
    if st.session_state.user_type == "Exchange Student":
        st.title("Mode Selection")
        st.write("Please select a mode below:")
        if st.button("Message Mode"):
            st.session_state.current_mode = "message_mode"
        if st.button("Search Mode"):
            st.session_state.current_mode = "search_mode"
        if st.button("Event Mode"):
            st.session_state.current_mode = "event_mode"
        if st.button("Profile Input"):
            st.session_state.current_mode = "profile"
    else:
        st.title("モード選択")
        st.write("以下のモードから選択してください：")
        if st.button("メッセージモード"):
            st.session_state.current_mode = "message_mode"
        if st.button("人探しモード"):
            st.session_state.current_mode = "search_mode"
        if st.button("イベントモード"):
            st.session_state.current_mode = "event_mode"
        if st.button("プロフィール入力"):
            st.session_state.current_mode = "profile"

# メッセージモード
def message_mode():
    st.title("メッセージモード")
    st.write("チャット機能がここに表示されます。")
    if st.button("戻る"):
        st.session_state.current_mode = "menu"

# 人探しモード
def search_mode():
    if st.session_state.user_type == "Exchange Student":
        st.title("Search Mode")
        search_hobby = st.text_input("Search by Hobby")
        search_target_country = st.text_input("Search by Target Country")
        
        st.write("Registered Users:")
    else:
        st.title("人探しモード")
        search_hobby = st.text_input("趣味で検索")
        search_target_country = st.text_input("行きたい国で検索")
        
        st.write("登録者一覧:")

    # 検索結果のフィルタリング
    filtered_profiles = []
    for profile in st.session_state.all_profiles:
        match_hobby = search_hobby.lower() in profile.get("hobby", "").lower() if search_hobby else True
        match_country = (
            search_target_country.lower() in profile.get("target_country", "").lower() or
            search_target_country.lower() in profile.get("country", "").lower()
            if search_target_country else True
        )
        if match_hobby and match_country:
            filtered_profiles.append(profile)

    # 検索結果を表示
    if filtered_profiles:
        for profile in filtered_profiles:
            st.write("---")
            st.write(f"**Type**: {profile['type']}" if st.session_state.user_type == "Exchange Student" else f"**タイプ**: {profile['type']}")
            st.write(f"**Name**: {profile['name']}" if st.session_state.user_type == "Exchange Student" else f"**名前**: {profile['name']}")
            st.write(f"**Faculty**: {profile['faculty']}" if st.session_state.user_type == "Exchange Student" else f"**学部**: {profile['faculty']}")
            if profile["type"] == "日本人":
                st.write(f"**Age**: {profile['age']}" if st.session_state.user_type == "Exchange Student" else f"**年齢**: {profile['age']}")
                st.write(f"**Target Country**: {profile['target_country']}" if st.session_state.user_type == "Exchange Student" else f"**行きたい国**: {profile['target_country']}")
            else:
                st.write(f"**Country of Origin**: {profile['country']}" if st.session_state.user_type == "Exchange Student" else f"**出身国**: {profile['country']}")
            st.write(f"**Hobby**: {profile['hobby']}" if st.session_state.user_type == "Exchange Student" else f"**趣味**: {profile['hobby']}")
    else:
        st.warning("No users found matching the criteria." if st.session_state.user_type == "Exchange Student" else "条件に合う登録者が見つかりませんでした。")

    if st.button("Back" if st.session_state.user_type == "Exchange Student" else "戻る"):
        st.session_state.current_mode = "menu"

# イベント機能
def event_mode():
    st.title("イベント機能")
    st.write("イベントを作成・参加する機能がここに表示されます。")
    if st.button("戻る"):
        st.session_state.current_mode = "menu"

# モードに応じて適切な関数を呼び出す
if st.session_state.current_mode == "home":
    home()
elif st.session_state.current_mode == "profile":
    profile_input()
elif st.session_state.current_mode == "menu":
    mode_selection()
elif st.session_state.current_mode == "message_mode":
    message_mode()
elif st.session_state.current_mode == "search_mode":
    search_mode()
elif st.session_state.current_mode == "event_mode":
    event_mode()
