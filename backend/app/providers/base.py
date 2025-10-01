from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel


class SuggestionRequest(BaseModel):
    description: str


class SuggestionResponse(BaseModel):
    suggested_type: str
    suggested_category: str
    confidence: float


class ReportRequest(BaseModel):
    month: str
    transactions: List[Dict[str, Any]]


class ReportResponse(BaseModel):
    report_text: str
    insights: List[str]


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def suggest_category(self, request: SuggestionRequest) -> SuggestionResponse:
        """Suggest transaction type and category based on description"""
        pass
    
    @abstractmethod
    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """Generate monthly spending report"""
        pass
