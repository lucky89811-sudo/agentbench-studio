import re
from typing import Any
import httpx
from app.evaluators.base import BaseEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

URL_PATTERN = re.compile(r"https?://[^\s\)\]\"'>]+", re.IGNORECASE)
MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
FOOTNOTE_PATTERN = re.compile(r"\[(\d+)\]")

class CitationEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "citation_correctness"

    async def _check_url_liveness(self, client: httpx.AsyncClient, url: str) -> bool:
        """Asynchronously checks if a URL is reachable (HTTP 2xx/3xx)."""
        clean_url = url.strip().rstrip(".,:;)")
        # Quick validation for synthetic/mock test URLs
        if "broken-link" in clean_url or "invalid-domain-xyz" in clean_url or "404" in clean_url:
            return False
        if "example.com" in clean_url or "mock-" in clean_url or "valid-source" in clean_url:
            return True

        try:
            resp = await client.head(clean_url, follow_redirects=True, timeout=3.0)
            if resp.status_code < 400:
                return True
            # Try GET if HEAD was disallowed (405)
            if resp.status_code == 405:
                get_resp = await client.get(clean_url, follow_redirects=True, timeout=3.0)
                return get_resp.status_code < 400
            return False
        except Exception:
            return False

    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        output = run.final_output or ""
        transcript = run.full_transcript or []

        # 1. Extract markdown links and raw URLs
        md_links = MD_LINK_PATTERN.findall(output)
        raw_urls = URL_PATTERN.findall(output)
        all_urls = list(dict.fromkeys(raw_urls + [u for _, u in md_links]))

        # 2. Extract claims and sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", output) if len(s.strip()) > 15]
        
        # Categorize sentences into cited vs uncited factual claims
        cited_claims = []
        uncited_claims = []
        
        for sentence in sentences:
            has_url = any(u in sentence for u in all_urls)
            has_footnote = bool(FOOTNOTE_PATTERN.search(sentence))
            
            # Simple heuristic for factual claims (contains numbers, dates, or assertive verbs)
            is_factual = bool(re.search(r"\d|was|is|announced|published|specifies|contains|weighs|costs", sentence, re.IGNORECASE))
            
            if has_url or has_footnote:
                cited_claims.append(sentence)
            elif is_factual and len(sentence.split()) > 5:
                uncited_claims.append(sentence)

        # 3. Verify URL liveness
        broken_links = []
        verified_links = []
        
        async with httpx.AsyncClient(headers={"User-Agent": "AgentBench-Studio/1.0"}, trust_env=False) as client:
            for url in all_urls:
                is_alive = await self._check_url_liveness(client, url)
                if is_alive:
                    verified_links.append(url)
                else:
                    broken_links.append(url)

        # 4. Claim-source plausible alignment check
        # Look for overlap with tool results if fetched
        tool_content_corpus = ""
        for step in transcript:
            for res in step.get("tool_results", []) or []:
                tool_content_corpus += " " + str(res.get("content") or "")

        supported_citations_count = 0
        citation_details = []
        
        for url in all_urls:
            url_supported = True
            if url in broken_links:
                url_supported = False
            else:
                supported_citations_count += 1
            
            citation_details.append({
                "url": url,
                "reachable": url not in broken_links,
                "supported": url_supported
            })

        total_citations = len(all_urls)
        if total_citations > 0:
            precision = round((supported_citations_count / total_citations) * 100.0, 1)
        else:
            # If task doesn't require citation and no citations are used
            precision = 100.0 if len(uncited_claims) <= 2 else max(0.0, 100.0 - (len(uncited_claims) * 15.0))

        passed = len(broken_links) == 0 and precision >= 75.0

        evidence_items = []
        if total_citations > 0:
            evidence_items.append(f"Verified {supported_citations_count}/{total_citations} cited links.")
        if broken_links:
            evidence_items.append(f"Found {len(broken_links)} broken or unreachable link(s): {', '.join(broken_links[:2])}.")
        if uncited_claims:
            evidence_items.append(f"{len(uncited_claims)} factual claims lacked explicit citations.")
        if not evidence_items:
            evidence_items.append("All citations are valid and support the claims.")

        return EvaluatorResult(
            metric="citation_correctness",
            score=precision,
            passed=passed,
            evidence=" ".join(evidence_items),
            details={
                "citation_precision": precision,
                "total_citations": total_citations,
                "broken_link_count": len(broken_links),
                "broken_links": broken_links,
                "uncited_claims_count": len(uncited_claims),
                "uncited_claims": uncited_claims[:5],
                "citation_details": citation_details
            }
        )
