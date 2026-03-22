from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
You are an intelligent web search agent.

User request: {user_input}

Decide:
1. Platform (youtube / google)
2. Category (F1, ANIME, MOVIES, etc)
3. Build a clean search query

Return ONLY the search query.
"""
)

def agent_reason(user_input):
    chain = prompt | llm
    result = chain.invoke({"user_input": user_input})
    return result.content
