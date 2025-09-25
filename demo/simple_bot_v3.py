# simple_bot_v3.py
from openai import OpenAI
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def save_conversation(messages):
    """대화 내용을 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"💾 대화가 {filename}에 저장되었습니다.")

def main():
    messages = []
    print("🤖 AI 챗봇 (종료: quit, 저장: save)")
    print("-" * 40)

    while True:
        user_input = input("👤 You: ")

        if user_input == 'quit':
            print("👋 안녕히 가세요!")
            break
        elif user_input == 'save':
            save_conversation(messages)
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            ai_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": ai_response})

            print(f"🤖 AI: {ai_response}")
            print()

        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
