import base64
import os
from google import genai
from google.genai import types
from fire import Fire
import httpx
import fastmcp

mcp = fastmcp.FastMCP("Software Advice MCP")

def generate(prompt: str):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        tools = [
            types.Tool(url_context=types.UrlContext()),
            types.Tool(google_search=types.GoogleSearch()),
        ],
        response_mime_type="text/plain",
        thinking_config = types.ThinkingConfig(
            thinking_budget=16384,
        ),
        system_instruction=[
            types.Part.from_text(text="User prefers consise, but informative answers. Be sure to include all relevant information. Always use web search to find the most up-to-date information and documentation. Use as many sources as possible to provide a comprehensive answer."),
        ],
    )

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    match resp.candidates:
        case [candidate]:
            if candidate.content is not None:
                parts = candidate.content.parts
                match parts:
                    case list():
                        main_text = "".join(filter(None, [part.text for part in parts]))
                        if candidate.grounding_metadata is not None:
                            grounding_chunks = candidate.grounding_metadata.grounding_chunks
                            if grounding_chunks:
                                links = [
                                    httpx.get(chunk.web.uri, follow_redirects=True).url
                                    for chunk in grounding_chunks
                                ]
                                main_text += "\n\nSources:\n" + "\n".join(map(str, links))

                        return main_text

                    case _:
                        raise RuntimeError(f"Unexpected content type returned: {parts}")
        case None:
            return "No candidates returned, please try again."
        case _:
            return "Multiple candidates returned, expected only one."



@mcp.tool(
    name="ask_for_latest_advice",
    description="Ask experienced helpful software engineer for an up-to-date advice on a software engineering problem. This person has full access to the very latest information and documentation.",
)
def ask_for_advice(question: str) -> str:
    answer = generate(
        question
    )
    return answer


def main(prompt=None):
    if prompt is None:
        mcp.run(transport="sse", host="127.0.0.1", port=8000, path="/mcp")
    else:
        print(generate(prompt))

if __name__ == "__main__":
    Fire(main)
