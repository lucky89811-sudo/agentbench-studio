from typing import Any

# Curated sandboxed benchmark search index for reproducible evaluations
SEARCH_CACHE: dict[str, list[dict[str, str]]] = {
    "laptop": [
        {
            "title": "Top Ultraportables 2026",
            "url": "https://valid-source.org/tech/laptops-2026",
            "snippet": "Acer Swift Go 14: $799.99, 16GB LPDDR5 RAM, weight 1.30kg, 14-inch OLED. Lenovo Yoga Slim 7: $949.00, 16GB RAM, weight 1.40kg, AMD Ryzen 7. ASUS Zenbook 14 OLED: $1049.99, 16GB RAM, weight 1.28kg, Intel Core Ultra 7."
        },
        {
            "title": "Best Budget Laptops Under $1200",
            "url": "https://valid-source.org/reviews/budget-ultrabooks",
            "snippet": "Dell Inspiron 14 Plus: $899.99, 16GB RAM, 1.6kg. HP Pavilion Plus 14: $829.99, 16GB RAM, 1.44kg. All models deliver over 10 hours battery life."
        }
    ],
    "clinical": [
        {
            "title": "Phase 3 Trial of Novel Anti-PD1 in Melanoma",
            "url": "https://valid-source.org/medical/oncology-pd1-2025",
            "snippet": "In the randomized phase 3 trial (NCT04512399), overall survival was 71.4% at 24 months in the combination arm vs 58.2% with monotherapy (hazard ratio 0.68, 95% CI 0.53-0.87, p=0.002)."
        }
    ],
    "financial": [
        {
            "title": "Q3 2026 Tech Sector Earnings & Metrics",
            "url": "https://valid-source.org/finance/tech-q3-2026",
            "snippet": "Cloud division revenue reached $12.4B, an increase of 28% year-over-year. Operating margin expanded by 210 bps to 32.5%. Free cash flow was $4.1B."
        }
    ]
}

def execute_web_search(query: str, max_results: int = 3) -> dict[str, Any]:
    """Executes a sandboxed web search query."""
    q_lower = query.lower()
    results = []
    
    # Check cache keys
    for key, cached_items in SEARCH_CACHE.items():
        if key in q_lower:
            results.extend(cached_items)

    if not results:
        # Default realistic synthetic response
        results = [
            {
                "title": f"Search Results for: {query[:40]}",
                "url": "https://valid-source.org/knowledge/search-result",
                "snippet": f"Verified documentation and benchmark data concerning '{query}'. Data current as of 2026."
            }
        ]

    return {
        "query": query,
        "results": results[:max_results],
        "total_results": len(results)
    }
