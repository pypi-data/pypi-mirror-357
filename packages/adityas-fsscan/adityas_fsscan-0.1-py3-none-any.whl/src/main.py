from os import getcwd

from src.count_data import CountData
from src.file_scanner import scan_files

def continuous_input() -> list[str]:
  inputs: list[str] = []
  last: str = " "

  while last:
    last = input("Enter a value (or press Enter to finish): ")
    if last:
      inputs.append(last)

  return inputs

def main() -> None:
  cwd: str = getcwd()
  print(f"Current working directory: {cwd}")
  
  print("Enter file extensions to scan: ")
  print("Please avoid leading dots", end=" ")
  print("(e.g., write 'py' instead of '.py').")
  extensions: set[str] = set(continuous_input())

  print()

  print("Enter directories to ignore (optional): ")
  print("Please avoid leading slashes", end=" ")
  print("(e.g., write 'node_modules' instead of '/node_modules').")
  ignore: set[str] = set(continuous_input())

  counts: dict[str, CountData] = scan_files(
    cwd,
    extensions,
    ignore,
  )

  for ext in extensions:
    data: CountData = counts[ext]
    print(f"Data for {ext}:")
    print(f"  Files: {data.files}")
    print(f"  Lines: {data.lines}")
    print(f"  Chars: {data.chars}")

if __name__ == "__main__":
  main()

