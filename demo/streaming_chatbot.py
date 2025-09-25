from openai import OpenAI
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class StreamingChatbot:
    """스트리밍 응답을 지원하는 챗봇"""

    def __init__(self):
        self.messages = [
            {"role": "system", "content": "당신은 친절한 AI 도우미입니다."}
        ]

    def typing_effect(self, text, delay=0.1):
        """타이핑 효과 (선택사항)"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)

    def stream_chat(self, user_input):
        """스트리밍으로 대화"""
        # 사용자 메시지 추가
        self.messages.append({"role": "user", "content": user_input})

        # 스트리밍 응답
        print("🤖 AI: ", end='')

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            stream=True,
            temperature=0.9
        )

        # 전체 응답 저장용
        full_response = ""

        try:
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content

            print("\n")  # 응답 끝나면 줄바꿈

            # 대화 기록에 저장
            self.messages.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            print("\n\n⚠️ 응답이 중단되었습니다.")

        return full_response

    def run(self):
        """챗봇 실행"""
        print("=" * 50)
        print("🌊 스트리밍 AI 챗봇")
        print("명령어: quit(종료), clear(초기화)")
        print("=" * 50)

        while True:
            try:
                user_input = input("👤 You: ")

                if user_input.lower() == 'quit':
                    print("👋 안녕히 가세요!")
                    break

                elif user_input.lower() == 'clear':
                    self.messages = [self.messages[0]]  # system 메시지만 유지
                    print("✨ 대화가 초기화되었습니다.\n")
                    continue

                # 스트리밍 응답
                self.stream_chat(user_input)

            except Exception as e:
                print(f"\n❌ 오류: {e}\n")

# 실행
if __name__ == "__main__":
    bot = StreamingChatbot()
    bot.run()
