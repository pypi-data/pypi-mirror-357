import json
import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from rbac import RBACError
from .config import Config
from .embeddings import gemini_embed
from .governance import GovernanceManager
from .llm_client import LLMClient
from .memory_manager import MemoryManager
from .orchestrator import SimpleOrchestrator
from .prompt_renderer import PromptRenderer
from .retriever import GraphRetriever, VectorRetriever
from .tool_registry import SimilarityMetric, ToolRegistry, AccessManager

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
    def __init__(self, protocol: str = None, access_manager: Optional[AccessManager] = None, llm_model: Optional[str] = None):
        self.protocol = protocol or DEFAULT_PROTOCOL
        self.access_manager = access_manager or AccessManager() 
        self.llm_model_override = llm_model
        if self.protocol not in (p.value for p in PROTOCOLS):
            raise ValueError("Unsupported protocol: {}".format(self.protocol))
        gov.audit(
            user_id="system",
            action="protocol_selected",
            resource="ProtocolManager",
            metadata={"protocol": self.protocol}
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
            raise NotImplementedError("Protocol '{}' is not implemented.".format(self.protocol))

    def _initialize_shared_resources(self):
        """Initializes all shared components needed by the protocols."""
        cfg = Config()
        model_to_use = self.llm_model_override or cfg.llm_model
        llm = LLMClient(provider=cfg.llm_provider, api_key=cfg.api_key, model=model_to_use)
        renderer = PromptRenderer(template_dir=Path(cfg.template_dir))
        embedding_fn = lambda text: gemini_embed(text, cfg.api_key)

        vector_ret = VectorRetriever(index_path=cfg.faiss_index_path, embed_model_fn=embedding_fn)
        
        # Conditionally initialize GraphRetriever only if NEO4J_URI is explicitly set and not the default
        graph_ret = None
        if cfg.neo4j_uri and cfg.neo4j_uri != "bolt://localhost:7687":
            try:
                graph_ret = GraphRetriever(
                    neo4j_uri=cfg.neo4j_uri,
                    user=cfg.neo4j_user,
                    password=cfg.neo4j_password,
                    gds_graph_name=cfg.gds_graph_name,
                    embed_model_fn=embedding_fn
                )
            except Exception as e:
                logging.warning(f"Could not connect to Neo4j GraphRetriever: {e}. Graph features will be unavailable.")
                graph_ret = None
        else:
            logging.info("Neo4j URI not explicitly configured or using default. GraphRetriever will not be initialized.")
            
        mem_mgr = MemoryManager(backend=cfg.memory_backend, redis_url=cfg.redis_url)

        # Correctly initialize the ToolRegistry with all new configurations
        tool_registry = ToolRegistry(
            governance_manager=gov,
            access_manager=self.access_manager,
            embedding_config={"api_key": cfg.api_key},
            similarity_metric=SimilarityMetric(cfg.tool_similarity_metric),
            embedding_dimension=cfg.embedding_dimension
        )
        return llm, renderer, vector_ret, graph_ret, mem_mgr, tool_registry

    def _define_tools(self, tool_registry: ToolRegistry):
        """A central place to define and register all available tools with policies."""
        @tool_registry.register(
            cost_per_call=0.001,
            cache_ttl_seconds=512,
            retry_attempts=2
        )
        def get_weather(city: str) -> str:
            """A governed tool to fetch the weather for a given city."""
            if "new york" in city.lower():
                return "It is currently 82°F and sunny in New York."
            elif "san francisco" in city.lower():
                return "It is currently 65°F and foggy in San Francisco."
            else:
                return "Weather data for {} is not available.".format(city)

    def _build_mcp_orchestrator(self, resources: tuple) -> SimpleOrchestrator:
        """Builds the MCP orchestrator with the superior tool-use workflow."""
        llm, renderer, vector_ret, graph_ret, mem_mgr, tool_registry = resources
        self._define_tools(tool_registry)

        orch = SimpleOrchestrator()

        def retrieve_docs(user_input: str, user_id: str, **kwargs):
            if not tool_registry.access_manager.check_access(user_id, "vector_store"):
                raise RBACError("User {} unauthorized for retrieval".format(user_id))
            
            v_docs = vector_ret.query(user_input, top_k=3)
            
            g_docs = []
            if graph_ret:
                g_docs = graph_ret.query(user_input, top_k=3)
            else:
                logging.info("GraphRetriever not available, skipping graph query.")

            combined = {d["id"]: d for d in (v_docs + g_docs)}
            return list(combined.values())

        def make_initial_prompt(user_input: str, retrieve_docs: List[dict], **kwargs) -> str:
            relevant_tools = tool_registry.get_relevant_tools(user_input, top_k=3)
            tool_schemas = tool_registry.generate_tool_schema(relevant_tools)
            return renderer.render(
                "tool_decider_prompt.j2",
                question=user_input,
                docs=retrieve_docs,
                tools=tool_schemas
            )

        def call_llm_for_tool(make_initial_prompt: str, user_id: str, **kwargs) -> dict:
            if not tool_registry.access_manager.check_access(user_id, "llm_call"):
                raise RBACError("User {} unauthorized for LLM calls".format(user_id))
            summary = mem_mgr.load(user_id, "summary") or ""
            full_prompt = "{}\n\n{}".format(summary, make_initial_prompt)
            return llm.generate(full_prompt)

        def execute_tool(call_llm_for_tool: dict, user_id: str, **kwargs) -> dict:
            response_text = call_llm_for_tool.get("text", "")
            try:
                data = json.loads(response_text)
                if isinstance(data, dict) and "tool_name" in data and "tool_args" in data:
                    tool_name = data["tool_name"]
                    tool_args = data["tool_args"]
                    governed_tool = tool_registry.get_governed_tool(tool_name, user_id)
                    result = governed_tool(**tool_args)
                    return {"status": "success", "output": result}
            except (json.JSONDecodeError, TypeError, NameError):
                pass
            return {"status": "no_tool_needed", "output": response_text}

        def generate_final_answer(execute_tool: dict, user_input: str, **kwargs) -> dict:
            if execute_tool["status"] != "success":
                return {"text": execute_tool["output"]}
            final_prompt = renderer.render("synthesis_prompt.j2", question=user_input, tool_result=execute_tool["output"])
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
        
        gov.audit(user_id=inputs.get("user_id", "system"), action="run_mcp_start", resource="ProtocolManager")
        results = orch.run(inputs)
        gov.audit(user_id=inputs.get("user_id", "system"), action="run_mcp_end", resource="ProtocolManager")
        return results

    def _run_agent2agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the Agent-to-Agent simulation workflow."""
        gov.audit(user_id=inputs.get("user_id", "system"), action="run_agent2agent_start", resource="ProtocolManager")
        llm, renderer, vector_ret, graph_ret, mem_mgr, tool_registry = self._initialize_shared_resources()
        agents = {}
        agent_ids = ["analyst_agent", "manager_agent"]
        
        for aid in agent_ids:
            orch = SimpleOrchestrator()
            def retrieve(agent_id=aid, user_input: str = inputs["user_input"], 
                         vector_ret=vector_ret, graph_ret=graph_ret, **kwargs):
                
                v_docs = vector_ret.query("Query for {}: {}".format(aid, user_input), top_k=2)
                g_docs = []
                if graph_ret:
                    g_docs = graph_ret.query("Query for {}: {}".format(aid, user_input), top_k=2)
                else:
                    logging.info(f"GraphRetriever not available for {aid}, skipping graph query.")

                combined = {d["id"]: d for d in (v_docs + g_docs)}
                return list(combined.values())

            def respond(retrieve_docs: List[dict] = None, agent_id=aid, llm=llm, **kwargs) -> dict: 
                retrieved_results_from_orchestrator = kwargs.get(f"{aid}_retrieve", retrieve_docs if retrieve_docs is not None else [])
                
                doc_ids = [d.get('id', 'N/A') for d in retrieved_results_from_orchestrator]
                prompt = "As {}, generate a one-sentence response based on documents: {}".format(agent_id, doc_ids)
                return llm.generate(prompt)

            orch.add_node("{}_retrieve".format(aid), retrieve)
            orch.add_node("{}_respond".format(aid), respond)
            orch.add_edge("{}_retrieve".format(aid), "{}_respond".format(aid))
            agents[aid] = orch

        outputs = {}
        for aid, orch in agents.items():
            gov.audit(user_id=inputs.get("user_id", "system"), action="agent_start", resource=aid)
            res = orch.run(inputs)
            outputs[aid] = res.get("{}_respond".format(aid), {}).get("text", "")
            mem_mgr.save(aid, "last_response", outputs[aid])
            gov.audit(user_id=inputs.get("user_id", "system"), action="agent_end", resource=aid)
            
        gov.audit(user_id=inputs.get("user_id", "system"), action="run_agent2agent_end", resource="ProtocolManager")
        return outputs

# Example usage block to demonstrate and test the MCP protocol.
if __name__ == "__main__":
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    (template_dir / "tool_decider_prompt.j2").write_text("Question: {{ question }}\nTools: {{ tools }}")
    (template_dir / "synthesis_prompt.j2").write_text("Based on this tool result: {{ tool_result }}, answer the question: {{ question }}")
    custom_roles = {
        "test_user_123": ["vector_store", "llm_call", "weather_forecaster"]
    }
    custom_access_manager = AccessManager(role_config=custom_roles)
    test_inputs = {"user_input": "What is the weather like in New York City today?", "user_id": "test_user_123"}
    pm = ProtocolManager(
        protocol=PROTOCOLS.MCP.value, 
        access_manager=custom_access_manager,
        llm_model=os.environ["LLM_MODEL"]
    )
    final_results = pm.run(test_inputs)
    print("\n--- MCP Protocol Final Result ---")
    print(json.dumps(final_results.get("generate_final_answer"), indent=2))
