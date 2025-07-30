from typing import Self

class CountData:
  files: int
  lines: int
  chars: int

  def __init__(self: Self) -> None:
    self.files = 0
    self.lines = 0
    self.chars = 0

  def add_file(self: Self, file_path: str) -> None:
    self.files += 1
    with open(file_path, 'r') as file:
      content = file.read()
      self.lines += content.count('\n') + 1
      self.chars += len(content)
