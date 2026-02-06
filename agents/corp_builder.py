from utils.get_model import get_model
from pydantic_ai import Agent
from pydantic import BaseModel
import asyncio

class Corporation(BaseModel):
    name: str
    founded: int
    business_model: str
    employee_count: int
    revenue: int
    growth_rate: float
    publicly_traded: bool
    headquarters: str
    
system_prompt = """
Its 2028. Your task is to create a corporation based on the given prompt and following rules:
- The corporation must be something that could realistically exist in 2028
"""

_agent = Agent(
    model=get_model("creative"),
    system_prompt=system_prompt,
    output_type=Corporation
)

variants = [
"""
- This corporation has recently grew from a small startup to blazingly fast growing scaleup
- It has gained significant media attention due their unique way of doing business
- They are focusing on a very significant global problem and are expressing bold claims of their innovations
- Culture is almost cult-like and very demanding
""",
"""
- This corporation is a huge corporation that has been around for a while
- It has claimed stable but significant market share on several markets
- They want to look innovative and modern, but suffer from bureaucracy and internal politics
- They are also facing some legal challenges
- Corporation is publicly traded
- Employees are well-paid and even they have high criterias for new hires, work is not too demanding, but thats exactly the problem.
""",
"""
- This corporation is working on a very traditional industry,
- They grew family business into a very successful company
- They struggle to adapt to new technologies and ways of working
- Culture is very traditional and hierarchical
"""
]

async def run() -> list[Corporation]:
    results = await asyncio.gather(*[_agent.run(prompt) for prompt in variants])
    return [result.output for result in results]
        