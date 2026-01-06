from src.core.models import Plan, Action
from src.mcp.playwright_mcp.services import PlaywrightService
import sys
import logging

logger = logging.getLogger(__name__)

class Executor:
    def __init__(self):
        self.playwright_service = None

    def get_playwright_service(self):
        if not self.playwright_service:
            self.playwright_service = PlaywrightService()
            # Start headless=False so user can see what's happening
            self.playwright_service.start(headless=False) 
        return self.playwright_service

    def execute_plan(self, plan: Plan):
        print(f"Executing plan for goal: {plan.goal}")
        results = []
        try:
            for step in plan.steps:
                print(f"  - Executing step: {step.action} on MCP {step.mcp} with args {step.args}")
                result = None
                if step.mcp == "playwright":
                    service = self.get_playwright_service()
                    if step.action == "navigate":
                        result = service.navigate(**step.args)
                    elif step.action == "type":
                        result = service.type(**step.args)
                    elif step.action == "click":
                        result = service.click(**step.args)
                    elif step.action == "scrape":
                        result = service.scrape(**step.args)
                        print(f"    (Scraped {len(result)} bytes)")
                    elif step.action == "get_form_fields":
                        result = service.get_form_fields()
                        print(f"    (Found {len(result)} form fields)")
                    elif step.action == "screenshot":
                        result = service.screenshot(**step.args)
                        print(f"    (Screenshot saved to {step.args.get('path')})")
                    else:
                        print(f"    (Unknown Playwright action: {step.action})")

                elif step.mcp == "ai":
                    if step.action == "ocr":
                        from src.llm.gemini import get_gemini_multimodal_response
                        result = get_gemini_multimodal_response(
                            prompt=step.args.get("prompt", "Extract all details from this document as JSON."),
                            image_path=step.args.get("path"),
                            system_instruction="Return structured JSON only."
                        )
                        if result is not None:
                            print(f"    (OCR complete: {len(result)} bytes)")
                        else:
                            print(f"    (OCR failed: No response received from AI service)")
                            result = ""

                elif step.mcp == "filesystem":
                    print(f"    (Simulating Filesystem action: {step.action} {step.args})")
                
                elif step.mcp == "notion":
                    print(f"    (Simulating Notion action: {step.action} {step.args})")
                
                else:
                    print(f"    (Unknown MCP: {step.mcp})")
                
                results.append(result)
            
        except Exception:
            logger.exception("Error executing plan")
            raise
        
        return results

    def cleanup(self):
        if self.playwright_service:
            self.playwright_service.stop()
            self.playwright_service = None
