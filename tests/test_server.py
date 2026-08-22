import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from mcp.types import TextContent


@pytest.fixture
def server_module(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-api-key")
    return importlib.import_module("server")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "core_function_name"),
    [
        ("analyze_image", "core_analyze_image"),
        ("analyze_image_json", "core_analyze_image_json"),
    ],
)
async def test_vision_tools_read_binary_resources(
    monkeypatch, server_module, tool_name, core_function_name
):
    image_data = b"image data"
    context = SimpleNamespace(
        read_resource=AsyncMock(
            return_value=[SimpleNamespace(content=image_data, mime_type="image/png")]
        )
    )
    core_function = Mock(return_value=TextContent(type="text", text="analysis"))
    monkeypatch.setattr(server_module, core_function_name, core_function)

    result = await getattr(server_module, tool_name)(
        image="resource://uploaded-image",
        ctx=context,
    )

    context.read_resource.assert_awaited_once_with("resource://uploaded-image")
    assert core_function.call_args.kwargs["input_source"] == image_data
    assert result.text == "analysis"
