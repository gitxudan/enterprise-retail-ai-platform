import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_menu():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server.server.retail_mcp_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            tools = tools_response.tools

            print("\nAvailable Retail MCP Tools:")
            for i, tool in enumerate(tools, start=1):
                print(f"{i}. {tool.name}")
                print(f"   {tool.description}")

            while True:
                choice = input("\nSelect tool number, or 0 to exit: ")

                if choice == "0":
                    break

                try:
                    selected_tool = tools[int(choice) - 1]
                    args = {}

                    properties = selected_tool.inputSchema.get("properties", {})
                    for param_name in properties.keys():
                        value = input(f"Enter {param_name}: ")
                        args[param_name] = value

                    result = await session.call_tool(
                        selected_tool.name,
                        arguments=args
                    )

                    print("\n--- Result ---")
                    for content in result.content:
                        print(content.text)

                except Exception as e:
                    print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_menu())