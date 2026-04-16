from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes

def create_graph():
    nodes = AgentNodes()
    workflow = StateGraph(AgentState)

    # Add node
    workflow.add_node("summary_agent", nodes.summary_node)

    # Define edges
    workflow.set_entry_point("summary_agent")
    workflow.add_edge("summary_agent", END)
    
    return workflow.compile()
