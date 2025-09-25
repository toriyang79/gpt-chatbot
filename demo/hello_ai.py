# 1. 필요한 것들 가져오기
from openai import OpenAI
import os
from dotenv import load_dotenv

# 2. API 키 로드
load_dotenv()

# 3. OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 4. AI에게 인사하기
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "안녕하세요."}
    ]
)

# 5. 응답 출력
print(response.choices[0].message.content)
# 응답 객체 자세히 보기
print("전체 응답 구조:")
print(f"모델: {response.model}")
print(f"토큰 사용량: {response.usage.total_tokens}")
print(f"응답 내용: {response.choices[0].message.content}")
