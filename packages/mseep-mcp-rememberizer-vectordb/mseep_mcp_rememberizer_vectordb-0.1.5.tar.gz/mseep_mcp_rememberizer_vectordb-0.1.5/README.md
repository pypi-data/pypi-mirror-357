# Rememberizer Vector Store MCP Server

A [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) server for LLMs to interact with [Rememberizer Vector Store](https://docs.rememberizer.ai/developer/vector-stores).

## Components

### Resources

The server provides access to your Vector Store's documents in [Rememberizer](https://docs.rememberizer.ai/).

### Tools

1. `rememberizer_vectordb_search`

    - Search for documents in your Vector Store by semantic similarity
    - Input:
        - `q` (string): Up to a 400-word sentence to find semantically similar chunks of knowledge
        - `n` (integer, optional): Number of similar documents to return (default: 5)

2. `rememberizer_vectordb_agentic_search`

    - Search for documents in your Vector Store by semantic similarity with LLM Agents augmentation
    - Input:
        - `query` (string): Up to a 400-word sentence to find semantically similar chunks of knowledge. This query can be augmented by our LLM Agents for better results.
        - `n_chunks` (integer, optional): Number of similar documents to return (default: 5)
        - `user_context` (string, optional): The additional context for the query. You might need to summarize the conversation up to this point for better context-awared results (default: None)

3. `rememberizer_vectordb_list_documents`

    - Retrieves a paginated list of all documents
    - Input:
        - `page` (integer, optional): Page number for pagination, starts at 1 (default: 1)
        - `page_size` (integer, optional): Number of documents per page, range 1-1000 (default: 100)
    - Returns: List of documents

4. `rememberizer_vectordb_information`

    - Get information of your Vector Store
    - Input: None required
    - Returns: Vector Store information details

5. `rememberizer_vectordb_create_document`

    - Create a new document for your Vector Store
    - Input:
        - `text` (string): The content of the document
        - `document_name` (integer, optional): A name for the document

6. `rememberizer_vectordb_delete_document`

    - Delete a document from your Vector Store
    - Input:
        - `document_id` (integer): The ID of the document you want to delete

7. `rememberizer_vectordb_modify_document`

    - Change the name of your Vector Store document
    - Input:
        - `document_id` (integer): The ID of the document you want to modify

## Installation

**Via mcp-get.com:** Use mcp-get command to automatically set up the Rememberizer MCP Vector Store MCP Server.

```bash
npx @michaellatman/mcp-get@latest install mcp-rememberizer-vectordb
```

**Via SkyDeck AI Helper App:** If you have SkyDeck AI Helper app installed, you can search for "Rememberizer" and install the mcp-rememberizer-vectordb.

![SkyDeck AI Helper App installation](https://docs.rememberizer.ai/~gitbook/image?url=https%3A%2F%2F2952947711-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FyNqpTh7Mh66N0RnO0k24%252Fuploads%252FFNtwkzA6eyC1yDrmOqjv%252Fimage.png%3Falt%3Dmedia%26token%3Dccb0dd6a-dde5-41a4-b148-cbc11ddcf5a9&width=768&dpr=2&quality=100&sign=839d22ba&sv=2)

## Configuration

### Environment Variables

The following environment variables are required:

-   `REMEMBERIZER_VECTOR_STORE_API_KEY`: Your Rememberizer Vector Store API token

You can register an API key by create your own [Vector Store in Rememberizer](https://docs.rememberizer.ai/developer/vector-stores).

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "rememberizer": {
      "command": "uvx",
      "args": ["mcp-rememberizer-vectordb"],
      "env": {
        "REMEMBERIZER_VECTOR_STORE_API_KEY": "your_rememberizer_api_token"
      }
    },
}
```

## Usage with SkyDeck AI Helper App

Add the env `REMEMBERIZER_VECTOR_STORE_API_KEY` to `mcp-rememberizer-vectordb`.

![SkyDeck AI Helper App Configuration](https://docs.rememberizer.ai/~gitbook/image?url=https%3A%2F%2F2952947711-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FyNqpTh7Mh66N0RnO0k24%252Fuploads%252FaaRJQXKzlN8o4jEW5y17%252Fimage.png%3Falt%3Dmedia%26token%3Dd0641bd9-082e-46c9-a1f6-4c4d4de9b144&width=768&dpr=2&quality=100&sign=c5a1c835&sv=2)

## License

This MCP server is licensed under the [Apache License 2.0](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the Apache License. For more details, please see the [LICENSE](LICENSE) file in the project repository.


