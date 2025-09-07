from openai import OpenAI
import json

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

# 스토리의 구조 생성
def story_structure(theme='복수', background='중세'):
    content = f'''
당신은 창의적이고 논리적인 판타지 스토리 시나리오 전문가입니다.

요청 사항:
1. 입력된 테마와 배경을 바탕으로 결말을 창의적으로 만들어주세요.
단, 간결하게 15자 이내로 간결하게 작성하세요.
2. 결말을 표현하기 위해 필요한 인물, 배경, 매개체를 추천해주세요.
단, 배경은 최소 max_cuts - 2 이상으로 만드세요.
- characters: 스토리에 등장할 캐릭터  
- settings: 장소나 환경  
- objects: 사건에 중요한 오브젝트나 도구, 예를 들어 독약과 독을 탈 술잔, 함정용 도구 등 반드시 포함
3. 결말과 스토리 흐름을 자연스럽게 표현할 수 있는 최대 컷 수(max_cuts)를 결정해주세요.
4. 출력은 반드시 JSON 형식으로 작성하고, 키는 반드시 지정된 명칭으로 사용하세요.
'''\
'''예시 출력:{
    "ending": "기사가 왕위를 강탈한다",
    "characters": ["기사", "왕", "왕비"],
    "settings": ["연회장", "왕좌의 방"],
    "objects": ["술잔", "독약", "왕관"],
    "max_cuts": 5
}'''

    user_input = f"테마: {theme}, 배경: {background}"

    messages = [{"role": "system", "content": content},
                {"role": "user", "content": user_input}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format = { "type": "json_object" },
        temperature=0.8,
        max_tokens=512,
        top_p=1
    )
    return json.loads(response.choices[0].message.content)

# 최종 시나리오 작성
def final_scenario(json_response, scenario_templates):
    content = f'''
당신은 창의적이고 논리적인 판타지 스토리 시나리오 전문가입니다.
플레이어가 입력한 컷별 구성을 바탕으로 스토리를 만들어주세요.

스토리 엔딩:
"{json_response['ending']}"

전체 등장인물: {json_response['characters']}
전체 장소: {json_response['settings']}
전체 매개체: {json_response['objects']}

요청 사항:
1. 각 컷은 짧고 핵심만 담은 한 문장(15자 이내)으로 작성하세요.
2. 컷의 흐름은 앞뒤 컷의 내용, 엔딩과 자연스럽게 연결되도록 서술하세요.
3. 선택된 컷으로 엔딩 도달이 가능하면 기존 엔딩을 사용하세요.
4. 불가능하면 새로운 엔딩을 제안하고, 새로운 엔딩으로 가는 시나리오를 작성하세요.
   - 새로운 엔딩 작성 시 플레이어에게 재도전을 권유하세요.
5. 출력은 반드시 JSON 형식으로 작성하고, 키는 반드시 지정된 명칭으로 사용하세요.
'''\
'''예시 출력:{
    "status": "success" or "retry",
    "final_scenario": ["1컷: 전투장에서 복수자와 배신자가 맞선다.", "2컷: 왕의 방에서 배신자는 왕을 속인다."],
    "ending": "<최종 엔딩>"
}'''

    user_content = "컷별 구성은 아래와 같습니다.\n"
    for i, cut in enumerate(scenario_templates, 1):
        user_content += f"{i}컷: 등장인물 {cut['characters']}, 장소 {cut['settings']}, 매개체 {cut['objects']}\n"


    messages = [{"role": "system", "content": content},
                {"role": "user", "content": user_content}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format = { "type": "json_object" },
        temperature=0.8,
        max_tokens=4096,
        top_p=1
    )

    return json.loads(response.choices[0].message.content)