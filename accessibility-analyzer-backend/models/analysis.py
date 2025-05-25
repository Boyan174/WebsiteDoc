from pydantic import BaseModel
from typing import List, Dict

class AnalysisRequest(BaseModel):
    url: str

class AccessibilityFeedback(BaseModel):
    category: str
    score: int
    feedback: str

class AnalysisReport(BaseModel):
    scores: List[AccessibilityFeedback]
    implementation_plan: str
