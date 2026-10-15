import asyncio
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig

START_URL = "https://www.kiesopmaat.nl/modules/"
OUTPUT = Path("minoren.json")
MAX_PAGES = 300


def is_module_url(url):
    parsed = urlparse(url)
    return (
        parsed.netloc in {
            "www.kiesopmaat.nl",
            "kiesopmaat.nl",
        }
        and parsed.path.startswith("/modules/")
        and parsed.path.endswith("/")
    )


async def main():
    queue = [START_URL]
    visited = set()
    records = []

    async with AsyncWebCrawler(
        config=BrowserConfig(headless=True)
    ) as crawler:

        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)

            if url in visited:
                continue

            visited.add(url)
            print(f"[{len(visited)}] {url}")

            try:
                result = await crawler.arun(url=url)

                if not result.success:
                    print("Mislukt:", url)
                    continue

                markdown = result.markdown
                if not isinstance(markdown, str):
                    markdown = getattr(
                        markdown, "raw_markdown", ""
                    )

                records.append({
                    "url": url,
                    "markdown": markdown,
                })

                links = (result.links or {}).get(
                    "internal", []
                )

                for link in links:
                    href = link.get("href", "")
                    absolute = urljoin(url, href)

                    if (
                        is_module_url(absolute)
                        and absolute not in visited
                        and absolute not in queue
                    ):
                        queue.append(absolute)

                await asyncio.sleep(1)

            except Exception as error:
                print("Fout:", url, error)

    OUTPUT.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

if __name__ == "__main__":
        asyncio.run(main())