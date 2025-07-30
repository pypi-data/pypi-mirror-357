from NNU_MCP import mcp


def main():
    print("Hello from nnu-mcp!")
    print("server is running...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
