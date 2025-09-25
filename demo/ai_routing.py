#AI로 하여금 질문 내용에 따라서 고급인지 아닌지 판단하면 됩니다.
from openai import OpenAI
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_routing(question):
    messages = [{"role": "user", "content": question}]
    messages.append({"role": "system", "content": "당신은 고급인지 아닌지 판단하는 전문가입니다. 질문 내용에 따라서 고급인지 아닌지 판단해주세요.질문에 대한 답변은 하지 않습니다."})
    response = client.chat.completions.create(
        model="gpt-4o-mini",          # ★ 추가: 어떤 모델 쓸지 지정
        messages=messages,            # ★ 추가: messages 전달
        temperature=0                 # (선택) 일관성 위해 0
    )
    return response.choices[0].message.content  # ★ return은 함수 호출 '다음 줄'에

output = ai_routing("한국의 AI산업의 발전을 위해서 정부의 각 부처에서 준비하고 실행해야 할 내용은 뭐야?라는 질문은 고급인가요")
print(output)
