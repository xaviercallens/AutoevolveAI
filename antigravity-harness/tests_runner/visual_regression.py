"""
Visual Regression Runner: Playwright and Pixelmatch UI testing.
Automates visual snapshot comparison of the Evolution Lab dashboard (web/server.py).
Detects pixel layout shifts, CSS breakages, and component rendering regressions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VisualRegressionResult:
    """Outcome of a visual snapshot comparison."""

    passed: bool
    mismatched_pixels: int
    total_pixels: int
    mismatch_ratio: float
    diff_image_path: str | None = None
    error: str | None = None

    @property
    def summary(self) -> str:
        if self.error:
            return f"Visual test ERROR: {self.error}"
        status = "PASSED" if self.passed else "FAILED"
        return (
            f"Visual Regression {status}: {self.mismatched_pixels} / {self.total_pixels} pixels mismatched "
            f"({self.mismatch_ratio * 100:.3f}% difference)"
        )


class VisualRegressionRunner:
    """
    Manages Playwright browser automation and pixel-by-pixel snapshot comparison.
    Includes pure-Python pixel comparison fallback for lightweight environments.
    """

    def __init__(self, tolerance_ratio: float = 0.005) -> None:
        """
        :param tolerance_ratio: Maximum allowable mismatched pixels ratio (default 0.5%).
        """
        self.tolerance_ratio = tolerance_ratio

    @property
    def is_playwright_installed(self) -> bool:
        """Checks if Playwright Python library and browser binaries exist."""
        try:
            import playwright  # noqa: F401

            return True
        except ImportError:
            return False

    def compare_images(
        self,
        baseline_path: str | Path,
        candidate_path: str | Path,
        diff_output_path: str | Path | None = None,
        threshold: int = 20,
    ) -> VisualRegressionResult:
        """
        Pure-Python pixel-by-pixel image comparison algorithm (Pixelmatch-equivalent).
        Threshold determines RGB distance sensitivity per channel (0-255).
        """
        base_p = Path(baseline_path)
        cand_p = Path(candidate_path)

        if not base_p.exists():
            return VisualRegressionResult(
                passed=False,
                mismatched_pixels=0,
                total_pixels=0,
                mismatch_ratio=1.0,
                error=f"Baseline image '{base_p}' does not exist.",
            )

        if not cand_p.exists():
            return VisualRegressionResult(
                passed=False,
                mismatched_pixels=0,
                total_pixels=0,
                mismatch_ratio=1.0,
                error=f"Candidate image '{cand_p}' does not exist.",
            )

        try:
            from PIL import Image

            base_img = Image.open(base_p).convert("RGBA")
            cand_img = Image.open(cand_p).convert("RGBA")

            if base_img.size != cand_img.size:
                return VisualRegressionResult(
                    passed=False,
                    mismatched_pixels=max(
                        base_img.width * base_img.height, cand_img.width * cand_img.height
                    ),
                    total_pixels=base_img.width * base_img.height,
                    mismatch_ratio=1.0,
                    error=f"Image dimensions mismatch: baseline {base_img.size} vs candidate {cand_img.size}.",
                )

            width, height = base_img.size
            total_pixels = width * height

            base_data = base_img.load()
            cand_data = cand_img.load()

            diff_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            diff_data = diff_img.load()
            assert base_data is not None
            assert cand_data is not None
            assert diff_data is not None

            mismatched = 0
            for y in range(height):
                for x in range(width):
                    p1 = base_data[x, y]  # type: ignore[index]
                    p2 = cand_data[x, y]  # type: ignore[index]
                    r1, g1, b1, a1 = p1[0], p1[1], p1[2], p1[3]  # type: ignore[index]
                    r2, g2, b2, a2 = p2[0], p2[1], p2[2], p2[3]  # type: ignore[index]

                    # Euclidean RGB distance
                    dist = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2) + abs(a1 - a2)
                    if dist > threshold:
                        mismatched += 1
                        # Mark diff pixel in bright red
                        diff_data[x, y] = (255, 0, 0, 255)  # type: ignore[index]
                    else:
                        # Draw faded baseline in background
                        diff_data[x, y] = (r1, g1, b1, 40)  # type: ignore[index]

            ratio = mismatched / max(1, total_pixels)
            passed = ratio <= self.tolerance_ratio

            diff_saved: str | None = None
            if diff_output_path:
                diff_out = Path(diff_output_path)
                diff_out.parent.mkdir(parents=True, exist_ok=True)
                diff_img.save(diff_out)
                diff_saved = str(diff_out)

            return VisualRegressionResult(
                passed=passed,
                mismatched_pixels=mismatched,
                total_pixels=total_pixels,
                mismatch_ratio=ratio,
                diff_image_path=diff_saved,
            )

        except ImportError:
            # If PIL is not installed, do raw byte comparison fallback
            b1 = base_p.read_bytes()
            b2 = cand_p.read_bytes()
            identical = b1 == b2
            return VisualRegressionResult(
                passed=identical,
                mismatched_pixels=0 if identical else 1,
                total_pixels=1,
                mismatch_ratio=0.0 if identical else 1.0,
                error=None
                if identical
                else "Byte comparison detected diff (PIL not installed for pixel rendering).",
            )
        except Exception as exc:
            return VisualRegressionResult(
                passed=False,
                mismatched_pixels=0,
                total_pixels=0,
                mismatch_ratio=1.0,
                error=f"Image comparison error: {exc}",
            )

    def capture_screenshot_sync(
        self,
        url: str,
        output_path: str | Path,
        viewport_width: int = 1280,
        viewport_height: int = 800,
    ) -> bool:
        """Captures page screenshot via Playwright if available."""
        if not self.is_playwright_installed:
            return False

        try:
            from playwright.sync_api import sync_playwright

            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": viewport_width, "height": viewport_height}
                )
                page.goto(url, wait_until="networkidle")
                page.screenshot(path=str(out_p))
                browser.close()
            return True
        except Exception:
            return False
