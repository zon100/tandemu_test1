import streamlit as st
import uuid  # 一意のIDを生成するためのモジュール
import pandas as pd  # データ保存用
import os
import psycopg2
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh  # 追加
import re


# SupabaseのURLとキー（環境変数で管理するのが望ましい）
SUPABASE_URL = "https://zancatjxgdofhxlemcgf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphbmNhdGp4Z2RvZmh4bGVtY2dmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk5MDQyNDQsImV4cCI6MjA1NTQ4MDI0NH0.FeLkr0k_WSLXGQFtU2PyKMhMS_Zywbzb_FSTAIOsjsk"

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 初期化
if "agreed" not in st.session_state:
    st.session_state["agreed"] = False
if "current_mode" not in st.session_state:
    st.session_state["current_mode"] = "agreement"  # 初期画面は誓約書

# 誓約書画面
if st.session_state["current_mode"] == "agreement":
    st.title("誓約書の同意/Acceptance of the Pledge")

    # 誓約文の表示
    st.write("""
    ### 誓約書/pledge
    私は、本アプリを利用するにあたり、以下の事項を誓約します。/I, the undersigned, hereby pledge the following items in connection with my use of this application

    1. 出会い系サイト規制法および関連法令を遵守し、適正な利用を行うこと。/To comply with the Dating Site Regulation Law and related laws and regulations, and to use the site in an appropriate manner.
    2. 18歳未満でないことを確認し、虚偽の情報を提供しないこと。/Verify that you are not under 18 years of age and do not provide false information.
    3. 児童の利用を防止し、不適切な利用を行わないこと。/Preventing the use of children and ensuring that they do not use the facility inappropriately.
    4. 法令に基づき、適切な行動を取ること。/Act appropriately in accordance with laws and regulations.

    **上記に同意する場合は、チェックを入れてください。/If you agree with the above, please check the box.**
    """)

    # チェックボックス
    agree = st.checkbox("誓約書に同意します/I agree to the Pledge")

    # ボタンを有効化する制御
    if agree:
        if st.button("次へ/Next"):
            st.session_state["agreed"] = True
            st.session_state["current_mode"] = "auth"  # ログイン画面へ
            st.rerun()
    else:
        st.error("誓約書に同意しないとアプリを利用できません。/You must agree to the pledge to use the application.")

#プロフィールをSupabaseに保存
def save_profile_to_supabase(profile):
    email = profile.get("email")  # 入力されたメールアドレスを取得
    table_name = "profiles"  # profilesテーブルのみを使用
    
    # 既存のユーザーを検索（email または id）
    existing_user = supabase.table(table_name).select("id").or_(
        f"email.eq.{email},id.eq.{profile['id']}"
    ).execute()

    if existing_user.data:
        # 既存のデータがある場合は更新
        profile_id = existing_user.data[0]["id"]
        profile["id"] = profile_id  # IDを保持
        data = supabase.table(table_name).update(profile).eq("id", profile_id).execute()
    else:
        # 新規登録（IDを自動生成）
        profile.pop("id", None)  # IDを削除（Supabase側で生成）
        data = supabase.table(table_name).insert(profile).execute()

    return data



# アプリの状態管理
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "auth"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "home"
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "all_profiles" not in st.session_state:
    st.session_state.all_profiles = []
if "events" not in st.session_state:
    st.session_state.events = []  # イベントのリストを初期化



# ログイン / 新規登録画面

def is_allowed_email(email):
    """許可されたドメインのみ通す（正規表現で厳格にチェック）"""
    allowed_domains = [r"@m\.isct\.ac\.jp$", r"@m\.titech\.ac\.jp$"]
    email = email.strip().lower()  # 小文字変換 + 余分なスペース削除
    return any(re.search(domain, email) for domain in allowed_domains)



def auth():
    st.title("ログイン / 新規登録(Login / New Registration)")
    choice = st.radio("選択してください", ["ログイン/Login", "新規会員登録/New Registration"])
    
    if choice == "ログイン/Login":
        email = st.text_input("メールアドレス/email")
        username = st.text_input("ユーザーネーム/username")
        if st.button("ログイン/Login"):
           # メールアドレスのドメインチェックを追加
           if not is_allowed_email(email):
                st.error("このメールアドレスは使用できません。/ This email address is not allowed.")
           else:
            response = supabase.table("profiles").select("*").eq("email", email).eq("name", username).execute()
            if response.data:
                st.session_state.profile = response.data[0]
                st.session_state.user_id = response.data[0]["id"]
                st.session_state.current_mode = "menu"
                st.success("ログイン成功！/Login Successed!")
            else:
                st.error("ユーザーが見つかりません。/User not found.")
    
    elif choice == "新規会員登録/New Registration":
        if st.button("次へ/Next"):
            st.session_state.current_mode = "home"



# ホーム画面
def home():
    st.title("Tandem Science Tokyo(留学生と大学生のマッチングアプリ/Matching app for international students and university students)")
    
    # アプリの説明メッセージ
    st.write("""
    ### このアプリへようこそ！
    このアプリは **留学生と東工大生の交流を促進するためのアプリ** です。  
    ルールを守り、**犯罪や不正利用をしないように** お願いします。  
    **不正利用や援助交際などが発覚した場合、アプリの利用が停止され、必要に応じて警察に通報** いたします。  
    **正しく楽しく** このアプリを使っていきましょう！
    """)

    # 英語訳
    st.write("""
    ### Welcome to this app!
    This app is designed **to facilitate interaction between exchange students and Tokyo Tech students**.  
    Please follow the rules and **do not engage in any illegal or fraudulent activities**.  
    **If misuse or compensated dating is discovered, access to the app will be revoked, and in serious cases, the police may be notified**.  
    Let's use this app **correctly and enjoyably**!
    """)

    # 「次へ」ボタン
    if st.button("次へ / Next"):
        st.session_state.current_mode = "profile"  # プロフィール入力画面へ遷移


# プロフィール入力画面
def profile_input():
    st.title("プロフィール入力 / Profile Input")

    # セッションに all_profiles がない場合は空リストで初期化
    if "all_profiles" not in st.session_state:
        st.session_state.all_profiles = []

    # セッションに profile がない場合は初期化
    if "profile" not in st.session_state or not isinstance(st.session_state.profile, dict):
        st.session_state.profile = {"id": str(uuid.uuid4())}  # 初回はIDを設定

    profile = st.session_state.profile

    # 共通の入力フィールド
    profile["name"] = st.text_input("名前 / Name", profile.get("name", ""))
    profile["faculty"] = st.text_input("学部 / Faculty", profile.get("faculty", ""))
    profile["age"] = st.number_input("年齢 / Age", min_value=0, max_value=100, step=1)
    profile["hobby"] = st.text_input("趣味 / Hobby", profile.get("hobby", ""))
    profile["learning_language"] = st.text_input("学びたい言語 / Learning Language", profile.get("learning_language", ""))
    profile["speaking_language"] = st.text_input("話せる言語 / Speaking Language", profile.get("speaking_language", ""))
    st.write("Emailアドレスのドメインは「～～@m.isct.ac.jp」および「～～@m.titech.ac.jp」で登録してください。それ以外のドメインではセキュリティ機能によりログインできません。/Please register the domain of your email address as “~~~@m.isct.ac.jp” or “~~@m.titech.ac.jp”. Other domains will not allow you to log in due to security features.")
    profile["email"] = st.text_input("Email Address", profile.get("email", ""))

    # 日本人・留学生共通で出身国を入力
    profile["country"] = st.text_input("出身国 / Country of Origin", profile.get("country", ""))

    if st.button("プロフィールを登録 / Register Profile"):
        # `id` が確実に存在することを保証
        if "id" not in profile:
            profile["id"] = str(uuid.uuid4())

        # `all_profiles` に同じ ID のプロファイルがなければ追加、あれば更新
        existing_profile = next((p for p in st.session_state.all_profiles if p["id"] == profile["id"]), None)

        if existing_profile:
            # 既存のプロフィールを更新
            existing_profile.update(profile)
        else:
            # 新規プロフィールを追加
            st.session_state.all_profiles.append(profile)

        st.session_state.profile = profile
        save_profile_to_supabase(profile)  # Supabase に保存
        st.success("プロフィールが登録されました！ / Profile registered successfully!")
        st.session_state.current_mode = "menu"


# モード選択画面
def mode_selection():
    st.title("モード選択 / Mode Selection")
    st.write("以下のモードから選択してください / Please select a mode below:")

    if st.button("メッセージモード / Message Mode"):
        st.session_state.current_mode = "message_mode"
    if st.button("人探しモード / Search Mode"):
        st.session_state.current_mode = "search_mode"
    if st.button("イベントモード / Event Mode"):
        st.session_state.current_mode = "event_mode"
    if st.button("プロフィール入力 / Profile Input"):
        st.session_state.current_mode = "profile"



# メッセージモード

# メッセージモードと検索機能の統合

# メッセージモード

# メッセージモード

def message_mode():
    """メッセージの送信相手を選択する画面"""
    st.title("メッセージモード / Message Mode")
    st.write("チャットしたい相手を選んでください / Select a user to chat with.")

    # 自分のプロフィール取得
    if not st.session_state.get("profile"):
        st.error("まずプロフィールを登録してください / Please register your profile first.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "menu"
        return

    user_profile = st.session_state.profile

    # ID の存在を確認
    if "id" not in user_profile:
        st.error("プロフィール ID が見つかりません。再登録してください / Profile ID not found. Please re-register.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "menu"
        return

    user_id = user_profile["id"]

    # 他のユーザー一覧を取得
    profiles = supabase.table("profiles").select("id, name, country").execute()
    all_profiles = profiles.data or []

    recipients = [p for p in all_profiles if "id" in p and p["id"] != user_id]

    if not recipients:
        st.warning("現在メッセージを送信できるユーザーがいません / No users available for messaging.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "menu"
        return

    # ユーザー選択
    selected_user = st.selectbox(
        "チャット相手を選択してください / Select a chat partner", 
        recipients, 
        format_func=lambda p: f"{p['name']} ({p['country']})"
    )

    if st.button("チャット開始 / Start Chat"):
        st.session_state["chat_partner"] = selected_user
        st.session_state.current_mode = "chat"
        st.rerun()

    if st.button("戻る / Back"):
        st.session_state.current_mode = "menu"
        st.rerun()


def chat_screen():
    """選択したユーザーとのチャット画面"""
    st.title("チャット画面 / Chat Screen")

    # 3秒ごとに自動更新
    #st_autorefresh(interval=3000, key="chat_refresh")

    # 自分のプロフィール取得
    if not st.session_state.get("profile"):
        st.error("まずプロフィールを登録してください / Please register your profile first.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "menu"
        return

    user_profile = st.session_state.profile

    if "id" not in user_profile:
        st.error("プロフィール ID が見つかりません。再登録してください / Profile ID not found. Please re-register.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "menu"
        return

    user_id = user_profile["id"]
    chat_partner = st.session_state.get("chat_partner")

    if not chat_partner:
        st.warning("チャット相手が選択されていません / No chat partner selected.")
        if st.button("戻る / Back"):
            st.session_state.current_mode = "message"
        return

    st.subheader(f"チャット相手: {chat_partner['name']} / Chat Partner: {chat_partner['name']}")

    # メッセージ履歴の取得（送受信両方）
    messages = supabase.table("messages").select("from_user, to_user, message, timestamp") \
        .or_(f"and(from_user.eq.{user_id},to_user.eq.{chat_partner['id']}),and(from_user.eq.{chat_partner['id']},to_user.eq.{user_id})") \
        .order("timestamp", desc=False).execute()

    # メッセージを表示
    st.write("### メッセージ履歴 / Message History")
    if messages.data:
        for msg in messages.data:
            sender = "あなた / You" if msg["from_user"] == user_id else chat_partner["name"]
            st.write(f"**{sender}**: {msg['message']} ({msg['timestamp']})")
    else:
        st.info("まだメッセージがありません / No messages yet.")
    
    # 初回実行時にセッションステートを初期化
    if "message" not in st.session_state:
       st.session_state.message = ""
    
    # メッセージ送信フォーム
    message = st.text_area("メッセージを入力してください / Enter your message", key="message")
    if st.button("送信 / Send"):
        if message.strip():
            message_data = {
                "id": str(uuid.uuid4()),
                "from_user": user_id,
                "to_user": chat_partner["id"],
                "message": message,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            supabase.table("messages").insert(message_data).execute()
            st.success("メッセージを送信しました！ / Message sent!")
            # **チャットボックスの内容をリセット**
            del st.session_state["message"]
            st.rerun()
        else:
            st.error("メッセージを入力してください / Please enter a message.")
    
    # 戻るボタン
    if st.button("戻る / Back"):
        st.session_state.current_mode = "message"
        st.rerun()


# ページ遷移処理
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "message"

if st.session_state.current_mode == "message":
    message_mode()
elif st.session_state.current_mode == "chat":
    chat_screen()


# 人探しモード
def search_mode():
    st.title("人探しモード / Search Mode")
    
    # Supabaseから登録者一覧を取得
    def load_profiles_from_supabase():
        profiles = supabase.table("profiles").select("*").execute()
        st.session_state.all_profiles = profiles.data or []

    # アプリ起動時に実行（データがない場合のみ取得）
    if "all_profiles" not in st.session_state or not st.session_state.all_profiles:
        load_profiles_from_supabase()
    
    # 検索項目
    search_name = st.text_input("名前 / Name")
    search_faculty = st.text_input("学部 / Faculty")
    search_hobby = st.text_input("趣味 / Hobby")
    search_country = st.text_input("出身国 / Country of Origin")
    search_learning_language = st.text_input("学びたい言語 / Learning Language")
    search_speaking_language = st.text_input("話せる言語 / Speaking Language")
    
    st.write("登録者一覧:")
    
    # フィルタリング処理
    filtered_profiles = []
    for profile in st.session_state.all_profiles:
        match_name = search_name.lower() in profile.get("name", "").lower() if search_name else True
        match_faculty = search_faculty.lower() in profile.get("faculty", "").lower() if search_faculty else True
        match_hobby = search_hobby.lower() in profile.get("hobby", "").lower() if search_hobby else True
        match_country = search_country.lower() in profile.get("country", "").lower() if search_country else True
        match_learning_language = search_learning_language.lower() in profile.get("learning_language", "").lower() if search_learning_language else True
        match_speaking_language = search_speaking_language.lower() in profile.get("speaking_language", "").lower() if search_speaking_language else True
        
        if all([match_name, match_faculty, match_hobby, match_country, match_learning_language, match_speaking_language]):
            filtered_profiles.append(profile)
    
    # 検索結果を表示
    if filtered_profiles:
        for profile in filtered_profiles:
            st.write("---")
            st.write(f"**名前 / Name**: {profile['name']}")
            st.write(f"**学部 / Faculty**: {profile['faculty']}")
            st.write(f"**年齢 / Age**: {profile['age']}")
            st.write(f"**出身国 / Country of Origin**: {profile['country']}")
            st.write(f"**趣味 / Hobby**: {profile['hobby']}")
            st.write(f"**学びたい言語 / Learning Language**: {profile['learning_language']}")
            st.write(f"**話せる言語 / Speaking Language**: {profile['speaking_language']}")
    else:
        st.warning("条件に合う登録者が見つかりませんでした。")
    
    # 戻るボタン
    if st.button("戻る / Back"):
        st.session_state.current_mode = "menu"


# イベント機能
# イベントを取得（ホスト情報も取得）
def fetch_events():
    events = supabase.table("event").select("*").execute().data
    profiles = supabase.table("profiles").select("id, name, country, hobby").execute().data

    # profilesを辞書にして検索を高速化
    profile_dict = {p["id"]: p for p in profiles}

    # 各イベントにホスト情報を追加
    for event in events:
        host = profile_dict.get(event["hostno"], {"name": "不明", "country": "不明", "hobby": "不明"})
        event["host_name"] = host["name"]
        event["host_country"] = host["country"]
        event["host_hobby"] = host["hobby"]
    
    return events

# イベント作成
def create_event(name, location, date, description, hostno):
    event_data = {
        "name": name,
        "location": location,
        "date": str(date),
        "description": description,
        "hostno": hostno,
    }
    response = supabase.table("event").insert(event_data).execute()
    return response.data

def delete_event(event_id):
    response = supabase.table("event").delete().eq("id", event_id).execute()
    if response.data:
        st.success("イベントが削除されました！")
    else:
        st.error("イベント削除に失敗しました。")


# Streamlit UI
def event_mode():
    st.title("イベント機能 / Event Features")
    menu = st.radio("イベントメニューを選択してください", ["イベント参加 / Join Event", "イベント作成 / Create Event"])

    if menu == "イベント参加 / Join Event":
        event_join_menu()
    elif menu == "イベント作成 / Create Event":
        event_create_menu()
    

def event_join_menu():
    st.subheader("イベント参加メニュー / Event Join Menu")
    search_keyword = st.text_input("キーワードで検索 / Search by keyword")

    events = fetch_events()
    filtered_events = [
        event for event in events
        if search_keyword.lower() in event["name"].lower() or search_keyword.lower() in event["description"].lower()
    ] if search_keyword else events

    if filtered_events:
        for event in filtered_events:
            st.write("---")
            st.write(f"**イベント名 / Event Name**: {event['name']}")
            st.write(f"**場所 / Location**: {event['location']}")
            st.write(f"**日時 / Date**: {event['date']}")
            st.write(f"**説明 / Description**: {event['description']}")
            st.write(f"**ホスト / Host**: {event['host_name']} ({event['host_country']} - {event['host_hobby']})")
            participants = event.get("participants", [])
            st.write(f"**参加者数 / Number of Participants**: {len(participants)}")

            if participants:
                st.write("**参加者プロフィール / Participant Profiles**:")
                
                for participant_id in participants:
                    # Supabaseから参加者情報を取得
                    participant_response = supabase.table("profiles").select("*").eq("id", participant_id).execute()
                    if participant_response.data:
                        participant = participant_response.data[0]
                        st.write(f"**名前 / Name**: {participant['name']}")
                        st.write(f"**学部 / Faculty**: {participant['faculty']}")
                        st.write(f"**出身国 / Country of Origin**: {participant['country']}")
                        st.write(f"**趣味 / Hobby**: {participant['hobby']}")
                        st.write("---") 
                    else:
                        st.write(f"プロフィール情報が見つかりませんでした (ID: {participant_id})。")


             # 参加ボタン
            if st.button(f"このイベントに参加する / Join this Event: {event['name']}", key=f"join_event_{event['id']}"):
                if st.session_state.profile:
                    participant_id = st.session_state.profile["id"]
                    if participant_id not in participants:
                        participants.append(participant_id)
                        
                        # 参加者リストを Supabase に保存
                        response = supabase.table("event").update({"participants": participants}).eq("id", event["id"]).execute()
                        if response.data:
                            st.success(f"イベント '{event['name']}' に参加しました！")
                        else:
                            st.error("イベント参加に失敗しました。")
                        # 参加後にプロフィール情報が表示されるように再描画
                        st.rerun()
                    else:
                        st.warning("既にこのイベントに参加しています。")
                else:
                    st.error("まずプロフィールを登録してください。")

            # イベント作成者（ホスト）のみ削除ボタンを表示
            if st.session_state.profile and st.session_state.profile["id"] == event["hostno"]:
                if st.button(f"このイベントを削除 / Delete this Event: {event['name']}", key=f"delete_event_{event['id']}"):
                    delete_event(event["id"])
            # イベントごとに区切り線を追加
            st.write("---")
    else:
        st.warning("該当するイベントが見つかりませんでした。")

    if st.button("戻る / Back"):
        st.session_state.current_mode = "menu"
        st.rerun()

def event_create_menu():
    st.subheader("イベント作成メニュー / Event Creation Menu")
    name = st.text_input("イベント名 / Event Name")
    location = st.text_input("場所 / Location")
    date = st.date_input("日時 / Date")
    description = st.text_area("イベントの説明 / Event Description")

    if st.button("イベントを作成 / Create Event"):
        if st.session_state.profile:
            new_event = create_event(name, location, date, description, st.session_state.profile["id"])
            if new_event:
                st.success(f"イベント '{name}' を作成しました！")
                st.session_state.current_mode = "menu"  # メニュー画面に戻るように変更
                st.rerun()  # 画面を即座に更新
        else:
            st.error("まずプロフィールを登録してください。")
        if st.button("戻る / Back"):
          st.session_state.current_mode = "menu"
          st.rerun()  # 画面を即座に更新



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
elif st.session_state.current_mode == "auth":
        auth()
