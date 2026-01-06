from src.core.models import Plan, Action
from src.mcp.playwright_mcp.services import PlaywrightService
from typing import Optional
import sys
import logging

logger = logging.getLogger(__name__)

class Executor:
    def __init__(self, interactive: bool = True):
        self.playwright_service: Optional[PlaywrightService] = None
        self.interactive = interactive

    def get_playwright_service(self) -> PlaywrightService:
        if not self.playwright_service:
            self.playwright_service = PlaywrightService()
        
        if not self.playwright_service.is_active():
            # If the service exists but is not active (e.g. browser closed by user),
            # trigger start to recover.
            self.playwright_service.start(headless=not self.interactive)
            
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
                        file_path = step.args.get("path")
                        if not file_path:
                            print(f"    (OCR failed: No file path provided)")
                            result = ""
                        else:
                            result = get_gemini_multimodal_response(
                                prompt=step.args.get("prompt", "Extract all details from this document as JSON."),
                                file_path=file_path,
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

    def get_current_state(self) -> dict:
        """Returns the current state of the executor (e.g. current URL)."""
        state = {"url": None}
        if self.playwright_service and self.playwright_service.is_active():
            page = self.playwright_service.page
            if page is not None:
                state["url"] = getattr(page, "url", None)
        return state

    def cleanup(self):
        if self.playwright_service:
            self.playwright_service.stop()
            self.playwright_service = None
