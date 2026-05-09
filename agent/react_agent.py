from langchain.agents import create_agent
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
                                     fetch_external_data, fill_context_for_report)
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
                   fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query, session_id=None):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        context = {
            "report": False,
            "session_id": session_id,
        }
        for chunk in self.agent.stream(input_dict, stream_mode="values", context=context):
            latest_message = chunk["messages"][-1]  # 有历史记录所以取最后一条
            if latest_message.content:
                yield latest_message.content.strip() + "\n"

if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成一份报告"):
        print(chunk,end="",flush=True)
