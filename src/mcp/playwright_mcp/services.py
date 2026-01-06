from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Optional, Dict, Any

class PlaywrightService:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self, headless: bool = False):
        if not self.playwright:
            self.playwright = sync_playwright().start()
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("Browser started.")

    def stop(self):
        try:
            if self.page:
                self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        print("Browser stopped.")

    def navigate(self, url: str):
        if not self.page:
            self.start()
        
        # Ensure the URL has a protocol
        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"
            
        print(f"Navigating to {url}...")
        self.page.goto(url)

    def type(self, selector: str, text: str):
        if not self.page:
            raise RuntimeError("Browser not started. Call navigate first.")
        print(f"Typing '{text}' into '{selector}'...")
        self.page.fill(selector, text)

    def click(self, selector: str):
        if not self.page:
            raise RuntimeError("Browser not started. Call navigate first.")
        print(f"Clicking '{selector}'...")
        self.page.click(selector)

    def scrape(self, url: str = None) -> str:
        if url and self.page and self.page.url != url:
             self.navigate(url)
        
        if not self.page:
             raise RuntimeError("Browser not started.")

        print(f"Scraping content from {self.page.url}...")
        return self.page.content()

    def screenshot(self, path: str):
        if not self.page:
            raise RuntimeError("Browser not started.")
        self.page.screenshot(path=path)

    def get_form_fields(self) -> list:
        if not self.page:
            raise RuntimeError("Browser not started.")
        
        print("Extracting form fields with advanced Shadow DOM & anti-scraping detection...")
        
        # Wait for dynamic content to load
        self.page.wait_for_timeout(2000)  # Give JS time to inject Shadow DOM
        
        # Advanced JS script that handles Shadow DOM, honeypots, and dynamic forms
        fields = self.page.evaluate("""
            () => {
                // Helper to check if element is visible (not a honeypot)
                const isVisible = (el) => {
                    if (!el) return false;
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    
                    // Check if element is actually rendered
                    if (style.display === 'none' || 
                        style.visibility === 'hidden' || 
                        parseFloat(style.opacity) === 0) {
                        return false;
                    }
                    
                    // Honeypot detection: check if positioned off-screen
                    if (rect.width === 0 || rect.height === 0) return false;
                    if (rect.top < -1000 || rect.left < -1000) return false;
                    if (parseFloat(style.width) === 0 || parseFloat(style.height) === 0) return false;
                    
                    return true;
                };
                
                // Helper to detect honeypot fields
                const isHoneypot = (input) => {
                    const name = (input.name || '').toLowerCase();
                    const id = (input.id || '').toLowerCase();
                    const label = (input.getAttribute('aria-label') || '').toLowerCase();
                    
                    const honeypotPatterns = [
                        'honeypot', 'hp_', 'bot', 'spam', 'trap',
                        'website', 'url', 'confirm_email', 'email_confirm'
                    ];
                    
                    return honeypotPatterns.some(pattern => 
                        name.includes(pattern) || id.includes(pattern) || label.includes(pattern)
                    );
                };
                
                // Helper to get text content of an element, cleaned
                const getCleanText = (el) => {
                    if (!el) return '';
                    return el.innerText?.trim() || el.textContent?.trim() || '';
                };
                
                // Helper to generate a reliable selector (Shadow DOM aware)
                const generateSelector = (el, inShadow = false) => {
                    if (el.id) return inShadow ? `shadow::#${el.id}` : `#${el.id}`;
                    if (el.name) return inShadow ? `shadow::[name="${el.name}"]` : `[name="${el.name}"]`;
                    
                    // Generate path-based selector
                    let path = [];
                    let current = el;
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        let selector = current.nodeName.toLowerCase();
                        if (current.className && typeof current.className === 'string') {
                            const classes = current.className.trim().split(/\\s+/).filter(c => c && !c.includes(' '));
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }
                        path.unshift(selector);
                        if (current.id || path.length > 5) break;
                        current = current.parentElement;
                    }
                    const finalSelector = path.join(' > ');
                    return inShadow ? `shadow::${finalSelector}` : finalSelector;
                };
                
                // Helper to find label for an input (Shadow DOM aware)
                const findLabel = (input, root = document) => {
                    let label = '';
                    
                    // Strategy 1: aria-label
                    if (input.getAttribute('aria-label')) {
                        label = input.getAttribute('aria-label');
                    }
                    
                    // Strategy 2: aria-labelledby
                    if (!label && input.getAttribute('aria-labelledby')) {
                        const labelId = input.getAttribute('aria-labelledby');
                        const labelEl = root.getElementById(labelId);
                        if (labelEl) label = getCleanText(labelEl);
                    }
                    
                    // Strategy 3: Associated label element (for attribute)
                    if (!label && input.id) {
                        const labelEl = root.querySelector(`label[for="${input.id}"]`);
                        if (labelEl) label = getCleanText(labelEl);
                    }
                    
                    // Strategy 4: Parent label
                    if (!label) {
                        const parentLabel = input.closest('label');
                        if (parentLabel) {
                            const clone = parentLabel.cloneNode(true);
                            const nestedInputs = clone.querySelectorAll('input, select, textarea');
                            nestedInputs.forEach(inp => inp.remove());
                            label = getCleanText(clone);
                        }
                    }
                    
                    // Strategy 5: Previous sibling
                    if (!label) {
                        let prev = input.previousElementSibling;
                        let attempts = 0;
                        while (prev && !label && attempts < 3) {
                            if (prev.tagName === 'LABEL') {
                                label = getCleanText(prev);
                                break;
                            }
                            if (prev.tagName === 'SPAN' || prev.tagName === 'DIV' || prev.tagName === 'P') {
                                const text = getCleanText(prev);
                                if (text.length > 0 && text.length < 100) {
                                    label = text;
                                    break;
                                }
                            }
                            prev = prev.previousElementSibling;
                            attempts++;
                        }
                    }
                    
                    // Strategy 6: Placeholder
                    if (!label && input.placeholder) {
                        label = input.placeholder;
                    }
                    
                    // Strategy 7: Name attribute
                    if (!label && input.name) {
                        label = input.name.replace(/[_-]/g, ' ');
                    }
                    
                    // Strategy 8: Title attribute
                    if (!label && input.title) {
                        label = input.title;
                    }
                    
                    return label.trim();
                };
                
                // Recursive function to traverse Shadow DOM
                const getAllInputsRecursive = (root, inShadow = false) => {
                    let allInputs = [];
                    
                    // Get inputs from current root
                    const inputs = Array.from(root.querySelectorAll('input, select, textarea, button'));
                    inputs.forEach(input => {
                        allInputs.push({ element: input, inShadow, root });
                    });
                    
                    // Find all elements with Shadow DOM
                    const allElements = root.querySelectorAll('*');
                    allElements.forEach(el => {
                        if (el.shadowRoot) {
                            // Recursively traverse shadow root
                            const shadowInputs = getAllInputsRecursive(el.shadowRoot, true);
                            allInputs = allInputs.concat(shadowInputs);
                        }
                    });
                    
                    return allInputs;
                };
                
                // Get all inputs including those in Shadow DOM
                const allInputData = getAllInputsRecursive(document);
                
                // Process and filter inputs
                const processedFields = allInputData
                    .filter(({ element: input }) => {
                        // Filter out hidden inputs
                        if (input.type === 'hidden') return false;
                        
                        // Keep submit/button elements
                        if (input.type === 'submit' || input.type === 'button' || input.tagName === 'BUTTON') {
                            return isVisible(input);
                        }
                        
                        // Filter honeypots
                        if (isHoneypot(input)) {
                            console.log('Detected honeypot field:', input.name || input.id);
                            return false;
                        }
                        
                        // Only keep visible fields
                        return isVisible(input);
                    })
                    .map(({ element: input, inShadow, root }, index) => {
                        const label = findLabel(input, root);
                        const selector = generateSelector(input, inShadow);
                        
                        // Get options for select/radio/checkbox
                        let options = null;
                        if (input.tagName === 'SELECT') {
                            options = Array.from(input.options).map(opt => ({
                                value: opt.value,
                                text: opt.text,
                                selected: opt.selected
                            }));
                        } else if (input.type === 'radio' || input.type === 'checkbox') {
                            if (input.name) {
                                const related = root.querySelectorAll(`input[name="${input.name}"]`);
                                options = Array.from(related).map(r => ({
                                    value: r.value,
                                    label: findLabel(r, root),
                                    checked: r.checked
                                }));
                            }
                        }
                        
                        // Determine which form this belongs to
                        const form = input.closest('form');
                        const formId = form ? (form.id || form.name || 'form-' + Array.from(document.forms).indexOf(form)) : null;
                        
                        // Detect if this is a navigation button (multi-step forms)
                        const isNavButton = input.tagName === 'BUTTON' && 
                            (getCleanText(input).toLowerCase().includes('next') ||
                             getCleanText(input).toLowerCase().includes('previous') ||
                             getCleanText(input).toLowerCase().includes('back') ||
                             input.className.toLowerCase().includes('nav'));
                        
                        return {
                            index: index,
                            id: input.id || null,
                            name: input.name || null,
                            type: input.type || input.tagName.toLowerCase(),
                            tagName: input.tagName,
                            label: label,
                            placeholder: input.placeholder || null,
                            value: input.value || null,
                            required: input.required || input.getAttribute('aria-required') === 'true',
                            disabled: input.disabled,
                            readonly: input.readOnly,
                            selector: selector,
                            inShadowDOM: inShadow,
                            options: options,
                            formId: formId,
                            maxLength: input.maxLength > 0 ? input.maxLength : null,
                            pattern: input.pattern || null,
                            autocomplete: input.autocomplete || null,
                            isNavigationButton: isNavButton,
                            buttonText: input.tagName === 'BUTTON' ? getCleanText(input) : null
                        };
                    });
                
                return processedFields;
            }
        """)
        
        print(f"Extracted {len(fields)} form fields (including Shadow DOM)")
        return fields
