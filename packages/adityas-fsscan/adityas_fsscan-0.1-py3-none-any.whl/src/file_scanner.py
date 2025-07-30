from os import listdir
from os.path import isfile

from src.count_data import CountData

def scan_files(
  path: str,
  extensions: set[str],
  ignore: set[str],
) -> dict[str, CountData]:
  files: list[str] = []
  path_queue: list[str] = [path]
  counts: dict[str, CountData] = {
    ext: CountData() for ext in extensions
  }

  while path_queue:
    current_path = path_queue.pop(0)
    skip: bool = False

    for ignore_pattern in ignore:
      if f"/{ignore_pattern}/" in current_path:
        skip = True
        break

    if skip:
      continue
    
    if isfile(current_path):
      extension: str = current_path.split('.')[-1]
      if extension not in extensions: continue
      
      counts[extension].add_file(current_path)
      files.append(current_path)
      continue

    path_queue.extend([
      f"{current_path}/{child}"
      for child in listdir(current_path)
    ])
  
  return counts
