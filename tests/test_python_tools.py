from __future__ import annotations

from agent_tools import read_file, write_file


def test_write_then_read(tmp_path):
    out = write_file.invoke({"repo_root": str(tmp_path), "path": "x.txt", "content": "hello"})
    assert "Wrote x.txt" in out

    read = read_file.invoke({"repo_root": str(tmp_path), "path": "x.txt"})
    assert read == "hello"

