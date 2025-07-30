from typing import Optional, Dict

from pydantic import BaseModel, Field


class FileParams(BaseModel):
    file_path: str
    content: str
    permissions: Optional[str] = Field(default="644")


class Resources(BaseModel):
    files: Optional[Dict[str, FileParams]] = {}

    def file_add(self, file_path, content, permissions="644"):
        self.files[file_path] = FileParams(
            file_path=file_path, content=content, permissions=permissions
        )

    def file_str_replace(self, file_path, old_str, new_str):
        if old_str in self.files[file_path].content:
            self.files[file_path].content = self.files[file_path].content.replace(
                old_str, new_str
            )
            return True
        else:
            return False

    def file_full_rewrite(self, file_path, content, permissions):
        self.files[file_path] = FileParams(
            file_path=file_path, content=content, permissions=permissions
        )

    def file_delete(self, file_path):
        if file_path in self.files[file_path]:
            del self.files[file_path]

    def file_exists(self, file_path):
        return file_path in self.files

    def read_file(self, file_path, start_line, end_line):
        _lines = self.files[file_path].content.split("\n")
        return {
            "content": "\n".join(_lines[start_line:end_line]),
            "start_line": start_line,
            "end_line": end_line if end_line is not None else len(_lines),
            "total_lines": len(_lines),
        }

    def read_all_file(self, file_path):
        return self.files[file_path].content
