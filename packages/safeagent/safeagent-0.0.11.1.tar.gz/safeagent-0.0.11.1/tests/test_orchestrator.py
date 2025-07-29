# tests/test_orchestrator.py
import pytest
from safeagent import StatefulOrchestrator

def test_orchestrator_linear_graph():
    """Tests a simple graph with a single, linear path."""
    
    def start_node(state):
        return {"value": 1}

    def middle_node(state):
        return {"value": state["value"] + 1}

    def end_node(state):
        return {"value": state["value"] * 2}

    orchestrator = StatefulOrchestrator(entry_node="start")
    orchestrator.add_node("start", start_node)
    orchestrator.add_node("middle", middle_node)
    orchestrator.add_node("end", end_node)
    orchestrator.add_edge("start", "middle")
    orchestrator.add_edge("middle", "end")
    orchestrator.add_edge("end", "__end__")

    status, final_state = orchestrator.run(inputs={})
    
    assert status == "finished"
    assert final_state["value"] == 4 # (1 + 1) * 2

def test_orchestrator_conditional_graph():
    """
    Tests a graph with a conditional edge to verify branching logic.
    """
    def start_node(state):
        # Initial state comes from the run input
        return {}

    def high_path_node(state):
        return {"path_taken": "high"}

    def low_path_node(state):
        return {"path_taken": "low"}

    def check_condition(state):
        """Decides which path to take based on the input value."""
        if state.get("input_value", 0) > 10:
            return "high_path"
        else:
            return "low_path"

    orchestrator = StatefulOrchestrator(entry_node="start")
    orchestrator.add_node("start", start_node)
    orchestrator.add_node("high_path", high_path_node)
    orchestrator.add_node("low_path", low_path_node)

    # Add the conditional edge from the start node
    orchestrator.add_conditional_edge("start", check_condition)
    
    # Both paths lead to the end
    orchestrator.add_edge("high_path", "__end__")
    orchestrator.add_edge("low_path", "__end__")

    # Test the "high" path
    status_high, final_state_high = orchestrator.run(inputs={"input_value": 20})
    assert status_high == "finished"
    assert final_state_high["path_taken"] == "high"

    # Test the "low" path
    status_low, final_state_low = orchestrator.run(inputs={"input_value": 5})
    assert status_low == "finished"
    assert final_state_low["path_taken"] == "low"
