#!/usr/bin/env python3
"""
Dashboard Background Processor for Stockholm Dashboard

This module handles all background processing operations for the dashboard including
throttled updates, background data fetching, and streaming data management.

Extracted from textual_dashboard.py during modular refactoring.
"""

import time

from .panel_components import TickersPanel, SummaryPanel
from .tree_view_components import NewsTreeView


class DashboardBackgroundProcessor:
    """Manages background processing operations for the Stockholm dashboard"""

    def __init__(self, dashboard_app):
        """Initialize with reference to the dashboard app"""
        self.app = dashboard_app
        self.data_cache = dashboard_app.data_cache

        # Initialize throttling timestamps
        self._last_ticker_update = 0
        self._last_bg_update = {}
        self._last_price_refresh = 0
        self._last_news_refresh = 0
        self._last_market_refresh = 0

    def is_trading_hours(self) -> bool:
        """Check if current time is during US stock market trading hours"""
        import datetime
        import pytz

        # Get current time in Eastern Time (US stock market timezone)
        et_tz = pytz.timezone("US/Eastern")
        now_et = datetime.datetime.now(et_tz)

        # Check if it's a weekday (Monday=0, Sunday=6)
        if now_et.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check if it's during trading hours (9:30 AM - 4:00 PM ET)
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now_et <= market_close

    async def update_news_data_only(self) -> None:
        """Update only news and sentiment data (24/7)"""
        try:
            self.app.update_status("📰 Updating news...")

            # Import here to avoid circular imports
            from ..data.cached_data_fetcher import cached_get_news_data

            # Fetch fresh news data
            news_data = cached_get_news_data()
            self.data_cache["news_data"] = news_data

            # Update news tree if it exists
            try:
                news_tree = self.app.query_one("#news-tree", NewsTreeView)
                sentiment_scores = self.data_cache.get("sentiment_scores", {})
                sentiment_details = self.data_cache.get("sentiment_details", [])
                news_tree.update_news(news_data, sentiment_scores, sentiment_details)
            except Exception:
                pass

            self.app.update_status("✅ News updated")

        except Exception as e:
            self.app.update_status(f"❌ News update failed: {str(e)}")

    async def update_market_data_if_trading_hours(self) -> None:
        """Update market data only during trading hours"""
        if not self.is_trading_hours():
            self.app.update_status("🌙 Market closed - skipping price updates")
            return

        try:
            self.app.update_status("📈 Updating market data...")

            # Import here to avoid circular imports
            from ..data.cached_data_fetcher import cached_get_market_data_optimized

            # Fetch fresh market data
            market_data = cached_get_market_data_optimized()
            self.data_cache["market_data"] = market_data

            # Update summary panel if it exists
            try:
                summary_panel = self.app.query_one("#summary-panel", SummaryPanel)
                sentiment_analysis = self.data_cache.get("sentiment_analysis", {})
                policy_analysis = self.data_cache.get("policy_analysis", {})
                market_health = self.data_cache.get("market_health", {})
                summary_panel.update_data(
                    sentiment_analysis, policy_analysis, market_health, market_data
                )
            except Exception:
                pass

            self.app.update_status("✅ Market data updated")

        except Exception as e:
            self.app.update_status(f"❌ Market update failed: {str(e)}")

    def update_streaming_ticker_display(self) -> None:
        """Update ticker display with streaming data - throttled for responsiveness"""
        try:
            current_time = time.time()

            # Throttle updates to every 2 seconds
            if current_time - self._last_ticker_update < 2.0:
                return

            self._last_ticker_update = current_time

            # Update tickers panel with current data
            tickers_panel = self.app.query_one("#tickers-panel", TickersPanel)
            ticker_rankings = self.data_cache.get("ticker_rankings", [])
            price_changes = self.data_cache.get("price_changes", {})
            current_prices = self.data_cache.get("current_prices", {})
            sector_rankings = self.data_cache.get("sector_rankings", [])

            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )

            # Also update interactive ticker table if on that tab
            try:
                from .data_tables import InteractiveTickerTable

                ticker_table = self.app.query_one(InteractiveTickerTable)
                ticker_table.update_data(ticker_rankings, price_changes, current_prices)
            except Exception:
                pass  # Table might not be visible

        except Exception:
            pass  # Fail silently to avoid disrupting streaming

    def on_background_data_update(self, data_type: str, identifier: str) -> None:
        """Handle background data updates for hot loading with throttling"""
        try:
            # Throttle background updates to avoid overwhelming the UI
            current_time = time.time()

            # Only update each data type every 500ms
            if data_type in self._last_bg_update:
                if current_time - self._last_bg_update[data_type] < 0.5:
                    return

            self._last_bg_update[data_type] = current_time

            # DISABLE throttled refresh calls to prevent display corruption
            # These are commented out to prevent cascading UI updates
            # if data_type == "prices":
            #     self.app.call_later(self.refresh_price_panels_throttled)
            # elif data_type == "news":
            #     self.app.call_later(self.refresh_news_panels_throttled)
            # elif data_type == "market":
            #     self.app.call_later(self.refresh_market_panels_throttled)

        except Exception:
            # Handle errors silently to avoid disrupting background updates
            pass

    def refresh_price_panels_throttled(self) -> None:
        """Refresh panels that depend on price data with throttling"""
        try:
            # Throttle price panel updates
            current_time = time.time()

            if current_time - self._last_price_refresh < 1.0:  # Max once per second
                return

            self._last_price_refresh = current_time

            # Get fresh price data from cache
            from ..data.cached_data_fetcher import (
                get_multiple_ticker_current_prices,
                get_multiple_ticker_prices,
            )
            from ..data.data_fetcher import MAJOR_TICKERS

            tickers = MAJOR_TICKERS[:50]

            price_changes = get_multiple_ticker_prices(tickers)
            current_prices = get_multiple_ticker_current_prices(tickers)

            # Update cache
            self.data_cache.update(
                {
                    "price_changes": price_changes,
                    "current_prices": current_prices,
                }
            )

            # Update tickers panel if it exists
            try:
                tickers_panel = self.app.query_one("#tickers-panel", TickersPanel)
                ticker_rankings = self.data_cache.get("ticker_rankings", [])
                sector_rankings = self.data_cache.get("sector_rankings", [])
                tickers_panel.update_data(
                    sector_rankings, ticker_rankings, price_changes, current_prices
                )
            except Exception:
                pass

        except Exception:
            pass

    def refresh_news_panels_throttled(self) -> None:
        """Refresh panels that depend on news data with throttling"""
        try:
            # Throttle news panel updates
            current_time = time.time()

            if current_time - self._last_news_refresh < 2.0:  # Max once per 2 seconds
                return

            self._last_news_refresh = current_time

            # Update news tree if it exists
            try:
                news_tree = self.app.query_one("#news-tree", NewsTreeView)
                news_data = self.data_cache.get("news_data", [])
                sentiment_scores = self.data_cache.get("sentiment_scores", {})
                sentiment_details = self.data_cache.get("sentiment_details", [])
                news_tree.update_news(news_data, sentiment_scores, sentiment_details)
            except Exception:
                pass

        except Exception:
            pass

    def refresh_market_panels_throttled(self) -> None:
        """Refresh panels that depend on market data with throttling"""
        try:
            # Throttle market panel updates
            current_time = time.time()

            if (
                current_time - self._last_market_refresh < 1.5
            ):  # Max once per 1.5 seconds
                return

            self._last_market_refresh = current_time

            # Get fresh market data
            from ..data.cached_data_fetcher import cached_get_market_data_optimized

            market_data = cached_get_market_data_optimized()
            self.data_cache["market_data"] = market_data

            # Update summary panel if it exists
            try:
                summary_panel = self.app.query_one("#summary-panel", SummaryPanel)
                sentiment_analysis = self.data_cache.get("sentiment_analysis", {})
                policy_analysis = self.data_cache.get("policy_analysis", {})
                market_health = self.data_cache.get("market_health", {})
                summary_panel.update_data(
                    sentiment_analysis, policy_analysis, market_health, market_data
                )
            except Exception:
                pass

        except Exception:
            pass

    def cleanup_background_processes(self) -> None:
        """Cleanup when dashboard is closed"""
        try:
            if self.app.background_fetcher:
                self.app.background_fetcher.stop_background_fetching()
                self.app.update_status("🛑 Proactive cache system stopped")
        except Exception:
            pass
