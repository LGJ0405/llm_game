import streamlit as st
import json
from story_functions import story_structure, final_scenario

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
st.set_page_config(page_title="LLM Storyteller", layout="wide")

st.title("📖 LLM Storyteller")

# 시나리오 구조 생성
with st.form("structure_form"):
    st.header("시나리오 구조 생성")
    col1, col2 = st.columns(2)
    with col1:
        theme_input = st.text_input(
            "🎭 테마를 입력하세요 (예: 복수, 사랑, 모험)",
            value=st.session_state.get("theme", "")
        )
    with col2:
        background_input = st.text_input(
            "🌍 배경을 입력하세요 (예: 중세, 사이버펑크, 현대)",
            value=st.session_state.get("background", "")
        )

    submitted = st.form_submit_button("시나리오 구조 생성")
    if submitted:
        if not theme_input or not background_input:
            st.warning("테마와 배경을 모두 입력하세요!")
        else:
            st.session_state["final_ready"] = False

            st.session_state["cuts"] = []
            with st.spinner("시나리오 구조를 생성 중입니다... 잠시만 기다려주세요"):
                json_response = story_structure(theme_input, background_input)
            st.session_state["story_structure"] = json_response

            characters = '\n'.join([f"\t{i+1}. {name}" for i, name in enumerate(json_response['characters'])])
            settings = '\n'.join([f"\t{i+1}. {s}" for i, s in enumerate(json_response['settings'])])
            objects = '\n'.join([f"\t{i+1}. {o}" for i, o in enumerate(json_response['objects'])])
            st.session_state["structure_text"] = (f'''시나리오 엔딩은 다음과 같습니다:\n\t"{json_response["ending"]}"
등장인물: \n{characters}
장소: \n{settings}
사용 가능한 매개체: \n{objects}
{json_response["max_cuts"]}컷 이내로 시나리오 뼈대를 작성해보세요.
한 컷에는 1~2명의 등장인물, 1개의 장소, 0~2개의 오브젝트를 사용하세요.''')

col_left, col_right = st.columns([3,7])

with col_left:
    if "structure_text" in st.session_state:
        st.subheader("📝 생성된 시나리오 구조")
        st.text(st.session_state["structure_text"])

with col_right:
    if "story_structure" in st.session_state:
        structure = st.session_state["story_structure"]
        max_cuts = structure["max_cuts"]

        col_header, col_add, col_remove = st.columns([5,2,2])
        with col_header:
            st.subheader("🎬 컷별 선택")
        with col_add:
            if st.button("➕컷 추가"):
                if len(st.session_state.cuts) < max_cuts:
                    st.session_state.cuts.append(
                        {"character": [], "setting": structure["settings"][0], "object": []}
                    )
                else:
                    st.warning(f"⚠ 최대 컷 수({max_cuts})를 초과할 수 없습니다!")
        with col_remove:
            if st.button("➖컷 제거"):
                if len(st.session_state.cuts) > 2:
                    st.session_state.cuts.pop()
                else:
                    st.warning("⚠ 최소 컷 수는 2입니다!")

        # cuts 초기화
        if "cuts" not in st.session_state or len(st.session_state.cuts) < 2:
            st.session_state.cuts = [
                {"character": [], "setting": structure["settings"][0], "object": []} for _ in range(max_cuts - 2)
            ]

        # 컷별 선택
        for i, cut in enumerate(st.session_state.cuts):
            st.markdown(f"### {i+1}컷 선택")
            col1, col2, col3 = st.columns(3)
            with col1:
                char = st.multiselect(
                    f"등장인물 (1~2명)",
                    structure["characters"],
                    key=f"char_{i}"
                )
            with col2:
                setting = st.selectbox(
                    f"장소",
                    structure["settings"],
                    index=structure["settings"].index(cut.get("setting", structure["settings"][0])),
                    key=f"set_{i}"
                )
            with col3:
                objs = st.multiselect(
                    f"오브젝트 (0~2개)",
                    structure["objects"],
                    key=f"obj_{i}"
                )

            st.session_state.cuts[i] = {"characters": char, "settings": setting, "objects": objs}

        if st.button("최종 시나리오 생성"):
            errors = []
            for i, cut in enumerate(st.session_state.cuts, start=1):
                if not (1 <= len(cut["characters"]) <= 2):
                    errors.append(f"{i}컷: 등장인물은 1~2명이어야 합니다.")
                if not (0 <= len(cut["objects"]) <= 2):
                    errors.append(f"{i}컷: 오브젝트는 0~2개이어야 합니다.")

            if errors:
                st.error("🚨 입력 조건을 확인하세요:\n" + "\n".join(errors))
            else:
                with st.spinner("최종 시나리오 생성 중입니다... 잠시만 기다려주세요"):
                    st.session_state["final_story"] = final_scenario(
                        st.session_state["story_structure"], st.session_state["cuts"]
                    )
                st.session_state["final_ready"] = True

if st.session_state.get("final_ready", False):
    final_story = st.session_state["final_story"]

    st.subheader("🎉 최종 시나리오")

    for cut_text in final_story["final_scenario"]:
        st.markdown(f"""
        <div style="
            background-color:#f9f9f9;
            padding:15px;
            border-radius:10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            margin-bottom:10px;
            font-weight:bold;">
            {cut_text}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background-color:#e0f7fa;
        padding:15px;
        border-radius:10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        font-weight:bold;">
        📝 최종 엔딩: {final_story['ending']}
    </div>
    """, unsafe_allow_html=True)

    if final_story["status"] == "success":
        st.success("✅ 성공적인 스토리 텔링입니다!")
    else:
        st.warning("⚠ 재도전 해보세요!")