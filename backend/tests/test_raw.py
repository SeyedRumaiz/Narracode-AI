import os
import json
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.chains import get_llm, SYSTEM_PROMPT, HUMAN_PROMPT

llm = get_llm("ollama", "ollama", "qwen2.5-coder:1.5b")
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

chain = prompt | llm | StrOutputParser()
res = chain.invoke({
    "code": "def calculate_factorial(n):\n    if n < 0:\n        return None\n    elif n == 0 or n == 1:\n        return 1\n    else:\n        return n * calculate_factorial(n-1)",
    "language": "python",
    "num_questions": 5
})
