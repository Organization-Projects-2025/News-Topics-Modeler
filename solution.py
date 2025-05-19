from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Non-headless for bot detection bypass
        page = browser.new_page()
        
        # Set user-agent to mimic a real browser
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Debug responses
        page.on("response", lambda response: print(f"Response: {response.status} {response.url}"))
        
        # Navigate with increased timeout
        page.goto("https://www.nytimes.com/2025/05/15/us/politics/supreme-court-birthright-citizenship-takeaways.html", timeout=60000)
        page.wait_for_load_state("domcontentloaded")  # Wait for DOM, not networkidle

        # Handle potential paywall/login modal
        close_button = page.query_selector("button[data-testid='close-button']")  # Adjust selector
        if close_button:
            close_button.click()
            page.wait_for_timeout(1000)

        # Extract title and content
        title_element = page.query_selector("h1[data-testid='headline']")
        title = title_element.inner_text() if title_element else "Title not found"

        content_element = page.query_selector("section[name='articleBody']")
        content = content_element.inner_text() if content_element else "Content not found"

        print(f"Title: {title}")
        print(f"Content: {content}")

        # Save screenshot for debugging
        page.screenshot(path="page_screenshot.png")
        browser.close()

except Exception as e:
    print(f"An error occurred: {e}")
    if 'page' in locals() and not page.is_closed():
        page.screenshot(path="error_screenshot.png")