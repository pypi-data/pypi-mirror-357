from szetop_backend_code_gen_mcp import describe_image_from_file


async def test_code_gen():
    filepath = "E:\\Code\\ai-demo-api\\doc\\项目管理列表.png"
    return await describe_image_from_file(filepath)
