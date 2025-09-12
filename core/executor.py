from core.models import Plan, Action

class Executor:
    def execute_plan(self, plan: Plan):
        print(f"Executing plan for goal: {plan.goal}")
        for step in plan.steps:
            print(f"  - Executing step: {step.action} on MCP {step.mcp} with args {step.args}")
            # In a real scenario, this would call the actual MCP server
            if step.mcp == "playwright":
                print(f"    (Simulating Playwright action: {step.action} {step.args})")
            elif step.mcp == "filesystem":
                print(f"    (Simulating Filesystem action: {step.action} {step.args})")
            elif step.mcp == "notion":
                print(f"    (Simulating Notion action: {step.action} {step.args})")
            else:
                print(f"    (Unknown MCP: {step.mcp})")
