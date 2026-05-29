from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

def debug_agent(state):
    code = state["code"]
    result = llm.invoke(f"Find bugs in this code:\n{code}")
    return {"bugs": result.content}

def explain_agent(state):
    code = state["code"]
    result = llm.invoke(f"Explain this code:\n{code}")
    return {"explanation": result.content}


def build_graph():
    graph = StateGraph(dict)

    graph.add_node("debugger", debug_agent)
    graph.add_node("explainer", explain_agent)

    graph.set_entry_point("debugger")
    graph.add_edge("debugger", "explainer")

    return graph.compile()
