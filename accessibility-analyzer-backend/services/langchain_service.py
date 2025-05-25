from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import base64
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", max_tokens=1024, api_key=os.getenv("OPENAI_API_KEY"))

def analyze_accessibility(html: str, screenshot_base64: str) -> dict:
    """
    Analyzes website accessibility from HTML and a screenshot using a multi-step AI workflow.
    """
    try:
        # 1. HTML Analysis
        print("LANGCHAIN_SERVICE: Starting HTML analysis...")
        if not html:
            print("LANGCHAIN_SERVICE_ERROR: HTML content is missing or empty.")
            return {"error": "HTML content is missing for analysis."}

        html_analysis_prompt = ChatPromptTemplate.from_template(
            """
    **Your Role:** You are an expert Web Accessibility Specialist. Your task is to conduct a thorough analysis of the provided HTML code based on the core principles of the Web Content Accessibility Guidelines (WCAG).

    **Your Goal:** Identify accessibility violations and provide clear, actionable feedback with code examples to help a developer fix the issues.

    **Analyze the following HTML content based on these 6 critical accessibility guidelines:**

    **1. Semantic HTML Structure:**
    - **Description:** A well-structured document uses semantic HTML tags to define roles for different parts of the page. This is crucial for screen reader navigation.
    - **Analysis Criteria:**
        - Does the page use landmark tags like `<header>`, `<nav>`, `<main>`, `<footer>`, and `<aside>` correctly?
        - Is content structured into logical sections using `<section>` or `<article>` tags?
        - Is the main content of the page enclosed within a `<main>` tag?

    **2. Image Accessibility (Alternative Text):**
    - **Description:** All informative images must have descriptive alternative (alt) text. Decorative images should have an empty alt attribute (`alt=""`). This ensures that users of screen readers can understand the content and purpose of images.
    - **Analysis Criteria:**
        - Do all `<img>` tags have an `alt` attribute?
        - For `<img>` tags with `alt` attributes, is the text descriptive and meaningful, or is it a non-helpful placeholder like "image" or a filename?
        - Are purely decorative images correctly marked with `alt=""`?

    **3. Heading Hierarchy:**
    - **Description:** Headings must be structured in a logical, hierarchical order (`<h1>` followed by `<h2>`, `<h2>` by `<h3>`, etc.) without skipping levels. This is one of the primary ways screen reader users navigate a page.
    - **Analysis Criteria:**
        - Is there only one `<h1>` per page?
        - Do the heading levels follow a logical order (e.g., no `<h4>` directly after an `<h2>`)?
        - Are headings used to create an outline of the page content, or are they used just for styling text?

    **4. Form Labeling and Accessibility:**
    - **Description:** Every form control (`<input>`, `<textarea>`, `<select>`) needs a programmatically associated `<label>`. This allows screen reader users to know what information each field is asking for.
    - **Analysis Criteria:**
        - Does every `<input>`, `<textarea>`, and `<select>` element have an associated `<label>`?
        - Is the `for` attribute of the `<label>` correctly matched with the `id` of the corresponding form element?
        - Do related form elements (like a group of checkboxes or radio buttons) get grouped using `<fieldset>` and described with a `<legend>`?

    **5. Link Text Clarity:**
    - **Description:** The purpose of every link should be clear from its text alone. Using generic, non-descriptive phrases like "Click Here," "Read More," or "Learn More" is a common accessibility failure.
    - **Analysis Criteria:**
        - Identify links with ambiguous text (e.g., "click here," "more," "link").
        - Does the link text accurately describe the destination or action? For example, instead of "Click here to download the report," the link text should be "Download the 2024 Accessibility Report."

    **6. Language Specification:**
    - **Description:** The primary language of the page must be declared in the `<html>` tag using the `lang` attribute. This allows screen readers to switch to the correct language profile to pronounce the content correctly.
    - **Analysis Criteria:**
        - Does the `<html>` tag have a `lang` attribute (e.g., `<html lang="en">`)?
        - Is the value of the `lang` attribute a valid IETF language tag (e.g., "en", "es", "fr-CA")?

    ---

    **Output Format:**
    For each guideline where you find an issue, provide the following:
    - **Guideline Violated:** The name of the guideline (e.g., "Image Accessibility").
    - **Severity:** (Critical, High, Medium, Low).
    - **Issue Description:** A clear explanation of *why* it's an issue.
    - **Code Snippet:** The exact line(s) of HTML causing the issue.
    - **Recommendation:** A specific, actionable suggestion for how to fix the code.

    If no issues are found for a guideline, simply state: "No issues found."

    Begin your analysis now on the HTML content provided below:

    ```html
    {html_content}
    ```
    """
    )
        html_chain = html_analysis_prompt | llm | StrOutputParser()
        html_feedback = html_chain.invoke({"html_content": html})
        print(f"LANGCHAIN_SERVICE: HTML analysis feedback received: {html_feedback[:100]}...")

        # 2. Screenshot Analysis
        print("LANGCHAIN_SERVICE: Starting screenshot analysis...")
        if not screenshot_base64:
            print("LANGCHAIN_SERVICE_ERROR: Screenshot data is missing or empty.")
            screenshot_feedback = "Screenshot data was not provided or was invalid."
        else:
            screenshot_analysis_prompt = ChatPromptTemplate.from_messages([
                ("user", [
                    {"type": "text", "text": """
**Your Role:** You are an expert UI/UX Accessibility Analyst. Your task is to perform a visual accessibility audit of the provided webpage screenshot based on key visual design and accessibility principles from WCAG.

**Your Goal:** Identify visual design choices that negatively impact accessibility for users with visual impairments, motor difficulties, or cognitive disabilities. Provide clear, actionable feedback to help a designer or developer address these issues.

**Analyze the provided screenshot based on these 5 critical visual accessibility guidelines:**

**1. Color Contrast:**
- **Description:** Text and meaningful graphical elements (like icons or input borders) must have sufficient color contrast against their background to be readable by people with low vision or color blindness. The WCAG AA standard requires a ratio of at least 4.5:1 for normal text and 3:1 for large text.
- **Analysis Criteria:**
    - Visually scan the page for text or UI elements that appear to have low contrast. Point out specific examples (e.g., "The light gray text on the white background in the footer appears to have low contrast.").
    - Check if text placed over images or gradients has a consistent, readable contrast level.

**2. Typography and Readability:**
- **Description:** Text should be easy to read. This is affected by font size, weight, and spacing.
- **Analysis Criteria:**
    - Is the primary body text a reasonable size (typically at least 16px)?
    - Is there adequate spacing between lines of text (line-height, typically ~1.5) and between paragraphs?
    - Are font choices clear and legible? Avoid overly decorative or thin fonts for body text.

**3. Interactive Element Clarity & Target Size:**
- **Description:** Users need to be able to identify interactive elements (like links and buttons) and physically interact with them easily.
- **Analysis Criteria:**
    - **Clarity:** Are links and buttons visually distinct from non-interactive text? Do they have clear indicators like underlines or a button shape?
    - **Target Size:** Are buttons, links, and other interactive controls large enough to be easily tapped or clicked? Small targets can be difficult for users with motor impairments. Identify elements that appear too small or too close together.

**4. Layout and Spacing (White Space):**
- **Description:** A cluttered layout can be overwhelming and make it difficult to distinguish between different sections of content. Good use of white space improves clarity and focus.
- **Analysis Criteria:**
    - Does the layout feel cramped or cluttered?
    - Is there sufficient spacing between major content blocks, such as the navigation, main content, and footer?
    - Are interactive elements spaced far enough apart to prevent accidental clicks?

**5. Information Conveyed Solely by Color:**
- **Description:** Color should not be the *only* method used to convey important information. This is critical for users who are colorblind.
- **Analysis Criteria:**
    - Look for instances where information is indicated only by a change in color. For example, is an error message for a form field shown *only* by turning the label red?
    - A pass/fail status, link states, or selected items should use a secondary indicator, such as an icon, an underline, bold text, or another visual cue in addition to color.

---

**Output Format:**
For each guideline where you find an issue, provide the following:
- **Guideline Violated:** The name of the guideline (e.g., "Color Contrast").
- **Severity:** (Critical, High, Medium, Low).
- **Issue Description:** A clear explanation of the visual issue and where it appears on the page.
- **Recommendation:** A specific suggestion for how to fix the visual design (e.g., "Increase the font color contrast to meet the WCAG AA 4.5:1 ratio," or "Add an underline to all inline links to distinguish them from plain text.").

If no issues are found for a guideline, simply state: "No significant issues found."

Begin your analysis now.
"""},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_base64}"}}
                ])
            ])
            screenshot_chain = screenshot_analysis_prompt | llm | StrOutputParser()
            screenshot_feedback = screenshot_chain.invoke({})
        print(f"LANGCHAIN_SERVICE: Screenshot analysis feedback received: {screenshot_feedback[:100]}...")

        # 3. Aggregated Report and Scoring
        print("LANGCHAIN_SERVICE: Starting aggregated report and scoring...")
        report_prompt = ChatPromptTemplate.from_template(
    """
    **Your Role:** You are a Lead Web Accessibility Consultant. Your task is to synthesize the detailed technical findings from an HTML code analysis and a visual screenshot analysis into a single, client-ready accessibility report.

    **Your Goal:** Create a clear, insightful, and actionable report that helps a website owner understand their site's accessibility strengths and weaknesses. The report must include scores for key categories and a prioritized implementation plan.

    ---

    **Input Data:**

    **1. HTML Analysis Feedback:**
    ```
    {html_feedback}
    ```

    **2. Screenshot Analysis Feedback:**
    ```
    {screenshot_feedback}
    ```

    ---

    **Your Task (Follow these steps carefully):**

    **Step 1: Synthesize Findings**
    Review both sets of feedback. Map each identified issue (e.g., "Missing alt text," "Low contrast text," "Skipped heading level") to one of the five categories below.

    **Step 2: Score Each Category**
    For each category, provide a score from 0 to 100 based on the number and severity of the issues you mapped to it. Use this rubric as a guide:
    - **90-100:** Excellent. No significant issues found, or only minor best-practice suggestions.
    - **70-89:** Good. Some moderate issues were found that should be addressed but don't block core functionality.
    - **50-69:** Fair. Several notable issues exist that can create barriers for some users.
    - **30-49:** Poor. Serious accessibility issues were found that significantly impact usability for people with disabilities.
    - **0-29:** Critical. The site has critical blockers in this category, making key content or functions unusable for some user groups.

    **Step 3: Write Category Feedback & Implementation Plan**
    - For each category, write a concise `feedback` summary. Explain the score by highlighting the key issues found (both from the HTML and screenshot analysis).
    - Create a single, prioritized `implementation_plan`. Start with the most critical, highest-impact fixes (from the lowest-scoring categories) and move to minor improvements. Make it a clear, step-by-step guide for a developer.

    ---

    **Categories for Analysis:**

    1.  **Structure & Semantics:** How well the HTML is structured for navigation.
        *(Considers: Heading hierarchy, use of `<main>`, `<nav>`, etc., ARIA roles)*
    2.  **Readability & Visual Clarity:** How easy it is to read and visually parse the content.
        *(Considers: Font sizes, color contrast, typography, layout, and spacing from the screenshot)*
    3.  **Navigability & Interactivity:** How easy it is for users to navigate and interact with controls.
        *(Considers: Link text clarity, visual distinction of links/buttons, target sizes)*
    4.  **Forms & Inputs:** The accessibility of all user input fields.
        *(Considers: Form labels, input grouping (`fieldset`), and visual clarity of form elements)*
    5.  **Media Accessibility:** The accessibility of images, videos, and other media.
        *(Considers: `alt` text for all images)*

    ---

    **Output Format: CRITICAL**
    You MUST produce a single, valid JSON object and nothing else. Do not wrap it in markdown backticks or any other text. The JSON object must have exactly two top-level keys: `scores` and `implementation_plan`.

    -   The `scores` key must be a JSON list of objects.
    -   Each object in the `scores` list MUST have exactly three keys: `category` (string), `score` (integer 0-100), and `feedback` (string).
    -   The `implementation_plan` key must be a single string containing the prioritized, step-by-step plan.

    **Example of the required final JSON structure:**
    ```json
    {{
        "scores": [
            {{
                "category": "Structure & Semantics",
                "score": 75,
                "feedback": "The site uses some semantic tags like `<header>` but is missing a `<main>` landmark, and the heading structure skips from an H2 to an H4. This makes navigation for screen reader users less efficient."
            }},
            {{
                "category": "Readability & Visual Clarity",
                "score": 45,
                "feedback": "Critical issue: The light gray text on a white background in the user testimonial section has a very low contrast ratio, making it unreadable for users with low vision. Body text font size is also small."
            }}
        ],
        "implementation_plan": "1. **(Critical) Fix Color Contrast:** Immediately change the light gray text color in the testimonial section to a darker shade, ensuring a contrast ratio of at least 4.5:1.\\n2. **(High) Correct Heading Structure:** Restructure the page headings to follow a logical order without skipping levels.\\n3. **(High) Add a `<main>` Landmark:** Wrap the primary content of the page in a `<main>` tag to improve navigation."
    }}
    ```
    """
    )
        report_chain = report_prompt | llm | StrOutputParser()
        report_str_output = report_chain.invoke({
            "html_feedback": html_feedback,
            "screenshot_feedback": screenshot_feedback
        })
        print(f"LANGCHAIN_SERVICE: Raw report string from LLM: {report_str_output[:200]}...") # Log raw output

        # The function is typed to return a dict, but the chain returns a string.
        # The parsing to dict is handled in main.py.
        # This function should ideally return the string as produced by the LLM.
        return report_str_output # Return the string for main.py to parse

    except Exception as e:
        print(f"LANGCHAIN_SERVICE_ERROR: An error occurred during accessibility analysis: {e}")
        import traceback
        traceback.print_exc()
        # Return a structured error that main.py can check for
        # Or, re-raise to be caught by a global handler if FastAPI is configured for that.
        # For now, let's return a dict that indicates an error.
        # The calling function in main.py expects a string that it tries to json.loads().
        # So, we should return a string that represents a JSON error object, or handle this differently.
        # Let's return a JSON string representing an error.
        error_report = {
            "scores": [{"category": "Error", "score": 0, "feedback": f"An internal error occurred in Langchain service: {str(e)}"}],
            "implementation_plan": "Analysis could not be completed due to an internal error."
        }
        import json
        return json.dumps(error_report) # Return as JSON string
