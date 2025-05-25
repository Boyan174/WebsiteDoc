from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models.analysis import AnalysisRequest, AnalysisReport
from services.firecrawl_service import scrape_website
from services.langchain_service import analyze_accessibility
import json
import asyncio # Added for SSE

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Your React app's URL & potential other dev ports
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


async def stream_analysis_progress(url: str):
    """
    Generator function to stream analysis progress.
    """
    current_step = 0
    total_steps = 6 # Define total steps for progress calculation

    async def send_progress(message: str, step_name: str, progress_override: int = -1, error: bool = False, data: dict = None):
        nonlocal current_step
        current_step += 1
        progress = progress_override if progress_override != -1 else int((current_step / total_steps) * 100)
        if error:
            current_step -=1 # Don't count error step in progress
        
        payload = {
            "type": "progress" if not data else "report",
            "message": message,
            "step_name": step_name,
            "progress": min(progress, 100), # Cap progress at 100
            "error": error
        }
        if data:
            payload["data"] = data
        
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(0.1) # Small delay to ensure messages are sent

    try:
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Initializing analysis...', 'step_name': 'Initialization', 'progress': 0, 'error': False})}\n\n"
        await asyncio.sleep(0.1)

        # Step 1: Scrape website
        await asyncio.sleep(0.1) # give time for first message to be sent
        async for update in send_progress("Taking Screenshot and Structure of your website...", "Scraping Website"):
            yield update
        
        print(f"STREAM_PY: Scraping URL: {url}")
        scraped_data = await scrape_website(url)
        if not scraped_data or not scraped_data.get("html"):
            print(f"STREAM_PY_ERROR: Failed to scrape website or HTML content missing. URL: {url}")
            async for update in send_progress("Failed to scrape the website or critical content (HTML) is missing.", "Scraping", error=True):
                yield update
            # yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to scrape the website or critical content (HTML) is missing.'})}\n\n"
            return # Stop further processing

        html_content = scraped_data.get("html")
        screenshot_base64 = scraped_data.get("screenshot")

        async for update in send_progress("Website scraped. HTML and screenshot (if available) retrieved.", "Scraping Complete"):
            yield update

        if not html_content:
            print(f"STREAM_PY_ERROR: HTML content is None after scraping. URL: {url}")
            async for update in send_progress("HTML content could not be retrieved after scraping.", "Data Validation", error=True):
                yield update
            # yield f"data: {json.dumps({'type': 'error', 'message': 'HTML content could not be retrieved after scraping.'})}\n\n"
            return

        if screenshot_base64 is None:
            print(f"STREAM_PY_WARNING: Screenshot data is None. Proceeding with analysis, Langchain service might adapt.")
            async for update in send_progress("Screenshot not available, proceeding with HTML-only analysis.", "Screenshot Status"): # Not an error, but an update
                yield update
        else:
            async for update in send_progress("Screenshot captured successfully.", "Screenshot Status"):
                 yield update


        # Step 2: Analyze accessibility (Langchain service)
        # This is a single call, but Langchain itself has sub-steps. We'll treat it as one major step here for simplicity.
        # For more granular updates from Langchain, Langchain service would need to be a generator too.
        async for update in send_progress("Accessibility is beeing analyzed carefully...", "AI Analysis"):
            yield update
        
        print("STREAM_PY: Calling analyze_accessibility...")
        raw_report_str_from_llm = analyze_accessibility(html_content, screenshot_base64) # This is a sync call
        
        if not raw_report_str_from_llm:
            print("STREAM_PY_ERROR: analyze_accessibility returned None or empty string.")
            async for update in send_progress("Analysis service returned no data.", "AI Analysis", error=True):
                yield update
            # yield f"data: {json.dumps({'type': 'error', 'message': 'Analysis service returned no data.'})}\n\n"
            return

        # Strip markdown fences
        clean_report_str = raw_report_str_from_llm.strip()
        if clean_report_str.startswith("```json"):
            clean_report_str = clean_report_str[7:]
        if clean_report_str.startswith("```"):
            clean_report_str = clean_report_str[3:]
        if clean_report_str.endswith("```"):
            clean_report_str = clean_report_str[:-3]
        clean_report_str = clean_report_str.strip()

        async for update in send_progress("AI analysis complete. Processing report...", "Report Processing"):
            yield update

        try:
            report_dict = json.loads(clean_report_str)
            if isinstance(report_dict.get("scores"), list) and \
               len(report_dict["scores"]) > 0 and \
               report_dict["scores"][0].get("category") == "Error":
                error_message = f"Analysis service error: {report_dict['scores'][0].get('feedback')}"
                print(f"STREAM_PY_ERROR: Langchain service reported an error: {error_message}")
                async for update in send_progress(error_message, "AI Analysis", error=True):
                    yield update
                # yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
                return

            if "scores" in report_dict and isinstance(report_dict["scores"], list):
                for score_item in report_dict["scores"]:
                    if "feedback" not in score_item:
                        score_item["feedback"] = "No specific feedback provided for this category."
            
            analysis_report_model = AnalysisReport(**report_dict)
            
            async for update in send_progress("Report processed successfully. Creating final report.", "Finalizing", progress_override=99):
                yield update
            
            # Send the final report
            # yield f"data: {json.dumps({'type': 'report', 'data': analysis_report_model.model_dump()})}\n\n"
            async for update in send_progress("Analysis complete!", "Complete", progress_override=100, data=analysis_report_model.model_dump()):
                yield update


        except json.JSONDecodeError as e:
            error_message = f"Failed to parse the analysis report from AI service. Raw output: {clean_report_str}"
            print(f"STREAM_PY_ERROR: Failed to parse JSON. Error: {e}. Data: {clean_report_str}")
            async for update in send_progress(error_message, "Report Processing", error=True):
                yield update
            # yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
        except Exception as e_model:
            error_message = f"Failed to structure the analysis report. Error: {e_model}"
            print(f"STREAM_PY_ERROR: Failed to create AnalysisReport model. Error: {e_model}")
            async for update in send_progress(error_message, "Report Processing", error=True):
                yield update
            # yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"

    except Exception as e:
        error_message = f"An unexpected server error occurred during streaming: {str(e)}"
        print(f"STREAM_PY_ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        # Ensure a final error message is sent to the client if an unexpected exception occurs
        # Need to be careful here as the generator might already be closed.
        # This yield might not reach the client if the connection is broken.
        try:
            # yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
            async for update in send_progress(error_message, "System Error", error=True): # Try to send one last message
                yield update
        except Exception: # Catch if yield fails
            pass


@app.get("/analyze-stream") # Changed from POST to GET
async def analyze_stream_endpoint(url: str): # URL from query param
    """
    Endpoint to analyze a website's accessibility and stream progress.
    Accepts URL as a query parameter.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL query parameter is required.")
    print(f"STREAM_PY: Received stream request for URL: {url}")
    return StreamingResponse(stream_analysis_progress(url), media_type="text/event-stream")

@app.get("/")
def read_root():
    return {"message": "Accessibility Analyzer API is running."}
