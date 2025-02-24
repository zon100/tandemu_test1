import streamlit as st
import uuid  # 一意のIDを生成するためのモジュール
import pandas as pd  # データ保存用
import os
import psycopg2
from supabase import create_client, Client



# SupabaseのURLとキー（環境変数で管理するのが望ましい）
SUPABASE_URL = "https://zancatjxgdofhxlemcgf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphbmNhdGp4Z2RvZmh4bGVtY2dmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk5MDQyNDQsImV4cCI6MjA1NTQ4MDI0NH0.FeLkr0k_WSLXGQFtU2PyKMhMS_Zywbzb_FSTAIOsjsk"

# Supabaseクライアントの作成
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



# プロフィールをSupabaseに保存
def save_profile_to_supabase(profile):
    email = profile.get("email")  # 入力されたメールアドレスを取得
    table_name = "profiles" if profile["type"] == "Japanese" else "profiles_exchange_students"

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
def auth():
    st.title("ログイン / 新規登録")
    choice = st.radio("選択してください", ["ログイン", "新規会員登録"])
    
    if choice == "ログイン":
        email = st.text_input("メールアドレス")
        username = st.text_input("ユーザーネーム")
        if st.button("ログイン"):
            response = supabase.table("profiles").select("*").eq("email", email).eq("name", username).execute()
            if response.data:
                st.session_state.profile = response.data[0]
                st.session_state.user_id = response.data[0]["id"]
                st.session_state.current_mode = "menu"
                st.success("ログイン成功！")
            else:
                st.error("ユーザーが見つかりません。")
    
    elif choice == "新規会員登録":
        if st.button("次へ"):
            st.session_state.current_mode = "home"


# ホーム画面
def home():
    st.title("留学生と大学生のマッチングアプリ")
    st.write("日本人または留学生を選択してください。（Please choose whether you are Japanese or an exchange student.）")
    user_type = st.radio("あなたはどちらですか？", ["Japanese", "Exchange Student"])
    
    if st.button("次へ"):
        st.session_state.user_type = user_type
        st.session_state.current_mode = "profile"

# プロフィール入力画面
def profile_input():
    st.title("プロフィール入力")
    profile = st.session_state.profile or {"id": str(uuid.uuid4())}

    if st.session_state.user_type == "Japanese":
        st.subheader("英語で入力してください")
         # 注意事項を追加
        st.warning("**注意: 名前はローマ字、他の項目は英語で記入してください。**")
        profile["type"] = "Japanese"
        profile["name"] = st.text_input("名前")
        profile["faculty"] = st.text_input("学部")
        profile["age"] = st.number_input("年齢", min_value=0, max_value=100, step=1)
        profile["target_country"] = st.text_input("行きたい国")
        profile["hobby"] = st.text_input("趣味")
        profile["learning_language"] = st.text_input("学びたい言語")  # 追加
        profile["speaking_language"] = st.text_input("話せる言語")  # 追加
    else:
        st.subheader("Please fill in your information in English")
        profile["type"] = "Exchange Student"
        profile["name"] = st.text_input("Name")
        profile["faculty"] = st.text_input("Faculty")
        profile["age"] = st.number_input("age", min_value=0, max_value=100, step=1)
        profile["country"] = st.text_input("Country of origin")
        profile["hobby"] = st.text_input("Hobby")
        profile["learning_language"] = st.text_input("Learning Language")  # 追加
        profile["speaking_language"] = st.text_input("Speaking Language")  # 追加

    profile["email"] = st.text_input("Email Address")

    if st.button("プロフィールを登録"):
        # プロフィール保存処理
        if not any(p["id"] == profile["id"] for p in st.session_state.all_profiles):
            st.session_state.all_profiles.append(profile)
        else:
            st.session_state.all_profiles = [p if p["id"] != profile["id"] else profile for p in st.session_state.all_profiles]

        st.session_state.profile = profile
        save_profile_to_supabase(profile)  # Supabaseに保存
        st.success("プロフィールが登録されました！")
        st.session_state.current_mode = "menu"

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
    """メッセージの送信相手を選択する画面"""
    st.title("メッセージモード")
    st.write("チャットしたい相手を選んでください。")

    # 自分のプロフィール取得
    if not st.session_state.get("profile"):
        st.error("まずプロフィールを登録してください。")
        if st.button("戻る"):
            st.session_state.current_mode = "menu"
        return

    user_profile = st.session_state.profile
    user_id = user_profile["id"]

    # 他のユーザー一覧を取得
    profiles_jp = supabase.table("profiles").select("id, name, type").execute()
    profiles_ex = supabase.table("profiles_exchange_students").select("id, name, type").execute()
    all_profiles = (profiles_jp.data or []) + (profiles_ex.data or [])
    
    recipients = [p for p in all_profiles if p["id"] != user_id]
    
    if not recipients:
        st.warning("現在メッセージを送信できるユーザーがいません。")
        if st.button("戻る"):
            st.session_state.current_mode = "menu"
        return

    # ユーザー選択
    selected_user = st.selectbox("チャット相手を選択してください", recipients, format_func=lambda p: f"{p['name']} ({p['type']})")
    
    if st.button("チャット開始"):
        st.session_state["chat_partner"] = selected_user
        st.session_state.current_mode = "chat"
        st.rerun()
    # メニューに戻るボタン（追加）
    if st.button("戻る"):
        st.session_state.current_mode = "menu"
        st.rerun()


def chat_screen():
    """選択したユーザーとのチャット画面"""
    st.title("チャット画面")

    # 自分のプロフィール取得
    if not st.session_state.get("profile"):
        st.error("まずプロフィールを登録してください。")
        if st.button("戻る"):
            st.session_state.current_mode = "menu"
        return

    user_profile = st.session_state.profile
    user_id = user_profile["id"]
    chat_partner = st.session_state.get("chat_partner")

    if not chat_partner:
        st.warning("チャット相手が選択されていません。")
        if st.button("戻る"):
            st.session_state.current_mode = "message"
        return

    st.subheader(f"チャット相手: {chat_partner['name']} ({chat_partner['type']})")

    # メッセージ履歴の取得（送受信両方）
    messages = supabase.table("messages").select("from_user, to_user, message, timestamp") \
    .or_(f"and(from_user.eq.{user_id},to_user.eq.{chat_partner['id']}),and(from_user.eq.{chat_partner['id']},to_user.eq.{user_id})") \
    .order("timestamp", desc=False).execute()


    # メッセージを表示
    st.write("### メッセージ履歴")
    if messages.data:
        for msg in messages.data:
            sender = "あなた" if msg["from_user"] == user_id else chat_partner["name"]
            st.write(f"**{sender}**: {msg['message']} ({msg['timestamp']})")
    else:
        st.info("まだメッセージがありません。")

    # メッセージ送信フォーム
    message = st.text_area("メッセージを入力してください")
    if st.button("送信"):
        if message.strip():
            message_data = {
                "id": str(uuid.uuid4()),
                "from_user": user_id,
                "to_user": chat_partner["id"],
                "message": message,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            supabase.table("messages").insert(message_data).execute()
            st.success("メッセージを送信しました！")
            st.rerun()  # 送信後に再読み込み
  # 送信後に再読み込み
        else:
            st.error("メッセージを入力してください。")

    # 戻るボタン
    if st.button("戻る"):
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
    # Supabaseから登録者一覧を取得
    def load_profiles_from_supabase():
       japanese_profiles = supabase.table("profiles").select("*").execute()
       exchange_profiles = supabase.table("profiles_exchange_students").select("*").execute()

    # 取得したデータを `st.session_state.all_profiles` に格納
       st.session_state.all_profiles = (japanese_profiles.data or []) + (exchange_profiles.data or [])

# アプリ起動時に実行
    if "all_profiles" not in st.session_state or not st.session_state.all_profiles:
       load_profiles_from_supabase()

    if st.session_state.user_type == "Exchange Student":
        st.title("Search Mode")
        search_hobby = st.text_input("Search by Hobby")
        search_target_country = st.text_input("Search by Target Country")
        search_learning_language = st.text_input("Search by Learning Language")  # 追加
        search_speaking_language = st.text_input("Search by Speaking Language")  # 追加
        st.write("Registered Users:")
    else:
        st.title("人探しモード")
        search_hobby = st.text_input("趣味で検索")
        search_target_country = st.text_input("行きたい国で検索")
        search_learning_language = st.text_input("学びたい言語で検索")  # 追加
        search_speaking_language = st.text_input("話せる言語で検索")  # 追加
        st.write("登録者一覧:")

    filtered_profiles = []
    for profile in st.session_state.all_profiles:
        match_hobby = search_hobby.lower() in profile.get("hobby", "").lower() if search_hobby else True
        match_country = (
            search_target_country.lower() in profile.get("target_country", "").lower() or
            search_target_country.lower() in profile.get("country", "").lower()
            if search_target_country else True
        )
        match_learning_language = (
            search_learning_language.lower() in profile.get("learning_language", "").lower()
            if search_learning_language else True
        )
        match_speaking_language = (
            search_speaking_language.lower() in profile.get("speaking_language", "").lower()
            if search_speaking_language else True
        )
        if match_hobby and match_country and match_learning_language and match_speaking_language:
            filtered_profiles.append(profile)

    if filtered_profiles:
        for profile in filtered_profiles:
            st.write("---")
            st.write(f"**Type**: {profile['type']}")
            st.write(f"**Name**: {profile['name']}")
            st.write(f"**Faculty**: {profile['faculty']}")
            if profile["type"] == "Japanese":
                st.write(f"**Age**: {profile['age']}")
                st.write(f"**Target Country**: {profile['target_country']}")
            else:
                st.write(f"**Country of Origin**: {profile['country']}")
            st.write(f"**Hobby**: {profile['hobby']}")
            st.write(f"**Learning Language**: {profile['learning_language']}")
            st.write(f"**Speaking Language**: {profile['speaking_language']}")
    else:
        st.warning("No users found matching the criteria." if st.session_state.user_type == "Exchange Student" else "条件に合う登録者が見つかりませんでした。")

    if st.button("Back" if st.session_state.user_type == "Exchange Student" else "戻る"):
        st.session_state.current_mode = "menu"

# イベント機能
# イベント機能
def event_mode():
    if st.session_state.user_type == "Exchange Student":
        st.title("Event Features")
        menu = st.radio("Select Event Menu", ["Join Event", "Create Event"])
    else:
        st.title("イベント機能")
        menu = st.radio("イベントメニューを選択してください", ["イベント参加", "イベント作成"])
    
    if menu == ("Join Event" if st.session_state.user_type == "Exchange Student" else "イベント参加"):
        event_join_menu()
    elif menu == ("Create Event" if st.session_state.user_type == "Exchange Student" else "イベント作成"):
        event_create_menu()
# プロフィール表示関数
def show_profile(participant):
    st.write("---")
    st.write(f"**Name**: {participant['name']}")
    st.write(f"**Faculty**: {participant['faculty']}")
    if participant["type"] == "Exchange Student":
        st.write(f"**Country of Origin**: {participant['country']}")
    else:
        st.write(f"**Target Country**: {participant['target_country']}")
    st.write(f"**Hobby**: {participant['hobby']}")
    

# イベント参加メニュー
def event_join_menu():
    if st.session_state.user_type == "Exchange Student":
        st.subheader("Event Join Menu")
        search_keyword = st.text_input("Search by keyword")
        filtered_events = [
            event for event in st.session_state.events
            if search_keyword.lower() in event["name"].lower() or search_keyword.lower() in event["description"].lower()
        ] if search_keyword else st.session_state.events
    else:
        st.subheader("イベント参加メニュー")
        search_keyword = st.text_input("キーワードで検索")
        filtered_events = [
            event for event in st.session_state.events
            if search_keyword.lower() in event["name"].lower() or search_keyword.lower() in event["description"].lower()
        ] if search_keyword else st.session_state.events

    if filtered_events:
        for event in filtered_events:
            st.write("---")
            if st.session_state.user_type == "Exchange Student":
                st.write(f"**Event Name**: {event['name']}")
                st.write(f"**Location**: {event['location']}")
                st.write(f"**Date**: {event['date']}")
                st.write(f"**Description**: {event['description']}")
                st.write(f"**Host**: {event['host']}")
                st.write(f"**Number of Participants**: {len(event['participants'])}")
                if event["participants"]:
                 st.write("**Participant Profiles**:" if st.session_state.user_type == "Exchange Student" else "**参加者プロフィール**:")
                for participant_id in event["participants"]:
                    # 参加者のプロフィールを探して表示
                    participant = next(p for p in st.session_state.all_profiles if p["id"] == participant_id)
                    st.write(f"**Name**: {participant['name']}")
                    st.write(f"**Faculty**: {participant['faculty']}")
                    if st.session_state.user_type == "Exchange Student":
                        st.write(f"**Country of Origin**: {participant['country']}")
                    else:
                        st.write(f"**Target Country**: {participant['target_country']}")
                    st.write(f"**Hobby**: {participant['hobby']}")

                    # プロフィールを表示するボタン
                    if st.button(f"View Profile: {participant['name']}", key=f"view_profile_{participant_id}"):
                        show_profile(participant)  # プロフィール表示関数


        
                if st.button(f"Join this Event: {event['name']}", key=f"join_event_{event['id']}"):
                    if st.session_state.profile:
                        if st.session_state.profile["id"] not in event["participants"]:
                            event["participants"].append(st.session_state.profile["id"])
                            st.success(f"You have joined the event '{event['name']}'!")
                        else:
                            st.warning("You are already a participant of this event.")
                    else:
                        st.error("Please register your profile first.")
            else:
                st.write(f"**イベント名**: {event['name']}")
                st.write(f"**場所**: {event['location']}")
                st.write(f"**日時**: {event['date']}")
                st.write(f"**説明**: {event['description']}")
                st.write(f"**ホスト**: {event['host']}")
                st.write(f"**参加者数**: {len(event['participants'])}")
                if event["participants"]:
                 st.write("**参加者プロフィール**:")
                for participant_id in event["participants"]:
                    # 参加者のプロフィールを探して表示
                    participant = next(p for p in st.session_state.all_profiles if p["id"] == participant_id)
                    st.write(f"**Name**: {participant['name']}")
                    st.write(f"**Faculty**: {participant['faculty']}")
                    if st.session_state.user_type == "Exchange Student":
                        st.write(f"**Country of Origin**: {participant['country']}")
                    else:
                        st.write(f"**Target Country**: {participant['target_country']}")
                    st.write(f"**Hobby**: {participant['hobby']}")

                    # プロフィールを表示するボタン
                    if st.button(f"プロフィールを見る: {participant['name']}", key=f"view_profile_{participant_id}"):
                        show_profile(participant)  # プロフィール表示関数
                if st.button(f"このイベントに参加する: {event['name']}", key=f"join_event_{event['id']}"):
                    if st.session_state.profile:
                        if st.session_state.profile["id"] not in event["participants"]:
                            event["participants"].append(st.session_state.profile["id"])
                            st.success(f"イベント '{event['name']}' に参加しました！")
                        else:
                            st.warning("既にこのイベントに参加しています。")
                    else:
                        st.error("まずプロフィールを登録してください。")
                # イベント削除ボタン（ホストのみ表示）
            if event["host"] == (st.session_state.profile["name"] if st.session_state.profile else "不明"):
                if st.button(
                    f"このイベントを削除: {event['name']}" if st.session_state.user_type != "Exchange Student" else f"Delete this Event: {event['name']}",
                    key=f"delete_event_{event['id']}"
                ):
                    st.session_state.events = [e for e in st.session_state.events if e["id"] != event["id"]]
                    st.success(f"イベント '{event['name']}' を削除しました！" if st.session_state.user_type != "Exchange Student" else f"Successfully deleted the event: '{event['name']}'!")
    else:
        if st.session_state.user_type == "Exchange Student":
            st.warning("No matching events were found.")
        else:
            st.warning("該当するイベントが見つかりませんでした。")

    if st.button("Back" if st.session_state.user_type == "Exchange Student" else "戻る"):
        st.session_state.current_mode = "menu"

# イベント作成メニュー
def event_create_menu():
    if st.session_state.user_type == "Exchange Student":
        st.subheader("Event Creation Menu")
        name = st.text_input("Event Name")
        location = st.text_input("Location")
        date = st.date_input("Date")
        description = st.text_area("Description")
    else:
        st.subheader("イベント作成メニュー")
        name = st.text_input("イベント名")
        location = st.text_input("場所")
        date = st.date_input("日時")
        description = st.text_area("イベントの説明")

    if st.button("Create Event" if st.session_state.user_type == "Exchange Student" else "イベントを作成"):
        st.session_state.current_mode = "menu"
        if name and location and description:
            new_event = {
                "id": str(uuid.uuid4()),
                "name": name,
                "location": location,
                "date": str(date),
                "description": description,
                "host": st.session_state.profile["name"] if st.session_state.profile else ("Unknown" if st.session_state.user_type == "Exchange Student" else "不明"),
                "participants": []
            }
            st.session_state.events.append(new_event)
            if st.session_state.user_type == "Exchange Student":
                st.success(f"Event '{name}' has been created!")
            else:
                st.success(f"イベント '{name}' を作成しました！")

        else:
            if st.session_state.user_type == "Exchange Student":
                st.error("Please fill in all fields.")
            else:
                st.error("すべてのフィールドを入力してください。")

    if st.button("Back" if st.session_state.user_type == "Exchange Student" else "戻る"):
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
elif st.session_state.current_mode == "auth":
        auth()
