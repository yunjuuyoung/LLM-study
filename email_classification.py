from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv('API_KEY'))

# 분석할 메일
email_content = """
제목: [긴급] 프로젝트 마감일 변경 안내
발신자: 김과장 <manager.kim@company.com>

안녕하세요 개발팀 여러분,

다음 주 금요일로 예정되어 있던 모바일 앱 프로젝트 마감일이 
이번 주 수요일로 앞당겨졌습니다.

클라이언트 측 요청으로 인한 변경사항이며, 
추가 작업이 필요한 부분이 있으시면 오늘 오후 5시까지 
공유 부탁드립니다.

내일 오전 10시에 긴급 회의를 진행하겠습니다.
참석 가능 여부를 회신해 주세요.

감사합니다.
김과장 드림
"""

def classification_email(article_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": """이메일을 분석해서 다음 JSON 형태로 응답해주세요.

반드시 다음 구조를 정확히 따라주세요:
- category: 업무/개인/스팸/마케팅/알림 중 하나
- priority: high/medium/low 중 하나
- action_required: reply_needed/read_only/archive 중 하나
- sentiment: positive/negative/neutral 중 하나
- keywords: ["키워드1", "키워드2", "키워드3"] 중요한 키워드를 세 개로 나열
- summary: 이메일 내용 요약 (1-2문장)

다른 필드는 추가하지 마세요."""
            },
            {"role": "system", "content": f"다음 email 내용을 분석해주세요:\n\n{article_text}"}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "classification_email",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["업무", "개인", "스팸", "마케팅", "알림"]
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"]
                        },
                        "action_required": {
                            "type": "string",
                            "enum": ["reply_needed", "read_only", "archive"]
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["positive", "negative", "neutral"]
                        },
                        "keywords": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "summary": {
                            "type": "string"
                        }
                    },
                    "required": ["category", "priority", "action_required", "sentiment", "keywords", "summary"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    return response.choices[0].message.content

# 이메일 분석 실행
print("이메일 분석 중...")
result = classification_email(email_content)

# JSON 파싱해서 활용
import json
from pprint import pprint
data = json.loads(result)

print("\n=== JSON 구조 확인 ===")
pprint(data)

print("\n=== 분석 결과 요약 ===")
print(f"분류: {data['category']}")
print(f"중요도: {data['priority']}")
print(f"상태: {data['action_required']}")
print(f"감정: {data['sentiment']}")
print("\n키워드:")
for i, fact in enumerate(data['keywords'], 1):
    print(f"{i}. {fact}")
print(f"내용: {data['summary']}")
