from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes

def create_graph():
    nodes = AgentNodes()
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("summary_agent", nodes.summary_node)
    workflow.add_node("mcq_agent", nodes.mcq_node)
    workflow.add_node("analytics_agent", nodes.analytics_node)

    # Define Edges - Sequential execution
    workflow.set_entry_point("summary_agent")
    workflow.add_edge("summary_agent", "mcq_agent")
    workflow.add_edge("mcq_agent", "analytics_agent")
    workflow.add_edge("analytics_agent", END)
    
    return workflow.compile()
