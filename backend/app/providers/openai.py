import openai
from typing import List, Dict, Any
from .base import BaseLLMProvider, SuggestionRequest, SuggestionResponse, ReportRequest, ReportResponse
from app.core.config import OPENAI_API_KEY


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    async def suggest_category(self, request: SuggestionRequest) -> SuggestionResponse:
        """Suggest transaction type and category based on description"""
        
        prompt = f"""
        Analyze this transaction description and suggest the most appropriate type and category.
        
        Description: "{request.description}"
        
        Available types: income, expense
        Available categories: salary, carryover, groceries, eating_out
        
        Return your response in this exact format:
        Type: [income or expense]
        Category: [one of the available categories]
        Confidence: [0.0 to 1.0]
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        
        # Parse response
        lines = content.strip().split('\n')
        type_line = next((line for line in lines if line.startswith('Type:')), 'Type: expense')
        category_line = next((line for line in lines if line.startswith('Category:')), 'Category: groceries')
        confidence_line = next((line for line in lines if line.startswith('Confidence:')), 'Confidence: 0.5')
        
        suggested_type = type_line.split(':', 1)[1].strip()
        suggested_category = category_line.split(':', 1)[1].strip()
        confidence = float(confidence_line.split(':', 1)[1].strip())
        
        return SuggestionResponse(
            suggested_type=suggested_type,
            suggested_category=suggested_category,
            confidence=confidence
        )
    
    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """Generate monthly spending report"""
        
        # Format transactions for the prompt
        transactions_text = "\n".join([
            f"- {tx.get('date', '')}: {tx.get('type', '')} - {tx.get('category', '')} - ${tx.get('amount', 0)} - {tx.get('description', '')}"
            for tx in request.transactions
        ])
        
        prompt = f"""
        Generate a friendly monthly spending report for {request.month} based on these transactions:
        
        {transactions_text}
        
        Provide:
        1. A brief summary of spending patterns
        2. Top expense categories
        3. Any notable insights or recommendations
        4. Overall financial health assessment
        
        Keep it conversational and helpful, like a personal finance assistant.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        report_text = response.choices[0].message.content
        
        # Extract insights (simple implementation)
        insights = [
            "Monthly spending analysis completed",
            f"Analyzed {len(request.transactions)} transactions",
            "Generated personalized recommendations"
        ]
        
        return ReportResponse(
            report_text=report_text,
            insights=insights
        )
