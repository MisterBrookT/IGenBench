import asyncio
from pathlib import Path
from typing import Any, Dict, List

from playwright.async_api import async_playwright, Error as PlaywrightError


async def render_d3_html_to_png(
    html: str,
    png_path: Path,
    viewport: Dict[str, int] | None = None,
    timeout_ms: int = 4000,
) -> Dict[str, Any]:
    """
    Render HTML (with D3.js etc.) in headless Chromium and export
    a PNG screenshot of the main infographic area.
    """
    if viewport is None:
        viewport = {"width": 1200, "height": 800}

    console_logs: List[Dict[str, str]] = []
    page_errors: List[str] = []
    result: Dict[str, Any] = {
        "success": False,
        "error": None,
        "console_logs": console_logs,
        "page_errors": page_errors,
        "png_path": None,
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = await browser.new_context(
                viewport=viewport,
                device_scale_factor=3,  # <–– 2x retina style
            )
            page = await context.new_page()

            page.on(
                "console",
                lambda msg: console_logs.append({"type": msg.type, "text": msg.text}),
            )
            page.on(
                "pageerror",
                lambda exc: page_errors.append(str(exc)),
            )

            await page.set_content(html, wait_until="networkidle")

            # Prefer the main infographic container; fall back to body.
            container = None
            try:
                container = await page.wait_for_selector(
                    ".infographic-container", timeout=timeout_ms
                )
            except PlaywrightError:
                try:
                    container = await page.wait_for_selector("body", timeout=timeout_ms)
                except PlaywrightError as e:
                    result["error"] = (
                        f"No suitable container found within {timeout_ms} ms: {e}"
                    )
                    await browser.close()
                    return result

            if not container:
                result["error"] = "No container element found in DOM."
                await browser.close()
                return result

            box = await container.bounding_box()
            if not box:
                result["error"] = "Failed to get bounding box for container."
                await browser.close()
                return result

            await page.screenshot(
                path=str(png_path),
                clip=box,
                omit_background=True,
            )
            result["png_path"] = str(png_path)

            await browser.close()
            result["success"] = True
            return result

    except Exception as e:
        result["error"] = f"Unexpected exception: {e}"
        return result


def render_d3_html_to_png_sync(
    html: str,
    png_path: Path,
    **kwargs,
) -> Dict[str, Any]:
    return asyncio.run(
        render_d3_html_to_png(
            html=html,
            png_path=Path(png_path),
            **kwargs,
        )
    )


if __name__ == "__main__":
    html_code = Path("tmp/output/0_t2c_gemini-2.5-flash.html").read_text(
        encoding="utf-8"
    )

    res = render_d3_html_to_png_sync(
        html=html_code,
        png_path=Path("tmp/output/0_t2c_gemini-2.5-flash.html.png"),
    )

    print("success:", res["success"])
    print("error:", res["error"])
    print("console logs:", res["console_logs"])
    print("page errors:", res["page_errors"])
