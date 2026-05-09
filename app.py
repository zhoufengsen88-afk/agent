import time

import streamlit as st
from agent.react_agent import ReactAgent
from agent.tools.agent_tools import get_current_month, get_user_id
from utils.db_handler import safe_create_chat_session, safe_save_chat_message, safe_save_report_record

st.title("智扫通机器人智能客服")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，我是智扫通机器人智能客服，请问有什么可以帮助你？"}]

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "user_id" not in st.session_state:
    st.session_state["user_id"] = get_user_id.invoke({})

if "session_id" not in st.session_state:
    st.session_state["session_id"] = safe_create_chat_session(st.session_state["user_id"])

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 在页面最下方提供用户输入栏
prompt = st.chat_input()

if prompt:
    # 在页面输出用户的提问
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})
    safe_save_chat_message(st.session_state["session_id"], "user", prompt)

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt, st.session_state["session_id"])

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)

                for char in chunk:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        assistant_content = "".join(response_messages).strip()
        if assistant_content:
            st.session_state["message"].append({"role": "assistant", "content": assistant_content})
            safe_save_chat_message(st.session_state["session_id"], "assistant", assistant_content)
            if "扫地机器人使用情况报告与保养建议" in assistant_content:
                safe_save_report_record(
                    st.session_state["user_id"],
                    get_current_month.invoke({}),
                    assistant_content,
                    f"DEV-{st.session_state['user_id']}-001",
                )
        st.rerun()
# cd C:\Users\19923\Desktop\Agent项目工程
# streamlit run app.py
