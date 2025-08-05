from mcp import MCPHost, Agent, OpenAIAgentLLM

# You can place this in a .env file too
import os
os.environ["OPENAI_API_KEY"] = "<your-api-key>"

class FungiForgeAgent(Agent):
    def describe(self):
        return {
            "name": "fungi_forge_agent",
            "description": "Controls and monitors the FungiForge IoT growing chamber."
        }

    def get_capabilities(self):
        return {
            "check_temperature": self.check_temperature,
            "capture_image": self.capture_image,
        }

    def check_temperature(self):
        # replace with real sensor read
        return {"temperature": 22.5}

    def capture_image(self):
        # replace with your actual capture function
        from camera.picam import capture_image
        filepath = capture_image()
        return {"image_path": filepath}

# Create the MCP Host
host = MCPHost(
    agents=[FungiForgeAgent()],
    llm=OpenAIAgentLLM(model="gpt-4")  # or gpt-3.5-turbo
)

if __name__ == "__main__":
    host.run_cli()  # CLI interface for now, can add web/chat later