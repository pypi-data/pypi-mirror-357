import mlflow
from vinagent.mlflow import autolog

# Enable Vinagent autologging
autolog.autolog()

# Optional: Set tracking URI and experiment
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Vinagent")


from langchain_together import ChatTogether 
from vinagent.agent.agent import Agent
from dotenv import load_dotenv
load_dotenv()

llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
)

agent = Agent(
    description="You are an Expert who can answer any general questions.",
    llm = llm,
    skills = [
        "Searching information from external search engine\n",
        "Summarize the main information\n"],
    tools = ['vinagent.tools.websearch_tools'],
    tools_path = 'templates/tools.json',
    memory_path = 'templates/memory.json'
)

result = agent.invoke(query="What is the weather today in Ha Noi?")
