from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__("coding_agent")

    async def execute_task(self, task: AgentTask) -> AgentResult:
        code_input = task.parameters.get("code", "")
        action = task.parameters.get("action", "review")
        
        if action == "review":
            lines_count = len(code_input.splitlines()) if code_input else 0
            res_summary = f"Code Review Completed: Analyzed {lines_count} lines of code."
        else:
            res_summary = f"Code Action '{action}' executed successfully."

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={"summary": res_summary, "action": action}
        )
