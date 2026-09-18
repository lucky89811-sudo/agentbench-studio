import re
from typing import Any
import httpx

PAGE_CACHE: dict[str, str] = {
    "https://valid-source.org/tech/laptops-2026": (
        "# Top Ultraportables 2026 Report\n\n"
        "1. Acer Swift Go 14: Model SFG14-72, $799.99, 16GB LPDDR5X RAM, weight 1.30kg, 14-inch 2.8K OLED.\n"
        "2. Lenovo Yoga Slim 7: Model 14IMH9, $949.00, 16GB RAM, weight 1.40kg, AMD Ryzen 7 8845HS.\n"
        "3. ASUS Zenbook 14 OLED: Model UX3405, $1049.99, 16GB RAM, weight 1.28kg, Intel Core Ultra 7 155H."
    ),
    "https://valid-source.org/medical/oncology-pd1-2025": (
        "# Clinical Trial NCT04512399 Results\n\n"
        "Phase 3 double-blind randomized study in advanced melanoma.\n"
        "Overall survival at 24 months was 71.4% in the combination cohort versus 58.2% in monotherapy (p=0.002)."
    )
}

async def execute_fetch_url(url: str) -> dict[str, Any]:
    """Fetches content from a URL or returns cached benchmark document."""
    clean_url = url.strip().rstrip(".,:;)")
    if clean_url in PAGE_CACHE:
        return {
            "url": clean_url,
            "status_code": 200,
            "content": PAGE_CACHE[clean_url]
        }

    try:
        async with httpx.AsyncClient(headers={"User-Agent": "AgentBench-Studio/1.0"}, timeout=5.0, trust_env=False) as client:
            resp = await client.get(clean_url, follow_redirects=True)
            text = resp.text
            # Strip html tags
            clean_text = re.sub(r"<[^>]+>", " ", text)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            return {
                "url": clean_url,
                "status_code": resp.status_code,
                "content": clean_text[:4000]
            }
    except Exception as e:
        return {
            "is_error": True,
            "url": clean_url,
            "content": f"Fetch Error: {type(e).__name__}: {str(e)}"
        }
