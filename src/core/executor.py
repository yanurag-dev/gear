from src.core.models import Plan, Action
from src.mcp.playwright_mcp.services import PlaywrightService
import sys

class Executor:
    def __init__(self):
        self.playwright_service = None

    def get_playwright_service(self):
        if not self.playwright_service:
            self.playwright_service = PlaywrightService()
            # Start headless=False so user can see what's happening if running locally,
            # or maybe configurable. The user complained about "no browser opening", implying they want to see it.
            # But usually for automation, headless is default. Let's make it visible for now as per user complaint.
            # "There is no browser opening" -> User wants to see it.
            self.playwright_service.start(headless=False) 
        return self.playwright_service

    def execute_plan(self, plan: Plan):
        print(f"Executing plan for goal: {plan.goal}")
        
        try:
            for step in plan.steps:
                print(f"  - Executing step: {step.action} on MCP {step.mcp} with args {step.args}")
                
                if step.mcp == "playwright":
                    service = self.get_playwright_service()
                    if step.action == "navigate":
                        service.navigate(**step.args)
                    elif step.action == "type":
                        service.type(**step.args)
                    elif step.action == "click":
                        service.click(**step.args)
                    elif step.action == "scrape":
                        content = service.scrape(**step.args)
                        print(f"    (Scraped {len(content)} bytes)")
                    else:
                        print(f"    (Unknown Playwright action: {step.action})")

                elif step.mcp == "filesystem":
                    print(f"    (Simulating Filesystem action: {step.action} {step.args})")
                elif step.mcp == "notion":
                    print(f"    (Simulating Notion action: {step.action} {step.args})")
                else:
                    print(f"    (Unknown MCP: {step.mcp})")
        
        except Exception as e:
            print(f"Error executing plan: {e}", file=sys.stderr)
        finally:
             if self.playwright_service:
                 # In a real daemon we might keep it open, but for a single plan execution, maybe close it?
                 # If we close it, the user won't 'see' the final state if it closes instantly.
                 # But leaving it dangling is bad.
                 # Let's keep it open if the script ends? No, the script will exit.
                 # Let's close it.
                 self.playwright_service.stop()
