from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def stream_response(prompt):
    """스트리밍으로 응답 받기"""

    # stream=True 옵션 추가
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True  # 🌟 핵심: 스트리밍 활성화
    )

    # 청크(조각)별로 출력
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end='', flush=True)
    print()  # 줄바꿈

# 테스트
print("🤖 AI: ", end='')
stream_response("파이썬의 장점 3가지를 알려주세요")
