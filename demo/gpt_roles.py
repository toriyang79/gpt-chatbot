# 필요한 라이브러리 임포트
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 3. OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 예시: 역할별 차이
def test_roles():
    # 1. system 역할 없이
    response1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "재봉틀 추천해주세요?"}
        ]
    )
    print("기본 응답:", response1.choices[0].message.content)

    # 2. system 역할 추가
    response2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 재봉틀 고수로서 재봉에 관한 모든 답을 할 수 있습니다."},
            {"role": "user", "content": "재봉틀 추천해주세요?"}
        ]
    )
    print("재봉고수 응답:", response2.choices[0].message.content)

test_roles()
