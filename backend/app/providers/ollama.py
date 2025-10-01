import httpx
import json
from typing import List, Dict, Any
from app.providers.base import BaseLLMProvider, SuggestionRequest, SuggestionResponse, ReportRequest, ReportResponse
from app.core.config import OPENAI_API_KEY # Not used for Ollama, but kept for consistency if switching

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2"  # Google's Gemma3 model (or gemma2 if you have that)
    
    async def suggest_category(self, request: SuggestionRequest) -> SuggestionResponse:
        """Suggest transaction type and category based on description"""
        
        prompt = f"""
        You are an AI assistant that suggests transaction types and categories.
        Given a transaction description, suggest the most appropriate type ('income' or 'expense')
        and category from the following list: {", ".join(["salary", "carryover", "groceries", "eating_out"])}.
        Respond only with a JSON object like:
        {{
            "suggested_type": "expense",
            "suggested_category": "eating_out",
            "confidence": 0.9
        }}
        If you cannot determine, use "other" for category and "expense" for type.
        
        Transaction description: "{request.description}"
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            try:
                # Ollama's /api/generate returns a stream of JSON objects, even for stream=False
                # We need to parse the last one or combine them
                full_response_content = ""
                for line in response.text.strip().split('\n'):
                    if line:
                        full_response_content += json.loads(line).get("response", "")
                
                # Attempt to extract JSON from the full response content
                json_start = full_response_content.find('{')
                json_end = full_response_content.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = full_response_content[json_start:json_end]
                    llm_output = json.loads(json_str)
                else:
                    raise ValueError("Could not find JSON in LLM response")

                return SuggestionResponse(
                    suggested_type=llm_output.get("suggested_type", "expense"),
                    suggested_category=llm_output.get("suggested_category", "other"),
                    confidence=llm_output.get("confidence", 0.5)
                )
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing LLM response: {e}")
                print(f"Full LLM output: {full_response_content}")
                return SuggestionResponse(
                    suggested_type="expense",
                    suggested_category="other",
                    confidence=0.1
                )

    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """Generate a narrative report for a given month's spending"""
        
        # Calculate our own stats (don't rely on LLM for calculations)
        income_total = sum(tx.get('amount', 0) for tx in request.transactions if tx.get('type') == 'income')
        expense_total = sum(tx.get('amount', 0) for tx in request.transactions if tx.get('type') == 'expense')
        net_result = income_total - expense_total
        
        # Group by category for insights
        categories = {}
        for tx in request.transactions:
            if tx.get('type') == 'expense':
                cat = tx.get('category', 'other')
                categories[cat] = categories.get(cat, 0) + tx.get('amount', 0)
        
        top_category = max(categories.items(), key=lambda x: x[1]) if categories else ("none", 0)
        
        # Create a focused prompt with our calculations
        prompt = f"""As a financial advisor, give me a quick rundown of my financial standing for {request.month}.

Here are the facts:
- Total Income: ${income_total:.2f}
- Total Expenses: ${expense_total:.2f}  
- Net Result: ${net_result:.2f}
- Top expense category: {top_category[0]} (${top_category[1]:.2f})
- Number of transactions: {len(request.transactions)}

Write a clear, coherent paragraph (3-4 sentences max) starting with a polite greeting, then give insights about spending patterns and financial health. Be direct and concise like a personal financial advisor."""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "max_tokens": 200  # Keep it short
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                
                full_response_content = ""
                for line in response.text.strip().split('\n'):
                    if line:
                        full_response_content += json.loads(line).get("response", "")
        except Exception as e:
            # Fallback to simple report if LLM fails
            full_response_content = f"""Hello! Here's your financial summary for {request.month}: You earned ${income_total:.2f} and spent ${expense_total:.2f}, resulting in a net {'gain' if net_result > 0 else 'loss'} of ${abs(net_result):.2f}. Your top expense category was {top_category[0]} at ${top_category[1]:.2f}."""

        # Generate insights from our calculations
        insights = [
            f"Total income: ${income_total:.2f}",
            f"Total expenses: ${expense_total:.2f}",
            f"Net result: ${net_result:.2f}",
            f"Top category: {top_category[0]} (${top_category[1]:.2f})"
        ]
        
        return ReportResponse(
            report_text=full_response_content,
            insights=insights,
            summary_data={"income": income_total, "expenses": expense_total, "net": net_result}
        )
