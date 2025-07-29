import json
import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from rbac import RBACError

from .config import Config
from .embeddings import gemini_embed
from .governance import GovernanceManager
from .llm_client import LLMClient
from .memory_manager import MemoryManager
from .orchestrator import SimpleOrchestrator
from .prompt_renderer import PromptRenderer
from .retriever import GraphRetriever, VectorRetriever
from .tool_registry import AccessManager, SimilarityMetric, ToolRegistry


# Protocol Configuration
class PROTOCOLS(Enum):
    """Defines the supported communication/execution protocols."""
    MCP = "mcp"  # Master/Controller/Program protocol
    AGENT2AGENT = "agent2agent"


DEFAULT_PROTOCOL = os.getenv("PROTOCOL_TYPE", PROTOCOLS.MCP.value)

# Global Governance Manager
gov = GovernanceManager()


class ProtocolManager:
    """
    Manages the selection and execution of different agent workflows (protocols).
    This class acts as the main entry point for running a complete agent system.
    """

    def __init__(self, protocol: str = None, access_manager: AccessManager = None):
        self.protocol = protocol or DEFAULT_PROTOCOL
        self.access_manager = access_manager or AccessManager()
        self.cfg = Config()
        if self.protocol not in (p.value for p in PROTOCOLS):
            raise ValueError(f"Unsupported protocol: {self.protocol}")
        gov.audit(
            user_id="system",
            action="protocol_selected",
            resource="ProtocolManager",
            metadata={"protocol": self.protocol},
        )

    def run(self, inputs: Dict[str, Any]) -> Any:
        """
        Executes the configured workflow based on the selected protocol.
        """
        if self.protocol == PROTOCOLS.MCP.value:
            return self._run_mcp(inputs)
        elif self.protocol == PROTOCOLS.AGENT2AGENT.value:
            return self._run_agent2agent(inputs)
        else:
            raise NotImplementedError(f"Protocol '{self.protocol}' is not implemented.")

    def _initialize_shared_resources(self):
        """Initializes all shared components needed by the protocols."""
        llm = LLMClient(
            provider=self.cfg.llm_provider,
            api_key=self.cfg.api_key,
            model=self.cfg.llm_model,
        )
        renderer = PromptRenderer(template_dir=Path(self.cfg.template_dir))
        embedding_fn = lambda text: gemini_embed(text, self.cfg.api_key)

        vector_ret = VectorRetriever(
            index_path=self.cfg.faiss_index_path, embed_model_fn=embedding_fn
        )
        graph_ret = GraphRetriever(
            neo4j_uri=self.cfg.neo4j_uri,
            user=self.cfg.neo4j_user,
            password=self.cfg.neo4j_password,
            gds_graph_name=self.cfg.gds_graph_name,
            embed_model_fn=embedding_fn,
        )
        mem_mgr = MemoryManager(
            backend=self.cfg.memory_backend, redis_url=self.cfg.redis_url
        )

        tool_registry = ToolRegistry(
            governance_manager=gov,
            access_manager=self.access_manager,
            embedding_config={"api_key": self.cfg.api_key},
            similarity_metric=SimilarityMetric(self.cfg.tool_similarity_metric),
            embedding_dimension=self.cfg.embedding_dimension,
        )
        return llm, renderer, vector_ret, graph_ret, mem_mgr, tool_registry

    def _define_tools(self, tool_registry: ToolRegistry):
        """A central place to define and register all available tools with policies."""

        @tool_registry.register(
            cost_per_call=0.001, cache_ttl_seconds=300, retry_attempts=2
        )
        def get_weather(city: str) -> str:
            """A governed tool to fetch the weather for a given city."""
            if "new york" in city.lower():
                return "It is currently 75°F and sunny in New York."
            elif "san francisco" in city.lower():
                return "It is currently 62°F and foggy in San Francisco."
            else:
                return f"Weather data for {city} is not available."

    def _build_mcp_orchestrator(self, resources: tuple) -> SimpleOrchestrator:
        """Builds the MCP orchestrator with the superior tool-use workflow."""
        llm, renderer, vector_ret, graph_ret, mem_mgr, tool_registry = resources
        self._define_tools(tool_registry)

        orch = SimpleOrchestrator()

        def retrieve_docs(user_input: str, user_id: str, **kwargs):
            if not self.access_manager.check_access(user_id, "vector_store"):
                raise RBACError(f"User {user_id} unauthorized for retrieval")
            v_docs = vector_ret.query(user_input, top_k=3)
            g_docs = graph_ret.query(user_input, top_k=3)
            combined = {d["id"]: d for d in (v_docs + g_docs)}
            return list(combined.values())

        def make_initial_prompt(
            user_input: str, retrieve_docs: List[dict], **kwargs
        ) -> str:
            relevant_tools = tool_registry.get_relevant_tools(user_input, top_k=3)
            tool_schemas = tool_registry.generate_tool_schema(relevant_tools)
            return renderer.render(
                "tool_decider_prompt.j2",
                question=user_input,
                docs=retrieve_docs,
                tools=tool_schemas,
            )

        def call_llm_for_tool(make_initial_prompt: str, user_id: str, **kwargs) -> dict:
            if not self.access_manager.check_access(user_id, "llm_call"):
                raise RBACError(f"User {user_id} unauthorized for LLM calls")
            summary = mem_mgr.load(user_id, "summary") or ""
            full_prompt = f"{summary}\n\n{make_initial_prompt}"
            return llm.generate(full_prompt)

        def execute_tool(call_llm_for_tool: dict, user_id: str, **kwargs) -> dict:
            response_text = call_llm_for_tool.get("text", "")
            try:
                data = json.loads(response_text)
                if (
                    isinstance(data, dict)
                    and "tool_name" in data
                    and "tool_args" in data
                ):
                    tool_name = data["tool_name"]
                    tool_args = data["tool_args"]
                    governed_tool = tool_registry.get_governed_tool(tool_name, user_id)
                    result = governed_tool(**tool_args)
                    return {"status": "success", "output": result}
            except (json.JSONDecodeError, TypeError, NameError):
                pass
            return {"status": "no_tool_needed", "output": response_text}

        def generate_final_answer(
            execute_tool: dict, user_input: str, **kwargs
        ) -> dict:
            if execute_tool["status"] != "success":
                return {"text": execute_tool["output"]}
            final_prompt = renderer.render(
                "synthesis_prompt.j2",
                question=user_input,
                tool_result=execute_tool["output"],
            )
            return llm.generate(final_prompt)

        # Define the graph structure
        orch.add_node("retrieve_docs", retrieve_docs)
        orch.add_node("make_initial_prompt", make_initial_prompt)
        orch.add_node("call_llm_for_tool", call_llm_for_tool)
        orch.add_node("execute_tool", execute_tool)
        orch.add_node("generate_final_answer", generate_final_answer)

        # Define the execution flow
        # orch.add_edge("user_input", "retrieve_docs")
        # orch.add_edge("user_input", "make_initial_prompt")
        orch.add_edge("retrieve_docs", "make_initial_prompt")
        orch.add_edge("make_initial_prompt", "call_llm_for_tool")
        orch.add_edge("call_llm_for_tool", "execute_tool")
        # orch.add_edge("user_id", "execute_tool")
        orch.add_edge("execute_tool", "generate_final_answer")
        # orch.add_edge("user_input", "generate_final_answer")
        
        return orch

    def _run_mcp(self, inputs: Dict[str, Any]) -> Any:
        """Runs the complete MCP workflow."""
        resources = self._initialize_shared_resources()
        orch = self._build_mcp_orchestrator(resources)
        gov.audit(
            user_id=inputs.get("user_id", "system"),
            action="run_mcp_start",
            resource="ProtocolManager",
        )
        results = orch.run(inputs)
        gov.audit(
            user_id=inputs.get("user_id", "system"),
            action="run_mcp_end",
            resource="ProtocolManager",
        )

        if self.cfg.log_mcp_separate:
            run_id = gov.get_current_run_id()
            filename = f"mcp_output_{run_id}.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, default=str)
                logging.info(f"MCP run output saved to {filename}")
            except Exception as e:
                logging.error(f"Failed to save MCP output to {filename}: {e}")

        return results

    def _run_agent2agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the Agent-to-Agent simulation workflow."""
        gov.audit(
            user_id=inputs.get("user_id", "system"),
            action="run_agent2agent_start",
            resource="ProtocolManager",
        )
        llm, _, vector_ret, _, mem_mgr, _ = self._initialize_shared_resources()
        agents = {}
        agent_ids = ["analyst_agent", "manager_agent"]

        for aid in agent_ids:
            orch = SimpleOrchestrator()

            def retrieve(agent_id=aid, user_input: str = inputs["user_input"], **kwargs):
                return vector_ret.query(f"Query for {agent_id}: {user_input}", top_k=2)

            def respond(retrieve: List[dict], agent_id=aid, **kwargs) -> dict:
                doc_ids = [d.get("id", "N/A") for d in retrieve]
                prompt = (
                    f"As {agent_id}, generate a one-sentence response based on "
                    f"documents: {doc_ids}"
                )
                return llm.generate(prompt)

            orch.add_node(f"{aid}_retrieve", retrieve)
            orch.add_node(f"{aid}_respond", respond)
            orch.add_edge(f"{aid}_retrieve", f"{aid}_respond")
            agents[aid] = orch

        outputs = {}
        for aid, orch in agents.items():
            gov.audit(
                user_id=inputs.get("user_id", "system"), action="agent_start", resource=aid
            )
            res = orch.run(inputs)
            outputs[aid] = res.get(f"{aid}_respond", {}).get("text", "")
            mem_mgr.save(aid, "last_response", outputs[aid])
            gov.audit(
                user_id=inputs.get("user_id", "system"), action="agent_end", resource=aid
            )

        gov.audit(
            user_id=inputs.get("user_id", "system"),
            action="run_agent2agent_end",
            resource="ProtocolManager",
        )

        if self.cfg.log_a2a_separate:
            run_id = gov.get_current_run_id()
            filename = f"a2a_output_{run_id}.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(outputs, f, indent=2, default=str)
                logging.info(f"Agent-to-Agent run output saved to {filename}")
            except Exception as e:
                logging.error(f"Failed to save Agent-to-Agent output to {filename}: {e}")

        return outputs


# Example usage block to demonstrate and test the MCP protocol.
if __name__ == "__main__":
    # Ensure dummy prompt templates exist for this example to run
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    (template_dir / "tool_decider_prompt.j2").write_text(
        "Question: {{ question }}\nTools: {{ tools }}"
    )
    (template_dir / "synthesis_prompt.j2").write_text(
        "Based on this tool result: {{ tool_result }}, "
        "answer the question: {{ question }}"
    )

    custom_roles = {
        "test_user_123": ["vector_store", "llm_call", "weather_forecaster"]
    }
    custom_access_manager = AccessManager(role_config=custom_roles)

    test_inputs = {
        "user_input": "What is the weather like in New York City today?",
        "user_id": "test_user_123",
    }

    pm = ProtocolManager(
        protocol=PROTOCOLS.MCP.value, access_manager=custom_access_manager
    )
    final_results = pm.run(test_inputs)
    print("\n--- MCP Protocol Final Result ---")
    print(json.dumps(final_results.get("generate_final_answer"), indent=2))