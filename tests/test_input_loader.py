from __future__ import annotations

from src.input_loader import load_manual_text, load_multiple_files, load_txt_file


class FakeUpload:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data
        self._position = 0

    def read(self) -> bytes:
        data = self._data[self._position :]
        self._position = len(self._data)
        return data

    def seek(self, position: int) -> None:
        self._position = position


def test_load_manual_text_returns_standard_columns():
    frame = load_manual_text("Apple opened an office in London.", category="technology")

    assert list(frame.columns) == ["id", "source_name", "text", "language", "category"]
    assert frame.iloc[0]["source_name"] == "manual_input"
    assert frame.iloc[0]["category"] == "technology"


def test_load_txt_file_reads_uploaded_bytes():
    upload = FakeUpload("note.txt", b"Microsoft works with schools in Jordan.")

    frame = load_txt_file(upload, category="education")

    assert len(frame) == 1
    assert frame.iloc[0]["source_name"] == "note.txt"
    assert "Microsoft" in frame.iloc[0]["text"]
    assert frame.iloc[0]["category"] == "education"


def test_load_multiple_files_warns_on_unsupported_type():
    upload = FakeUpload("image.png", b"not supported")

    frame, warnings = load_multiple_files([upload])

    assert frame.empty
    assert warnings
    assert "Unsupported file type" in warnings[0]
