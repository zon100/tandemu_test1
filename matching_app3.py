import streamlit as st
import uuid  # 一意のIDを生成するためのモジュール
import psycopg2  # PostgreSQL用のモジュール
from psycopg2.extras import RealDictCursor

# PostgreSQLデータベース接続設定
def init_connection():
    return psycopg2.connect(
        host="localhost",  # データベースホスト
        database="matching_app",  # データベース名
        user="your_username",  # ユーザー名
        password="your_password",  # パスワード
        cursor_factory=RealDictCursor
    )

# データベース初期化（テーブル作成）
def init_db():
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY,
                user_type TEXT,
                name TEXT,
                faculty TEXT,
                age INTEGER,
                target_country TEXT,
                hobby TEXT,
                country TEXT,
                email TEXT
            )
            """
        )
        conn.commit()
    conn.close()

# プロフィールをデータベースに保存する関数
def save_profile_to_db(profile):
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO profiles (id, user_type, name, faculty, age, target_country, hobby, country, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                user_type = EXCLUDED.user_type,
                name = EXCLUDED.name,
                faculty = EXCLUDED.faculty,
                age = EXCLUDED.age,
                target_country = EXCLUDED.target_country,
                hobby = EXCLUDED.hobby,
                country = EXCLUDED.country,
                email = EXCLUDED.email
            """,
            (
                profile["id"],
                profile.get("type"),
                profile.get("name"),
                profile.get("faculty"),
                profile.get("age"),
                profile.get("target_country"),
                profile.get("hobby"),
                profile.get("country"),
                profile.get("email"),
            )
        )
        conn.commit()
    conn.close()

# データベースからすべてのプロフィールを取得する関数
def get_all_profiles():
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM profiles")
        profiles = cur.fetchall()
    conn.close()
    return profiles

# アプリの状態管理
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "home"
if "user_type" not in st.session_state:
    st.session_state.user_type = None
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
    if st.session_state.profile:
        profile = st.session_state.profile
    else:
        profile = {"id": str(uuid.uuid4())}  # 新しいユーザーには一意のIDを割り当て

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

    profile["email"] = st.text_input("Email")

    if st.button("プロフィールを登録"):
        st.session_state.profile = profile
        save_profile_to_db(profile)
        st.success("プロフィールが登録されました！")
        st.session_state.current_mode = "menu"

# 管理者用ページ
def admin_page():
    st.title("管理者用ページ")
    st.write("登録されたプロフィール情報：")

    profiles = get_all_profiles()
    for profile in profiles:
        st.write("---")
        st.write(f"**Type**: {profile['user_type']}")
        st.write(f"**Name**: {profile['name']}")
        st.write(f"**Faculty**: {profile['faculty']}")
        st.write(f"**Email**: {profile['email']}")

    if st.button("戻る"):
        st.session_state.current_mode = "menu"

# モード選択画面
def mode_selection():
    if st.session_state.user_type == "Exchange Student":
        st.title("Mode Selection")
        st.write("Please select a mode below:")
    else:
        st.title("モード選択")
        st.write("以下のモードから選択してください：")

    if st.button("Admin Mode"):
        st.session_state.current_mode = "admin"
    if st.button("プロフィール入力"):
        st.session_state.current_mode = "profile"

# メイン処理
init_db()  # データベース初期化

if st.session_state.current_mode == "home":
    home()
elif st.session_state.current_mode == "profile":
    profile_input()
elif st.session_state.current_mode == "menu":
    mode_selection()
elif st.session_state.current_mode == "admin":
    admin_page()
