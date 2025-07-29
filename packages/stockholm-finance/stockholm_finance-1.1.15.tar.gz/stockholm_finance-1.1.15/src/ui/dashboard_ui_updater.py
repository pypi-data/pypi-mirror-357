#!/usr/bin/env python3
"""
Dashboard UI Updater for Stockholm Dashboard

This module handles all UI update operations for the dashboard including
panel updates, chunked UI updates, and coordinated UI refresh operations.

Extracted from textual_dashboard.py during modular refactoring.
"""

import asyncio
from typing import Any, Tuple

# Import component classes
from .panel_components import (
    SummaryPanel,
    TickersPanel,
    SectorsPanel,
    MultiTickerPanel,
    PolicySummaryPanel,
)
from .market_components import MarketIndicesPanel
from .tree_view_components import NewsTreeView, PolicyTreeView, PolicyTimelinePanel
from .data_tables import InteractiveTickerTable
from .charts import RealTimeChart


class DashboardUIUpdater:
    """Manages UI update operations for the Stockholm dashboard"""

    def __init__(self, dashboard_app):
        """Initialize with reference to the dashboard app"""
        self.app = dashboard_app

    async def update_ui_panels_chunked(self, analysis_results: Tuple[Any, ...]) -> None:
        """Update UI panels in chunks to maintain responsiveness"""
        # Unpack analysis results
        (
            sentiment_analysis,
            policy_analysis,
            market_health,
            sector_rankings,
            ticker_rankings,
            price_changes,
            current_prices,
            multi_ticker_articles,
            cross_ticker_analysis,
            news_data,
            sentiment_scores,
            sentiment_details,
            market_data,
            market_historical_data,
        ) = analysis_results

        # Chunk 1: Overview tab panels (most critical)
        self.app.update_status("🎨 Updating overview...")
        await self._update_overview_panels(
            sentiment_analysis,
            policy_analysis,
            market_health,
            market_data,
            sector_rankings,
            ticker_rankings,
            price_changes,
            current_prices,
            multi_ticker_articles,
            cross_ticker_analysis,
        )
        await asyncio.sleep(0.05)  # Yield control to UI

        # Chunk 2: Interactive tickers tab
        self.app.update_status("🏆 Updating tickers...")
        await self._update_ticker_panels(ticker_rankings, price_changes, current_prices)
        await asyncio.sleep(0.05)

        # Chunk 3: News tab
        self.app.update_status("📰 Updating news...")
        await self._update_news_panels(
            news_data, sentiment_scores, sentiment_details, sentiment_analysis
        )
        await asyncio.sleep(0.05)

        # Chunk 4: Policy tab
        self.app.update_status("🏛️ Updating policy...")
        await self._update_policy_panels(policy_analysis)
        await asyncio.sleep(0.05)

        # Chunk 5: Market indices tab
        self.app.update_status("📈 Updating indices...")
        await self._update_market_panels(market_data, market_historical_data)
        await asyncio.sleep(0.05)

    async def _update_overview_panels(
        self,
        sentiment_analysis,
        policy_analysis,
        market_health,
        market_data,
        sector_rankings,
        ticker_rankings,
        price_changes,
        current_prices,
        multi_ticker_articles,
        cross_ticker_analysis,
    ) -> None:
        """Update overview tab panels"""
        try:
            summary_panel = self.app.query_one("#summary-panel", SummaryPanel)
            summary_panel.update_data(
                sentiment_analysis, policy_analysis, market_health, market_data
            )
        except Exception:
            pass

        try:
            tickers_panel = self.app.query_one("#tickers-panel", TickersPanel)
            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )
        except Exception:
            pass

        try:
            sectors_panel = self.app.query_one("#sectors-panel", SectorsPanel)
            sectors_panel.update_data(sector_rankings, price_changes)
        except Exception:
            pass

        try:
            multi_ticker_panel = self.app.query_one(
                "#multi-ticker-panel", MultiTickerPanel
            )
            multi_ticker_panel.update_data(multi_ticker_articles, cross_ticker_analysis)
        except Exception:
            pass

    async def _update_ticker_panels(
        self, ticker_rankings, price_changes, current_prices
    ) -> None:
        """Update ticker-related panels"""
        try:
            ticker_table = self.app.query_one(InteractiveTickerTable)
            ticker_table.update_data(ticker_rankings, price_changes, current_prices)
        except Exception:
            pass

    async def _update_news_panels(
        self, news_data, sentiment_scores, sentiment_details, sentiment_analysis
    ) -> None:
        """Update news-related panels"""
        try:
            news_tree = self.app.query_one("#news-tree", NewsTreeView)
            news_tree.update_news(news_data, sentiment_scores, sentiment_details)

            chart = self.app.query_one(RealTimeChart)
            if sentiment_analysis:
                chart.update_sentiment(sentiment_analysis.get("average_sentiment", 0))
        except Exception:
            pass

    async def _update_policy_panels(self, policy_analysis) -> None:
        """Update policy-related panels"""
        try:
            policy_tree = self.app.query_one("#policy-tree", PolicyTreeView)
            policy_tree.update_data(policy_analysis)
        except Exception:
            pass

        try:
            policy_summary_panel = self.app.query_one(
                "#policy-summary-panel", PolicySummaryPanel
            )
            policy_summary_panel.update_data(policy_analysis)
        except Exception:
            pass

        try:
            policy_timeline_panel = self.app.query_one(
                "#policy-timeline-panel", PolicyTimelinePanel
            )
            policy_timeline_panel.update_data(policy_analysis)
        except Exception:
            pass

    async def _update_market_panels(self, market_data, market_historical_data) -> None:
        """Update market-related panels"""
        try:
            indices_panel = self.app.query_one(
                "#market-indices-panel", MarketIndicesPanel
            )
            indices_panel.update_data(market_data, market_historical_data)
        except Exception:
            pass

    def update_all_panels_sync(self, analysis_results: Tuple[Any, ...]) -> None:
        """Update all panels synchronously (for compatibility)"""
        # Unpack analysis results
        (
            sentiment_analysis,
            policy_analysis,
            market_health,
            sector_rankings,
            ticker_rankings,
            price_changes,
            current_prices,
            multi_ticker_articles,
            cross_ticker_analysis,
            news_data,
            sentiment_scores,
            sentiment_details,
            market_data,
            market_historical_data,
        ) = analysis_results

        # Update Overview tab panels
        try:
            summary_panel = self.app.query_one("#summary-panel", SummaryPanel)
            summary_panel.update_data(
                sentiment_analysis, policy_analysis, market_health, market_data
            )
        except Exception:
            pass

        try:
            tickers_panel = self.app.query_one("#tickers-panel", TickersPanel)
            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )
        except Exception:
            pass

        try:
            sectors_panel = self.app.query_one("#sectors-panel", SectorsPanel)
            sectors_panel.update_data(sector_rankings, price_changes)
        except Exception:
            pass

        try:
            multi_ticker_panel = self.app.query_one(
                "#multi-ticker-panel", MultiTickerPanel
            )
            multi_ticker_panel.update_data(multi_ticker_articles, cross_ticker_analysis)
        except Exception:
            pass

        # Update Interactive Tickers tab
        try:
            ticker_table = self.app.query_one(InteractiveTickerTable)
            ticker_table.update_data(ticker_rankings, price_changes, current_prices)
        except Exception:
            pass

        # Update News Tree tab
        try:
            news_tree = self.app.query_one("#news-tree", NewsTreeView)
            news_tree.update_news(news_data, sentiment_scores, sentiment_details)

            chart = self.app.query_one(RealTimeChart)
            if sentiment_analysis:
                chart.update_sentiment(sentiment_analysis.get("average_sentiment", 0))
        except Exception:
            pass

        # Update Policy tab
        try:
            policy_tree = self.app.query_one("#policy-tree", PolicyTreeView)
            policy_tree.update_data(policy_analysis)
        except Exception:
            pass

        try:
            policy_summary_panel = self.app.query_one(
                "#policy-summary-panel", PolicySummaryPanel
            )
            policy_summary_panel.update_data(policy_analysis)
        except Exception:
            pass

        try:
            policy_timeline_panel = self.app.query_one(
                "#policy-timeline-panel", PolicyTimelinePanel
            )
            policy_timeline_panel.update_data(policy_analysis)
        except Exception:
            pass

        # Update Market Indices tab panel
        try:
            indices_panel = self.app.query_one(
                "#market-indices-panel", MarketIndicesPanel
            )
            indices_panel.update_data(market_data, market_historical_data)
        except Exception:
            pass

    def update_basic_ui_panels(
        self, ticker_rankings, price_changes, current_prices, market_data
    ) -> None:
        """Update basic UI panels with available data"""
        # Update tickers panel with available data
        try:
            tickers_panel = self.app.query_one("#tickers-panel", TickersPanel)
            sector_rankings = self.app.data_cache.get("sector_rankings", [])
            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )
        except Exception:
            pass

        # Update summary panel with basic market data
        try:
            summary_panel = self.app.query_one("#summary-panel", SummaryPanel)
            basic_sentiment = {
                "market_mood": "Loading...",
                "average_sentiment": 0.0,
            }
            summary_panel.update_data(basic_sentiment, {}, {}, market_data)
        except Exception:
            pass

    def update_news_ui_panels(self, news_data, basic_policy_analysis) -> None:
        """Update news-related UI panels"""
        # Update news tree with available data
        try:
            news_tree = self.app.query_one("#news-tree", NewsTreeView)
            # Get sentiment data from cache if available
            sentiment_scores = self.app.data_cache.get("sentiment_scores", {})
            sentiment_details = self.app.data_cache.get("sentiment_details", [])
            news_tree.update_news(news_data, sentiment_scores, sentiment_details)
        except Exception:
            pass

        # Update policy tree if government data is available
        if basic_policy_analysis:
            try:
                policy_tree = self.app.query_one("#policy-tree", PolicyTreeView)
                policy_tree.update_data(basic_policy_analysis)
            except Exception:
                pass
