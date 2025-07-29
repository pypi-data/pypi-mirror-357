# import smolagents
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
import os

# bring in MCP Client Side libraries
from mcp import StdioServerParameters

def main():
    # Specify OpenAI via LiteLLM
    model = LiteLLMModel(
        model_id="openai/gpt-3.5-turbo",
        api_base="https://api.openai.com/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # online STDIO stuff to get to MCP tools
    server_parameters = StdioServerParameters(
        command="mcp-server",
        args=[],
        env=None
    )

    # Run the agent using the MCP tools (chat functionality)
    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
        # agent.run("What was IBM last stock price?")
        # agent.run("Who are the core leaders at Walmart?")
        agent.run("give me quarterly income statement for apple")
        
if __name__ == "__main__":
    main()