# DTU University Info MCP Server

## Mô tả
MCP server để query thông tin tuyển sinh Đại học Duy Tân từ dataset JSON có sẵn.

## Lý do chọn
Dataset này có sẵn từ dự án chatbot tuyển sinh mình đã xây dựng trước đó. Server giúp Claude có thể trả lời câu hỏi tuyển sinh chính xác thay vì dựa vào kiến thức chung. Đây cũng là ứng dụng thực tế của MCP — kết nối Claude với domain knowledge cụ thể.

## Tools có sẵn
- `search_university_info` — Tìm thông tin chung về trường (lịch sử, xếp hạng...)
- `list_schools` — Liệt kê các trường/khoa trực thuộc
- `search_major` — Tìm ngành học theo từ khóa
- `get_major_detail` — Chi tiết ngành (mục tiêu, cơ hội việc làm...)
- `list_training_programs` — Danh sách chương trình đào tạo

## Cài đặt
```bash
pip install -r requirements.txt
```

## Cấu hình Claude Code
Sửa file `C:\Users\<tên>\.claude.json`:
```json
"dtu-info": {
  "type": "stdio",
  "command": "C:\\Users\\<tên>\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
  "args": ["D:\\path\\to\\server.py"],
  "env": {}
}
```

## Ví dụ sử dụng
- "Liệt kê các trường thuộc DTU"
- "Ngành Công nghệ thông tin tại DTU có những chuyên ngành gì?"
- "Cơ hội việc làm của ngành Kỹ thuật phần mềm?"