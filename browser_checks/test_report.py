"""Real Chromium against a generated offline HTML report; records its actual interactions."""

from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from reconproof.pipeline import run

ROOT = Path(__file__).resolve().parents[1]


def test_report_review_and_mobile(tmp_path):
    out = tmp_path / "report"
    report = run(
        ROOT / "examples/ledger.csv",
        ROOT / "examples/target.xlsx",
        ROOT / "examples/rules.json",
        out,
    )
    artifacts = ROOT / "test-results" / "browser"
    artifacts.mkdir(parents=True, exist_ok=True)
    errors, requests = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            record_video_dir=str(artifacts),
            record_video_size={"width": 1440, "height": 1000},
            reduced_motion="reduce",
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url))
        page.goto((out / "report.html").as_uri())
        expect(
            page.get_by_role("heading", name="Two exports. Every difference explained.")
        ).to_be_visible()
        expect(page.locator("#shown")).to_have_text("8 groups")
        page.screenshot(path=str(artifacts / "overview.png"), full_page=True)
        page.get_by_role("button", name="View source INV-004 EUR", exact=True).click()
        expect(page.locator("#detail-count")).to_have_text("3 source rows")
        expect(page.locator("#source-rows .source")).to_have_count(3)
        expect(page.locator("#source-rows")).to_contain_text("20.00 EUR")
        expect(page.locator("#source-rows")).to_contain_text("30.00 EUR")
        expect(page.locator("#source-rows")).to_contain_text("50.00 EUR")
        page.screenshot(path=str(artifacts / "duplicate-evidence.png"))
        # Brief pauses are only for readable demonstration footage, not synchronization.
        page.wait_for_timeout(1500)
        page.get_by_role("button", name="Close", exact=True).click()
        page.get_by_label("Find a reference", exact=True).fill("INV-002")
        expect(page.locator("#results tr")).to_have_count(1)
        expect(page.locator("#results")).to_contain_text("1.10")
        page.get_by_role("button", name="View source INV-002 EUR", exact=True).click()
        expect(page.locator("#detail-count")).to_have_text("2 source rows")
        page.wait_for_timeout(1500)
        page.keyboard.press("Escape")
        expect(page.locator("#detail")).not_to_be_visible()
        page.get_by_label("Find a reference", exact=True).fill("")
        page.get_by_label("Outcome", exact=True).select_option("MATCH")
        expect(page.locator("#shown")).to_have_text("3 groups")
        page.get_by_label("Outcome", exact=True).select_option("all")
        expect(page.locator("#results tr")).to_have_count(len(report["results"]))
        page.get_by_role("button", name="Inspect all source rows", exact=True).click()
        expect(page.locator("#detail-count")).to_have_text("25 source rows")
        expect(page.locator("#source-rows")).to_contain_text(
            "KEY_MUST_BE_NONEMPTY_TEXT"
        )
        page.get_by_role("button", name="Close", exact=True).click()
        page.get_by_label("Outcome", exact=True).select_option("exceptions")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(artifacts / "mobile.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors
        assert not any(url.startswith(("https://", "http://")) for url in requests)
        video = page.video
        context.close()
        video.save_as(str(artifacts / "review-demo.webm"))
        browser.close()
