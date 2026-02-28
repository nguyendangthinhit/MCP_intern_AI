#!/usr/bin/env python3
"""
DTU University Info MCP Server
Query thông tin tuyển sinh Đại học Duy Tân từ file JSON local
"""

import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

DATA_FILE = r"D:\py\git\intern_ai\dtu-mcp\data_thong_tin_chung.json"

app = Server("dtu-university-info")

_cached_data = None

def fetch_data() -> dict:
    global _cached_data
    if _cached_data is not None:
        return _cached_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        _cached_data = json.load(f)
    return _cached_data


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_university_info",
            description="Tìm kiếm thông tin chung về Đại học Duy Tân (lịch sử, lãnh đạo, cơ sở, xếp hạng...)",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Từ khóa tìm kiếm, ví dụ: 'lịch sử', 'xếp hạng', 'cơ sở vật chất'"
                    }
                },
                "required": ["keyword"]
            }
        ),
        types.Tool(
            name="list_schools",
            description="Liệt kê tất cả các trường/khoa thuộc Đại học Duy Tân",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="search_major",
            description="Tìm kiếm thông tin ngành học theo tên ngành hoặc tên trường",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Tên ngành hoặc tên trường cần tìm, ví dụ: 'Công nghệ thông tin', 'Kinh tế'"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_major_detail",
            description="Lấy thông tin chi tiết của một ngành học (giới thiệu, mục tiêu, chương trình, cơ hội việc làm)",
            inputSchema={
                "type": "object",
                "properties": {
                    "school_name": {
                        "type": "string",
                        "description": "Tên trường/khoa"
                    },
                    "major_name": {
                        "type": "string",
                        "description": "Tên ngành học"
                    }
                },
                "required": ["major_name"]
            }
        ),
        types.Tool(
            name="list_training_programs",
            description="Liệt kê các chương trình đào tạo (Đại học, Thạc sĩ, Tiến sĩ)",
            inputSchema={
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "description": "Bậc đào tạo: 'đại học', 'thạc sĩ', 'tiến sĩ'. Để trống để lấy tất cả."
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        data = fetch_data()
    except Exception as e:
        return [types.TextContent(type="text", text=f"Lỗi khi tải dữ liệu: {str(e)}")]

    if name == "search_university_info":
        keyword = arguments["keyword"].lower()
        results = []
        for item in data.get("thong_tin_dai_hoc_duy_tan", []):
            noi_dung = str(item.get("Nội dung", "")).lower()
            thong_tin = str(item.get("Thông tin", "")).lower()
            if keyword in noi_dung or keyword in thong_tin:
                results.append(item)
        if not results:
            return [types.TextContent(type="text", text=f"Không tìm thấy thông tin với từ khóa: '{arguments['keyword']}'")]
        output = f"Tìm thấy {len(results)} kết quả cho '{arguments['keyword']}':\n\n"
        for item in results[:5]:
            output += f"📌 {item.get('Nội dung', '')}\n{item.get('Thông tin', '')}\n\n"
        return [types.TextContent(type="text", text=output)]

    elif name == "list_schools":
        schools = data.get("truong_khoa_truc_thuoc", [])
        output = f"Đại học Duy Tân có {len(schools)} trường/khoa trực thuộc:\n\n"
        for i, school in enumerate(schools, 1):
            name_val = school.get("Tên Trường", school.get("Trường", str(school)))
            output += f"{i}. {name_val}\n"
        return [types.TextContent(type="text", text=output)]

    elif name == "search_major":
        query = arguments["query"].lower()
        mo_ta_nganh = data.get("mo_ta_nganh", {})
        results = []
        for school, majors in mo_ta_nganh.items():
            if query in school.lower():
                results.append(f"🏫 Trường: {school} - có {len(majors)} ngành")
                continue
            for major_name, details in majors.items():
                if query in major_name.lower():
                    results.append(f"📚 Ngành: {major_name} | Trường: {school}")
        if not results:
            return [types.TextContent(type="text", text=f"Không tìm thấy ngành/trường với từ khóa: '{arguments['query']}'")]
        output = f"Tìm thấy {len(results)} kết quả:\n\n" + "\n".join(results[:10])
        return [types.TextContent(type="text", text=output)]

    elif name == "get_major_detail":
        major_name = arguments["major_name"].lower()
        school_name = arguments.get("school_name", "").lower()
        mo_ta_nganh = data.get("mo_ta_nganh", {})
        for school, majors in mo_ta_nganh.items():
            if school_name and school_name not in school.lower():
                continue
            for mname, details in majors.items():
                if major_name in mname.lower():
                    output = f"📚 Ngành: {mname}\n🏫 Trường: {school}\n\n"
                    for item in details:
                        for key, val in item.items():
                            output += f"**{key}:**\n{val}\n\n"
                    return [types.TextContent(type="text", text=output)]
        return [types.TextContent(type="text", text=f"Không tìm thấy thông tin ngành: '{arguments['major_name']}'")]

    elif name == "list_training_programs":
        level = arguments.get("level", "").lower()
        programs = data.get("chương_trình_đào_tạo_trong_và_sau_đại_học", [])
        output = "Các chương trình đào tạo tại Đại học Duy Tân:\n\n"
        for item in programs:
            bac = str(item.get("Bậc", item.get("bac", ""))).lower()
            if not level or level in bac:
                output += f"• {json.dumps(item, ensure_ascii=False)}\n"
        return [types.TextContent(type="text", text=output)]

    return [types.TextContent(type="text", text=f"Tool không tồn tại: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())