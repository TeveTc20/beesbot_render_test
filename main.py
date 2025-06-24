import os
import json
import datetime
import re
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain.agents import tool, create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from operator import add as add_messages


load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

def extract_country(text: str) -> str:
    text_lower = text.lower()
    for country in pycountry.countries:
        if country.name.lower() in text_lower:
            return country.name
    return ""

def normalize_text(text):
    # Lowercase and remove punctuation for easier matching
    return re.sub(r'[^\w\s]', '', text.lower())

def extract_destination(text: str) -> str:
    countries = [country.name for country in pycountry.countries]
    text_norm = normalize_text(text)
    found = []

    for country in countries:
        if country.lower() in text_norm:
            found.append(country)

    if found:
        return found[-1]  # Last country mentioned

    return ""


def extract_nationality(text: str) -> str:
    text_lower = text.lower()
    for country in pycountry.countries:
        # Check for plural or adjective forms? For simplicity, just match country name.
        # You can add mapping for adjectives like "Israelis" => "Israel"
        if country.name.lower() in text_lower:
            return country.name
    return ""

@tool
def visa_required(query: str) -> str:
    """
    This tool gives information about visa requirements for a nationality.
    It scrapes the Passport Index website for the nationality's visa info.
    """
    nationality = extract_nationality(query)
    if not nationality:
        return "Sorry, I couldn't identify your nationality country from the query."

    url = f"https://www.passportindex.org/passport/{nationality.lower()}/"

    return nationality

@tool
def visa_application_link(query: str) -> str:
    """
    This tool gives information about visa requirements for a nationality.
    It scrapes the Passport Index website for the nationality's visa info.
    """
    docs = url_retriever.invoke(query)
    if not docs:
        return "I found no relevant information in the links storage."

    results = []
    url_pattern = re.compile(r'(https?://[^\s]+)')

    for i, doc in enumerate(docs):
        content = doc.page_content

        match = url_pattern.search(content)
        if match:
            url = match.group(1)
            clickable_url = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
            content = content.replace(url, clickable_url)

        results.append(f"Document {i+1}:\n{content}")

    return "\n\n".join(results)

tools = [visa_required, visa_application_link]
tools_dict = {t.name: t for t in tools}

llm = llm.bind_tools(tools)


system_prompt = """You are an helpful visa assistant agent, you will provide the user an insightful information about what visa he needs based on his nationality - you should use vise_required tool for it.
If the user asks for the official url of the visa application - use the visa_application_link tool to find the url of the visa application.
Never say something based on your general knowledge, everything needs to be official"""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def control_agent(state: AgentState) -> AgentState:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_message = SystemMessage(content=f"Current date and time: {now}")
    messages = [SystemMessage(content=system_prompt), time_message] + list(state['messages'])
    message = llm.invoke(messages)
    return {'messages': [message]}

def visa_agent(state: AgentState) -> AgentState:
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        tool_name = t['name']

        input_arg = t['args'].get('query', '')

        print(f"Calling Tool: {tool_name} with input: {input_arg}")

        if tool_name not in tools_dict:
            result = "Invalid tool name."
        else:
            result = tools_dict[tool_name].invoke(input_arg)
            print(f"Tool result length: {len(result)}")

        results.append(ToolMessage(tool_call_id=t['id'], name=tool_name, content=str(result)))

    print("Tools Execution Complete.")
    return {'messages': results}

def should_continue_visa(state: AgentState):
    last_msg = state['messages'][-1]
    return hasattr(last_msg, 'tool_calls') and len(last_msg.tool_calls) > 0


graph = StateGraph(AgentState)
graph.add_node("control_agent", control_agent)
graph.add_node("visa_agent", visa_agent)
graph.add_conditional_edges("control_agent", should_continue_visa, {True: "visa_agent", False: END})
graph.add_edge("visa_agent", "control_agent")
graph.set_entry_point("control_agent")

agent = graph.compile()

def running_agent():
    print("\n=== WELCOME TO VISA AI AGENT ===")
    print("Type your question or 'exit' to quit.")

    message_history = []

    while True:
        user_input = input("\nYour input: ").strip()
        if user_input.lower() in ['exit', 'ביי', 'סוף']:
            break

        message_history.append(HumanMessage(content=user_input))

        try:
            result = agent.invoke({"messages": message_history})

            for msg in result['messages']:
                message_history.append(msg)

            print("\n=== ANSWER ===")
            print(result['messages'][-1].content)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    running_agent()