
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.io import read_brands, read_domains
from core.normalize import normalize_domain_to_token
from core.similarity import calculate_similarity

BRANDS_PATH  = "data/brands.txt"
DOMAINS_PATH = "data/domains.txt"

def main():
    brands = read_brands(BRANDS_PATH)
    domains = read_domains(DOMAINS_PATH)

    print(f"Loaded {len(brands)} brands, {len(domains)} domains\n")

    for i, dom in enumerate(domains, start=1):
        token = normalize_domain_to_token(dom)

        best_brand = None
        best_score = 0.0
        for b in brands:
            s = calculate_similarity(token, b)
            if s > best_score:
                best_score = s
                best_brand = b

        if best_score >= 0.85:
            label = "HIGH"
        elif best_score >= 0.70:
            label = "MEDIUM"
        else:
            label = "LOW"

        print(f"[{i}] {dom:28} → token='{token:20}' | brand='{best_brand:12}' | sim={best_score:.2f} | {label}")

if __name__ == "__main__":
    main()
