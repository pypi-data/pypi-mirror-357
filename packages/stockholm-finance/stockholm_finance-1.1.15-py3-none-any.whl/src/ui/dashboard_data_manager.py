#!/usr/bin/env python3
"""
Dashboard Data Manager for Stockholm Dashboard

This module handles all data management operations for the dashboard including
data fetching, caching, analysis coordination, and data preparation for UI updates.

Extracted from textual_dashboard.py during modular refactoring.
"""

import asyncio
from datetime import datetime
from typing import Any, Tuple


class DashboardDataManager:
    """Manages data operations for the Stockholm dashboard"""

    def __init__(self, dashboard_app):
        """Initialize with reference to the dashboard app"""
        self.app = dashboard_app
        self.data_cache = dashboard_app.data_cache

    async def load_initial_data_once(self) -> None:
        """Load data once without cascading refreshes"""
        try:
            self.app.update_status("📊 Loading data...")

            # Load data using existing methods but without auto-refresh
            analysis_results = await self.update_dashboard_data()

            # Update UI with the loaded data
            if analysis_results:
                # Add missing parameters that UI updater expects
                news_data = self.data_cache.get("news_data", [])
                sentiment_scores = self.data_cache.get("sentiment_scores", {})
                sentiment_details = self.data_cache.get("sentiment_details", [])
                market_data = self.data_cache.get("market_data", {})
                market_historical_data = self.data_cache.get(
                    "market_historical_data", {}
                )

                # Create extended tuple with all parameters UI updater expects
                extended_results = analysis_results + (
                    news_data,
                    sentiment_scores,
                    sentiment_details,
                    market_data,
                    market_historical_data,
                )
                await self.app.ui_updater.update_ui_panels_chunked(extended_results)

            self.app.update_status("✅ Stockholm dashboard ready!")
        except Exception as e:
            self.app.update_status(f"❌ Error loading data: {str(e)}")

    async def update_dashboard_data(self) -> None:
        """Update all dashboard data - optimized for hot loading"""
        try:
            # Skip full reload if we're in progressive loading mode
            if self.data_cache.get("loading_phase") in ["critical", "secondary"]:
                self.app.update_status("🔄 Completing analysis...")
            else:
                self.app.update_status("🔄 Refreshing data...")

            # Import here to avoid circular imports
            from ..core.financial_analyzer import analyze_all_data, fetch_all_data

            # Use cached data if available, otherwise fetch fresh
            if "news_data" in self.data_cache and "government_data" in self.data_cache:
                news_data = self.data_cache["news_data"]
                government_data = self.data_cache["government_data"]
                market_data = self.data_cache.get("market_data", {})
                market_historical_data = self.data_cache.get(
                    "market_historical_data", {}
                )
            else:
                # Fetch new data
                (
                    news_data,
                    _,
                    government_data,
                    _,
                    market_data,
                    market_historical_data,
                ) = fetch_all_data()

            # Analyze data
            analysis_results = analyze_all_data(
                news_data, government_data, market_data, market_historical_data
            )

            # Unpack analysis results
            (
                sentiment_analysis,
                policy_analysis,
                market_health,
                sector_rankings,
                ticker_rankings,
                price_changes,
                current_prices,
                company_names,
                sentiment_scores,
                sentiment_details,
                multi_ticker_articles,
                cross_ticker_analysis,
                _,
            ) = analysis_results

            # Store data for other tabs
            self.data_cache.update(
                {
                    "sentiment_analysis": sentiment_analysis,
                    "policy_analysis": policy_analysis,
                    "market_health": market_health,
                    "sector_rankings": sector_rankings,
                    "ticker_rankings": ticker_rankings,
                    "price_changes": price_changes,
                    "current_prices": current_prices,
                    "company_names": company_names,
                    "sentiment_scores": sentiment_scores,
                    "sentiment_details": sentiment_details,
                    "multi_ticker_articles": multi_ticker_articles,
                    "cross_ticker_analysis": cross_ticker_analysis,
                    "market_data": market_data,
                    "market_historical_data": market_historical_data,
                    "news_data": news_data,
                    "government_data": government_data,
                }
            )

            # Update reactive variables
            self.app.current_sentiment = sentiment_analysis.get("average_sentiment", 0)
            self.app.last_update = datetime.now().strftime("%H:%M:%S")

            self.app.update_status(f"✅ Updated at {self.app.last_update}")

            return analysis_results

        except Exception as e:
            # Handle errors gracefully
            self.app.notify(f"Error updating data: {str(e)}", severity="error")
            self.app.update_status(f"❌ Error: {str(e)}")
            raise

    async def load_progressive_data(self) -> Tuple[Any, ...]:
        """Load data progressively with UI updates"""
        try:
            # Import here to avoid circular imports
            from ..core.financial_analyzer import analyze_all_data, fetch_all_data

            # Use cached data if available, otherwise fetch fresh
            if "news_data" in self.data_cache and "government_data" in self.data_cache:
                news_data = self.data_cache["news_data"]
                government_data = self.data_cache["government_data"]
                market_data = self.data_cache.get("market_data", {})
                market_historical_data = self.data_cache.get(
                    "market_historical_data", {}
                )
            else:
                # Fetch new data
                (
                    news_data,
                    _,
                    government_data,
                    _,
                    market_data,
                    market_historical_data,
                ) = fetch_all_data()

            # Phase 1: Analyze core data (lighter processing)
            self.app.update_status("🧠 Analyzing sentiment...")
            await asyncio.sleep(0.05)  # Yield control to UI

            # Analyze data in chunks
            analysis_results = analyze_all_data(
                news_data, government_data, market_data, market_historical_data
            )

            # Unpack results
            (
                sentiment_analysis,
                policy_analysis,
                market_health,
                sector_rankings,
                ticker_rankings,
                price_changes,
                current_prices,
                company_names,
                sentiment_scores,
                sentiment_details,
                multi_ticker_articles,
                cross_ticker_analysis,
                _,
            ) = analysis_results

            # Phase 2: Update cache incrementally
            self.app.update_status("💾 Updating cache...")
            await asyncio.sleep(0.05)  # Yield control to UI

            # Store data for other tabs
            self.data_cache.update(
                {
                    "sentiment_analysis": sentiment_analysis,
                    "policy_analysis": policy_analysis,
                    "market_health": market_health,
                    "sector_rankings": sector_rankings,
                    "ticker_rankings": ticker_rankings,
                    "price_changes": price_changes,
                    "current_prices": current_prices,
                    "company_names": company_names,
                    "sentiment_scores": sentiment_scores,
                    "sentiment_details": sentiment_details,
                    "multi_ticker_articles": multi_ticker_articles,
                    "cross_ticker_analysis": cross_ticker_analysis,
                    "market_data": market_data,
                    "market_historical_data": market_historical_data,
                    "news_data": news_data,
                    "government_data": government_data,
                }
            )

            # Update reactive variables
            self.app.current_sentiment = sentiment_analysis.get("average_sentiment", 0)
            self.app.last_update = datetime.now().strftime("%H:%M:%S")
            self.app.update_status(f"✅ Updated at {self.app.last_update}")

            return analysis_results

        except Exception as e:
            # Handle errors gracefully
            self.app.notify(f"Error updating data: {str(e)}", severity="error")
            self.app.update_status(f"❌ Error: {str(e)}")
            raise

    def update_basic_panels(self) -> None:
        """Update basic panels with price data during progressive loading"""
        try:
            price_changes = self.data_cache.get("price_changes", {})
            current_prices = self.data_cache.get("current_prices", {})
            company_names = self.data_cache.get("company_names", {})
            market_data = self.data_cache.get("market_data", {})

            # Use existing ticker rankings if available, otherwise create basic ones
            ticker_rankings = self.data_cache.get("ticker_rankings", [])

            # If no ticker rankings yet and we have price data, create basic ones
            if not ticker_rankings and price_changes:
                ticker_rankings = []
                for i, ticker in enumerate(list(price_changes.keys())[:20]):
                    ticker_rankings.append(
                        {
                            "ticker": ticker,
                            "company_name": company_names.get(ticker, ticker),
                            "current_price": current_prices.get(ticker, 0.0),
                            "price_change": price_changes.get(ticker, 0.0),
                            "sentiment": 0.0,  # Will be updated later
                            "rank": i + 1,
                            "articles": 0,  # Will be updated later
                        }
                    )
                self.data_cache["ticker_rankings"] = ticker_rankings

            return ticker_rankings, price_changes, current_prices, market_data

        except Exception as e:
            self.app.notify(
                f"Error updating basic panels: {str(e)}", severity="warning"
            )
            return [], {}, {}, {}

    def update_news_panels(self) -> None:
        """Update news-related panels during progressive loading"""
        try:
            news_data = self.data_cache.get("news_data", [])
            government_data = self.data_cache.get("government_data", [])

            # Create basic policy analysis structure if government data is available
            basic_policy_analysis = None
            if government_data:
                basic_policy_analysis = {
                    "articles": government_data,
                    "categories": {},
                    "sentiment_summary": {"average_sentiment": 0.0},
                }

            return news_data, basic_policy_analysis

        except Exception as e:
            self.app.notify(f"Error updating news panels: {str(e)}", severity="warning")
            return [], None

    def update_cache_statistics(self) -> None:
        """Update cache statistics display"""
        try:
            from ..data.cache_manager import cache_manager

            stats = cache_manager.get_cache_stats()

            # Create cache status message
            cache_files = stats.get("cache_files", 0)
            cache_size = stats.get("cache_size_mb", 0)
            refresh_queue = stats.get("refresh_queue_size", 0)

            # Show cache performance in status
            if refresh_queue > 0:
                cache_status = f"🔄 Proactive Cache: {cache_files} files ({cache_size:.1f}MB) | {refresh_queue} refreshing"
            else:
                cache_status = f"✅ Proactive Cache: {cache_files} files ({cache_size:.1f}MB) | All fresh"

            # Update status bar with cache info (only if not showing other important messages)
            current_status = getattr(self.app, "_current_status", "")
            if not any(
                keyword in current_status.lower()
                for keyword in ["loading", "error", "analyzing"]
            ):
                self.app.update_status(cache_status)

        except Exception:
            pass  # Fail silently
