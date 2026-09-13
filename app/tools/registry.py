from app.tools.sale_tool import SalesTools
from app.tools.customer_tool import CustomerTools
from app.tools.get_deal import DealTool
from app.tools.rag_tools import RAGTools
from app.tools.feedback_tool import FeedbackTools

class ToolRegistry:

    def __init__(self):

        self.tools = {
            "sales": SalesTools(),
            "customer": CustomerTools(),
            "deal": DealTool(),
            "rag": RAGTools(),
            "feedback": FeedbackTools(),
        }

    def get(self, tool_group: str):

        return self.tools.get(tool_group)