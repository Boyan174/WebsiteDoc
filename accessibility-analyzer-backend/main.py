from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.analysis import AnalysisRequest, AnalysisReport
from services.firecrawl_service import scrape_website
from services.langchain_service import analyze_accessibility
import json

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=AnalysisReport)
async def analyze(request: AnalysisRequest):
    """
    Endpoint to analyze a website's accessibility.
    """
    try:
        print(f"MAIN_PY: Received request for URL: {request.url}")
        scraped_data = await scrape_website(request.url)
        if not scraped_data or not scraped_data.get("html"): # Check if HTML is present
            print(f"MAIN_PY_ERROR: Failed to scrape website or HTML content missing. URL: {request.url}")
            raise HTTPException(status_code=500, detail="Failed to scrape the website or critical content (HTML) is missing.")

        html_content = scraped_data.get("html")
        screenshot_base64 = scraped_data.get("screenshot") # This can be None if screenshot failed

        if not html_content: # Redundant if checked above, but good for safety
             print(f"MAIN_PY_ERROR: HTML content is None after scraping. URL: {request.url}")
             raise HTTPException(status_code=500, detail="HTML content could not be retrieved.")
        
        # Screenshot can be optional for Langchain if handled there
        if screenshot_base64 is None:
            print(f"MAIN_PY_WARNING: Screenshot data is None. Proceeding with analysis, Langchain service might adapt.")


        print("MAIN_PY: Calling analyze_accessibility...")
        raw_report_str_from_llm = analyze_accessibility(html_content, screenshot_base64)
        print(f"MAIN_PY: Received raw report string from Langchain: {raw_report_str_from_llm[:250]}...") # Log more

        if not raw_report_str_from_llm:
            print("MAIN_PY_ERROR: analyze_accessibility returned None or empty string.")
            raise HTTPException(status_code=500, detail="Analysis service returned no data.")

        # Strip markdown fences if present
        clean_report_str = raw_report_str_from_llm.strip()
        if clean_report_str.startswith("```json"):
            clean_report_str = clean_report_str[7:] # Remove ```json
        if clean_report_str.startswith("```"): # Handle if just ```
            clean_report_str = clean_report_str[3:]
        if clean_report_str.endswith("```"):
            clean_report_str = clean_report_str[:-3]
        clean_report_str = clean_report_str.strip() # Clean up any surrounding whitespace

        print(f"MAIN_PY: Cleaned report string for JSON parsing: {clean_report_str[:250]}...")

        try:
            report_dict = json.loads(clean_report_str)
            # Check if the loaded dict indicates an error from Langchain service itself
            if isinstance(report_dict.get("scores"), list) and \
               len(report_dict["scores"]) > 0 and \
               report_dict["scores"][0].get("category") == "Error":
                print(f"MAIN_PY_ERROR: Langchain service reported an error: {report_dict['scores'][0].get('feedback')}")
                # Propagate a generic error or the specific one if safe
                raise HTTPException(status_code=500, detail=f"Analysis service error: {report_dict['scores'][0].get('feedback')}")
            
            print("MAIN_PY: Successfully parsed report string to dict. Creating AnalysisReport model...")
            # Before creating the model, ensure 'feedback' key exists in each score item,
            # as the LLM might still omit it. If missing, add a default value.
            if "scores" in report_dict and isinstance(report_dict["scores"], list):
                for score_item in report_dict["scores"]:
                    if "feedback" not in score_item:
                        score_item["feedback"] = "No specific feedback provided for this category."
                        print(f"MAIN_PY_WARNING: Added default feedback for category '{score_item.get('category', 'Unknown')}'.")
            
            analysis_report_model = AnalysisReport(**report_dict)
            print("MAIN_PY: AnalysisReport model created successfully.")
            return analysis_report_model
        except json.JSONDecodeError as e:
            print(f"MAIN_PY_ERROR: Failed to parse JSON from Langchain service. Error: {e}. Data: {clean_report_str}")
            raise HTTPException(status_code=500, detail=f"Failed to parse the analysis report from AI service. Raw output: {clean_report_str}")
        except Exception as e_model: # Catch errors during Pydantic model instantiation
            print(f"MAIN_PY_ERROR: Failed to create AnalysisReport model. Error: {e_model}. Dict: {report_dict if 'report_dict' in locals() else 'N/A'}")
            raise HTTPException(status_code=500, detail=f"Failed to structure the analysis report. Error: {e_model}")

    except HTTPException as e: # Re-raise HTTPExceptions to let FastAPI handle them
        raise e 
    except Exception as e:
        print(f"MAIN_PY_ERROR: An unexpected error occurred in /analyze endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Accessibility Analyzer API is running."}
