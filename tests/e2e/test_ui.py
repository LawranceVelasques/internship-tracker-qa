"""End-to-end tests: start the app on a real port and drive the page in Chromium."""
import os
import threading
from datetime import date

import pytest
from werkzeug.serving import make_server

from app import create_app

playwright_api = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def browser():
    with playwright_api.sync_playwright() as p:
        try:
            b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        except Exception as exc:  # no browser installed on this machine
            pytest.skip(f"Chromium not available: {exc}")
        yield b
        b.close()


@pytest.fixture
def base_url():
    app = create_app(":memory:", today=date(2027, 3, 1))
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def page(browser, base_url):
    pg = browser.new_page()
    pg.goto(base_url)
    pg.get_by_test_id("stats").get_by_text("application(s)").wait_for()
    yield pg
    pg.close()


def add(page, company, position, status="Wishlist", applied_date=""):
    page.get_by_test_id("company").fill(company)
    page.get_by_test_id("position").fill(position)
    page.get_by_test_id("status").select_option(status)
    if applied_date:
        page.get_by_test_id("applied-date").fill(applied_date)
    page.get_by_test_id("submit").click()


def test_empty_state(page):
    expect = playwright_api.expect
    expect(page.get_by_test_id("stats")).to_have_text("0 application(s) · interview rate 0.0%")
    expect(page.get_by_test_id("row")).to_have_count(0)


def test_add_application_shows_in_table_and_clears_form(page):
    expect = playwright_api.expect
    add(page, "SIRCLO", "QA Intern", "Applied", "2027-02-10")
    row = page.get_by_test_id("row")
    expect(row).to_have_count(1)
    expect(row).to_contain_text("SIRCLO")
    expect(row).to_contain_text("2027-02-10")
    expect(page.get_by_test_id("company")).to_have_value("")
    expect(page.get_by_test_id("stats")).to_have_text("1 application(s) · interview rate 0.0%")


def test_missing_required_field_shows_error_and_adds_nothing(page):
    expect = playwright_api.expect
    page.get_by_test_id("position").fill("QA Intern")
    page.get_by_test_id("submit").click()
    expect(page.get_by_test_id("error")).to_contain_text("company is required")
    expect(page.get_by_test_id("row")).to_have_count(0)


def test_future_date_is_rejected_in_ui(page):
    expect = playwright_api.expect
    add(page, "Acme", "Data Intern", "Applied", "2027-12-31")
    expect(page.get_by_test_id("error")).to_contain_text("applied_date cannot be in the future")


def test_delete_removes_row(page):
    expect = playwright_api.expect
    add(page, "Acme", "BA Intern")
    expect(page.get_by_test_id("row")).to_have_count(1)
    page.get_by_test_id("delete").click()
    expect(page.get_by_test_id("row")).to_have_count(0)
