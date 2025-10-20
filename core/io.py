from typing import List

def read_brands(path: str) -> List[str]:
    """ Read brands file : (one per line) and returns them as a list"""
    brands: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                brands.append(line)
    return brands

def read_domains(path: str):
    """Reads domain file: (one per line) and returns them as a list"""
    domains = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  
                domains.append(line)
    return domains

