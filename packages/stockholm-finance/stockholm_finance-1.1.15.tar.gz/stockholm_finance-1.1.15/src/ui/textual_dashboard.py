#!/usr/bin/env python3
"""
Enhanced Interactive Textual Dashboard for Stockholm
Combines real-time data with advanced interactive features
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import var
from textual.widgets import (
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
)


# Import base components from the new module
from .base_components import LoadingNotification

# Import data table components
from .data_tables import InteractiveTickerTable

# Import chart components
from .charts import RealTimeChart

# Import panel components
from .panel_components import (
    TickerNewsPanel,
    SummaryPanel,
    TickersPanel,
    SectorsPanel,
    MultiTickerPanel,
    PolicySummaryPanel,
)

# Import market components
from .market_components import MarketIndicesPanel

# Import tree view components
from .tree_view_components import NewsTreeView, PolicyTreeView, PolicyTimelinePanel

# Import utility modules
from .dashboard_data_manager import DashboardDataManager
from .dashboard_ui_updater import DashboardUIUpdater
from .dashboard_background_processor import DashboardBackgroundProcessor

# Modal components removed - using 'o' key to open URLs directly


# Note: LoadingNotification and AdjustableDataTable have been moved to base_components.py


# TickerDetailModal has been moved to modals.py
# TickerNewsTable has been moved to data_tables.py
# ArticleTimelineChart has been moved to charts.py


# TickerNewsPanel has been moved to panel_components.py


# InteractiveTickerTable has been moved to data_tables.py

# Orphaned methods have been moved to InteractiveTickerTable class in data_tables.py


# All orphaned methods have been moved to InteractiveTickerTable class in data_tables.py


# NewsTreeView has been moved to tree_view_components.py


# SummaryPanel has been moved to panel_components.py


# NewsPanel has been removed - unused class


# TickersPanel has been moved to panel_components.py


# SectorsPanel has been moved to panel_components.py


# MultiTickerPanel has been moved to panel_components.py


# PolicySummaryPanel has been moved to panel_components.py


# PolicyTreeView has been moved to tree_view_components.py


# PolicyArticleDetailModal has been moved to modals.py


# PolicyTimelinePanel has been moved to tree_view_components.py


# MarketIndexCard and MarketIndicesPanel have been moved to panel_components.py


class StockholmDashboard(App):
    """Stockholm - Enhanced Interactive Dashboard with Tabbed Interface"""

    CSS = """
    #ticker-modal, #article-modal {
        align: center middle;
        width: 80;
        height: 20;
        background: $surface;
        border: thick $primary;
    }

    #modal-title {
        dock: top;
        height: 3;
        content-align: center middle;
    }

    #loading-notification {
        dock: bottom;
        align: right middle;
        width: 30;
        height: 4;
        background: $surface;
        border: solid $primary;
        padding: 1;
        margin: 1;
        opacity: 0;
        transition: opacity 300ms;
    }

    #loading-notification.loading-visible {
        opacity: 1;
        text-style: bold;
        background: $primary;
        color: $text;
    }

    #article-content {
        padding: 1;
        height: 1fr;
    }

    .data-table {
        height: 1fr;
    }

    .chart-container {
        height: 8;
        border: solid $primary;
        margin: 1;
    }

    .controls-panel {
        height: 6;
        border: solid $secondary;
        margin: 1;
    }

    .status-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1;
    }

    .news-item {
        margin: 1;
        padding: 1;
    }

    #left-panel {
        width: 1fr;
        margin: 1;
    }

    #right-panel {
        width: 2fr;
        margin: 1;
    }

    #summary-panel {
        height: 16;
        margin: 1;
        border: solid $primary;
    }

    #tickers-panel {
        height: 1fr;
        margin: 1;
        border: solid $secondary;
        width: 1fr;
    }

    #sectors-panel {
        height: 1fr;
        margin: 1;
        border: solid $secondary;
        width: 1fr;
    }

    #multi-ticker-panel {
        height: 1fr;
        margin: 1;
        border: solid $secondary;
        width: 1fr;
    }

    .details-panel {
        height: 1fr;
        margin: 1;
        border: solid $primary;
        padding: 1;
        width: 1fr;
    }

    #ticker-panels-row {
        height: 15;
        margin: 1;
    }

    .info-panel {
        width: 1fr;
        height: 100%;
        scrollbar-gutter: stable;
        overflow-y: auto;
        margin-right: 1;
        border: solid $primary;
        padding: 1;
    }

    .earnings-panel {
        width: 1fr;
        height: 100%;
        scrollbar-gutter: stable;
        overflow-y: auto;
        margin-left: 1;
        border: solid $secondary;
        padding: 1;
    }

    #ticker-chart {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    .chart-widget {
        height: 15;
        width: 1fr;
        min-width: 80;
        border: solid $primary;
        margin: 1;
        background: $surface;
    }

    .index-chart {
        height: 15;
        width: 1fr;
        min-width: 80;
        border: solid $primary;
        margin: 1;
        background: $surface;
    }

    #market-indices-panel {
        height: 1fr;
        padding: 1;
    }

    MarketIndexCard {
        margin: 1;
        border: solid $secondary;
        height: auto;
        width: 1fr;
        min-width: 90;
    }

    #ticker-details-container {
        width: 2fr;
        height: 1fr;
    }

    #ticker-news-panel {
        height: 1fr;
        padding: 1;
        border: solid $secondary;
    }

    #ticker-news-content {
        height: 1fr;
        scrollbar-gutter: stable;
        overflow-y: auto;
    }

    #ticker-news-table {
        height: 1fr;
        border: solid $secondary;
    }

    .news-table-panel {
        height: 60%;
        border: solid $secondary;
        margin-bottom: 1;
    }

    .timeline-chart-panel {
        height: 40%;
        border: solid $secondary;
    }

    #news-table-container {
        height: 1fr;
        scrollbar-gutter: stable;
        overflow-y: auto;
    }

    #article-timeline-chart {
        height: 1fr;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("1", "switch_tab('overview')", "Overview"),
        Binding("2", "switch_tab('tickers')", "Tickers"),
        Binding("3", "switch_tab('news')", "News"),
        Binding("4", "switch_tab('policy')", "Policy"),
        Binding("5", "switch_tab('indices')", "Indices"),
        Binding("o", "open_article_url", "Open Article URL"),
        Binding("ctrl+e", "export_data", "Export"),
        Binding("ctrl+r", "reset_column_widths", "Reset Column Widths"),
    ]

    TITLE = "🦍🦍💪💪 Stockholm - Interactive Real-time Market Analysis 💎🙌🚀🌙"
    SUB_TITLE = ""

    # Reactive variables for data
    current_sentiment = var(0.0)
    last_update = var("")
    auto_refresh_enabled = var(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_cache = {}
        self.debug_mode = False
        self.current_article_url = None  # Store current article URL for opening
        self.background_fetcher = None  # Will be initialized in on_mount

        # Initialize utility modules
        self.data_manager = DashboardDataManager(self)
        self.ui_updater = DashboardUIUpdater(self)
        self.background_processor = DashboardBackgroundProcessor(self)

    def compose(self) -> ComposeResult:
        """Create the enhanced dashboard layout"""
        yield Header()

        # Loading notification (initially hidden)
        yield LoadingNotification(id="loading-notification")

        with TabbedContent(initial="overview"):
            # Overview Tab - Enhanced summary dashboard
            with TabPane("📊 Overview", id="overview"):
                with Vertical():
                    # Top row - Market summary
                    yield SummaryPanel(id="summary-panel")

                    # Bottom row - Performance metrics in columns
                    with Horizontal():
                        yield TickersPanel(id="tickers-panel")
                        yield SectorsPanel(id="sectors-panel")
                        yield MultiTickerPanel(id="multi-ticker-panel")

            # Interactive Tickers Tab with Right Panel
            with TabPane("🏆 Tickers", id="tickers"):
                with Vertical():
                    with Horizontal():
                        # Left side - Ticker table
                        with Vertical():
                            yield InteractiveTickerTable(classes="data-table")
                        # Right side - Tabbed ticker details
                        with Vertical(id="ticker-details-container"):
                            with TabbedContent(initial="details"):
                                # Details Tab - Info, Earnings, and Chart
                                with TabPane("📊 Details", id="details"):
                                    with Vertical():
                                        # Side-by-side panels for ticker info and earnings
                                        with Horizontal(id="ticker-panels-row"):
                                            yield Static(
                                                "📊 Select a ticker to view detailed information",
                                                id="ticker-info",
                                                classes="info-panel",
                                            )
                                            yield Static(
                                                "📊 Earnings data will appear here",
                                                id="ticker-earnings",
                                                classes="earnings-panel",
                                            )
                                        # Chart underneath the panels - use ArticleTimelineChart for overlays
                                        from .charts import ArticleTimelineChart

                                        yield ArticleTimelineChart(
                                            id="ticker-chart", classes="chart-widget"
                                        )

                                # Headlines Tab - Ticker-specific news articles
                                with TabPane("📰 Headlines", id="ticker-news"):
                                    yield TickerNewsPanel(id="ticker-news-panel")

            # News Tree Tab
            with TabPane("📰 News", id="news"):
                with Horizontal():
                    with Vertical(id="left-panel"):
                        yield NewsTreeView(id="news-tree")
                    with Vertical(id="right-panel"):
                        yield RealTimeChart(classes="chart-container")
                        with ScrollableContainer():
                            yield Static(
                                "Select an article from the tree to view details",
                                id="news-details",
                            )

            # Policy Analysis Tab
            with TabPane("🏛️ Policy", id="policy"):
                with Horizontal():
                    with Vertical():
                        yield PolicyTreeView(id="policy-tree")
                    with Vertical():
                        yield PolicySummaryPanel(id="policy-summary-panel")
                        yield PolicyTimelinePanel(id="policy-timeline-panel")

            # Market Indices Tab
            with TabPane("📈 Indices", id="indices"):
                yield MarketIndicesPanel(id="market-indices-panel")

        yield Static(
            "🔄 Auto-refresh: ON | Last update: Never",
            classes="status-bar",
            id="status-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the dashboard with progressive data loading"""
        # Show dashboard immediately with loading states
        self.update_status("🚀 Dashboard ready - Loading data...")

        # Initialize background fetcher
        from ..data.cached_data_fetcher import background_fetcher

        self.background_fetcher = background_fetcher

        # DISABLE background fetcher to prevent cascading UI updates
        # self.background_fetcher.add_update_callback(self.on_background_data_update)
        # self.background_fetcher.start_background_fetching()

        # Show simple loading status
        self.update_status("📊 Loading Stockholm dashboard...")

        # Smart refresh strategy: different intervals for different data types
        # News updates: Every 2 minutes (news happens 24/7)
        self.set_interval(120, self.background_processor.update_news_data_only)

        # Price/market data: Every 5 minutes, but only during trading hours
        self.set_interval(
            300, self.background_processor.update_market_data_if_trading_hours
        )

        # Load data once on startup using the same method as manual refresh
        self.call_later(self.update_dashboard_data)

    # Trading hours check and data loading methods moved to utility modules
    def is_trading_hours(self) -> bool:
        """Check if current time is during US stock market trading hours"""
        return self.background_processor.is_trading_hours()

    # News and market data update methods moved to DashboardBackgroundProcessor utility module

    async def start_progressive_loading(self) -> None:
        """Start progressive data loading for better user experience"""
        try:
            # Show dashboard immediately with loading placeholders
            self.update_status("🚀 Dashboard ready - Loading data in background...")
            self.show_loading_placeholders()

            # Phase 1: Load critical data first (prices, basic market data) - NON-BLOCKING
            self.call_later(self.load_critical_data_background)

        except Exception as e:
            self.notify(f"Error during progressive loading: {str(e)}", severity="error")
            self.update_status(f"❌ Loading error: {str(e)}")

    def show_loading_placeholders(self) -> None:
        """Show the dashboard with loading placeholders immediately"""
        try:
            # Initialize empty data cache with loading indicators
            self.data_cache = {
                "loading_phase": "initializing",
                "price_changes": {},
                "current_prices": {},
                "company_names": {},
                "market_data": {},
                "news_data": [],
                "sentiment_analysis": {
                    "market_mood": "Loading...",
                    "average_sentiment": 0.0,
                },
                "ticker_rankings": [],
                "sector_rankings": [],
            }

            # Update basic panels with loading states
            self.update_basic_panels()

        except Exception:
            pass  # Fail silently to avoid blocking UI

    def load_critical_data_background(self) -> None:
        """Load critical data in background without blocking UI"""
        try:
            self.update_status("📊 Loading market prices...")

            # Run in background thread to avoid blocking UI
            import threading

            thread = threading.Thread(
                target=self._fetch_critical_data_thread, daemon=True
            )
            thread.start()

        except Exception as e:
            self.update_status(f"⚠️ Background loading error: {str(e)}")

    def _fetch_critical_data_thread(self) -> None:
        """Background thread for fetching critical data with streaming ticker updates"""
        try:
            from ..data.cached_data_fetcher import cached_get_market_data_optimized
            from ..data.data_fetcher import MAJOR_TICKERS

            # Get basic ticker data quickly
            tickers = MAJOR_TICKERS[:30]

            # Load market data first (fastest)
            market_data = cached_get_market_data_optimized()
            self.data_cache.update({"market_data": market_data})
            self.call_later(self.update_basic_panels)

            # Initialize ticker data containers
            if "price_changes" not in self.data_cache:
                self.data_cache["price_changes"] = {}
            if "current_prices" not in self.data_cache:
                self.data_cache["current_prices"] = {}
            if "company_names" not in self.data_cache:
                self.data_cache["company_names"] = {}

            # Start streaming ticker data processing
            self.call_later(
                lambda: self.update_status("📊 Loading tickers (streaming)...")
            )
            self.call_later(
                lambda: self._show_loading_notification(
                    "Loading ticker data...", 0, len(tickers)
                )
            )
            self._stream_ticker_data(tickers)

            # Mark critical phase complete
            self.data_cache["loading_phase"] = "critical_loaded"
            self.call_later(lambda: self.update_status("📰 Loading news data..."))

            # Start next phase
            self.call_later(self.load_secondary_data_background)

        except Exception as e:
            error_msg = str(e)
            self.call_later(
                lambda: self.update_status(f"⚠️ Critical data error: {error_msg}")
            )
            self.call_later(self._hide_loading_notification)

    def _show_loading_notification(
        self, message: str, current: int = 0, total: int = 0
    ):
        """Show loading notification with progress"""
        try:
            loading_widget = self.query_one(
                "#loading-notification", LoadingNotification
            )
            if total > 0:
                loading_widget.update_progress(current, total, message)
            else:
                loading_widget.show_loading(message)
        except Exception:
            pass  # Widget might not be available yet

    def _update_loading_progress(
        self, current: int, total: int, message: str = "Loading..."
    ):
        """Update loading progress"""
        try:
            loading_widget = self.query_one(
                "#loading-notification", LoadingNotification
            )
            loading_widget.update_progress(current, total, message)
        except Exception:
            pass  # Widget might not be available yet

    def _hide_loading_notification(self):
        """Hide loading notification"""
        try:
            loading_widget = self.query_one(
                "#loading-notification", LoadingNotification
            )
            loading_widget.hide_loading()
        except Exception:
            pass  # Widget might not be available yet

    def _stream_ticker_data(self, tickers):
        """Stream ticker data processing with chunked updates for responsiveness"""
        import threading
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from ..data.cached_data_fetcher import (
            cached_get_ticker_price_change,
            cached_get_ticker_current_price,
            cached_get_ticker_company_name,
        )

        def fetch_single_ticker(ticker):
            """Fetch data for a single ticker"""
            try:
                price_change = cached_get_ticker_price_change(ticker)
                current_price = cached_get_ticker_current_price(ticker)
                company_name = cached_get_ticker_company_name(ticker)

                return {
                    "ticker": ticker,
                    "price_change": price_change,
                    "current_price": current_price,
                    "company_name": company_name,
                    "success": True,
                }
            except Exception as e:
                return {
                    "ticker": ticker,
                    "price_change": 0.0,
                    "current_price": 0.0,
                    "company_name": ticker,
                    "success": False,
                    "error": str(e),
                }

        def chunked_stream_worker():
            """Worker thread for chunked streaming ticker updates"""
            completed_count = 0
            chunk_size = 5  # Process 5 tickers at a time for responsiveness
            ui_update_interval = 0.1  # Update UI every 100ms to keep it responsive

            # Process tickers in chunks to avoid overwhelming the UI
            for i in range(0, len(tickers), chunk_size):
                chunk = tickers[i : i + chunk_size]

                # Process this chunk in parallel
                with ThreadPoolExecutor(max_workers=3) as executor:
                    # Submit chunk tasks
                    future_to_ticker = {
                        executor.submit(fetch_single_ticker, ticker): ticker
                        for ticker in chunk
                    }

                    # Process chunk results
                    chunk_results = []
                    for future in as_completed(future_to_ticker):
                        try:
                            result = future.result()
                            chunk_results.append(result)
                        except Exception:
                            pass

                    # Batch update cache with chunk results
                    for result in chunk_results:
                        completed_count += 1
                        ticker = result["ticker"]

                        # Update cache with individual ticker data
                        self.data_cache["price_changes"][ticker] = result[
                            "price_change"
                        ]
                        self.data_cache["current_prices"][ticker] = result[
                            "current_price"
                        ]
                        self.data_cache["company_names"][ticker] = result[
                            "company_name"
                        ]

                        # Create basic ticker ranking entry
                        ticker_entry = {
                            "ticker": ticker,
                            "company_name": result["company_name"],
                            "current_price": result["current_price"],
                            "price_change": result["price_change"],
                            "sentiment": 0.0,  # Will be updated later
                            "rank": completed_count,
                            "articles": 0,  # Will be updated later
                        }

                        # Add to ticker rankings
                        if "ticker_rankings" not in self.data_cache:
                            self.data_cache["ticker_rankings"] = []

                        # Update or add ticker entry
                        existing_index = None
                        for j, existing in enumerate(
                            self.data_cache["ticker_rankings"]
                        ):
                            if existing["ticker"] == ticker:
                                existing_index = j
                                break

                        if existing_index is not None:
                            self.data_cache["ticker_rankings"][
                                existing_index
                            ] = ticker_entry
                        else:
                            self.data_cache["ticker_rankings"].append(ticker_entry)

                    # Schedule single UI update for the entire chunk
                    self.call_later(self.update_streaming_ticker_display)

                    # Update status with progress
                    progress = f"📊 Loaded {completed_count}/{len(tickers)} tickers..."
                    self.call_later(lambda msg=progress: self.update_status(msg))

                    # Update loading notification with progress
                    total_tickers = len(tickers)
                    self.call_later(
                        lambda count=completed_count, total=total_tickers: self._update_loading_progress(
                            count, total, "Loading ticker data..."
                        )
                    )

                # Small delay between chunks to keep UI responsive
                time.sleep(ui_update_interval)

            # Hide loading notification when complete
            self.call_later(self._hide_loading_notification)

        # Start chunked streaming in background thread
        stream_thread = threading.Thread(target=chunked_stream_worker, daemon=True)
        stream_thread.start()

    def update_streaming_ticker_display(self) -> None:
        """Update ticker display with streaming data - throttled for responsiveness"""
        try:
            import time

            # Throttle updates to avoid overwhelming the UI
            current_time = time.time()
            if not hasattr(self, "_last_ticker_update"):
                self._last_ticker_update = 0

            # Only update every 200ms to keep UI responsive
            if current_time - self._last_ticker_update < 0.2:
                return

            self._last_ticker_update = current_time

            # Update tickers panel with current data
            tickers_panel = self.query_one("#tickers-panel", TickersPanel)
            ticker_rankings = self.data_cache.get("ticker_rankings", [])
            price_changes = self.data_cache.get("price_changes", {})
            current_prices = self.data_cache.get("current_prices", {})
            sector_rankings = self.data_cache.get("sector_rankings", [])

            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )

            # Also update interactive ticker table if on that tab
            try:
                ticker_table = self.query_one(InteractiveTickerTable)
                ticker_table.update_data(ticker_rankings, price_changes, current_prices)
            except Exception:
                pass  # Table might not be visible

        except Exception:
            pass  # Fail silently to avoid disrupting streaming

    def load_secondary_data_background(self) -> None:
        """Load secondary data in background"""
        try:
            # Run in background thread
            import threading

            thread = threading.Thread(
                target=self._fetch_secondary_data_thread, daemon=True
            )
            thread.start()

        except Exception as e:
            self.update_status(f"⚠️ Secondary loading error: {str(e)}")

    def _fetch_secondary_data_thread(self) -> None:
        """Background thread for fetching secondary data with chunked processing"""
        try:
            import time
            from ..core.financial_analyzer import fetch_all_data

            # Phase 1: Fetch basic news and government data (lighter load)
            self.call_later(lambda: self.update_status("📰 Loading news data..."))

            # Fetch data in smaller chunks to avoid blocking
            (
                news_data,
                news_stats,
                government_data,
                policy_stats,
                market_data,
                market_historical_data,
            ) = fetch_all_data()

            # Update cache incrementally
            self.data_cache.update(
                {
                    "news_data": news_data,
                    "government_data": government_data,
                    "market_historical_data": market_historical_data,
                }
            )

            # Schedule UI updates on main thread
            self.call_later(self.update_news_panels)

            # Small delay to keep UI responsive
            time.sleep(0.1)

            # Phase 2: Start earnings data loading in chunks
            self.call_later(lambda: self.update_status("💰 Loading earnings data..."))
            self._load_earnings_data_chunked()

            # Phase 3: Mark secondary loading complete
            self.data_cache["loading_phase"] = "secondary_loaded"
            self.call_later(lambda: self.update_status("🧠 Completing analysis..."))

            # Start final analysis phase
            self.call_later(self.complete_analysis_background)

        except Exception as e:
            error_msg = str(e)
            self.call_later(
                lambda: self.update_status(f"⚠️ News data error: {error_msg}")
            )

    def _load_earnings_data_chunked(self):
        """Load earnings data in chunks to avoid UI blocking"""
        import threading
        import time
        from ..data.data_fetcher import MAJOR_TICKERS
        from ..core.earnings_fetcher import cached_get_ticker_quarterly_earnings

        def chunked_earnings_worker():
            """Worker for chunked earnings data loading"""
            try:
                tickers = MAJOR_TICKERS[:30]

                chunk_size = 3  # Process 3 tickers' earnings at a time
                ui_update_interval = 0.2  # Update every 200ms
                completed_count = 0

                # Initialize earnings cache
                if "earnings_data" not in self.data_cache:
                    self.data_cache["earnings_data"] = {}

                # Process earnings in small chunks
                for i in range(0, len(tickers), chunk_size):
                    chunk = tickers[i : i + chunk_size]

                    # Process chunk
                    for ticker in chunk:
                        try:
                            earnings = cached_get_ticker_quarterly_earnings(ticker)
                            if earnings:
                                self.data_cache["earnings_data"][ticker] = earnings
                            completed_count += 1

                            # Update progress
                            progress = f"💰 Loaded earnings {completed_count}/{len(tickers)}..."
                            self.call_later(
                                lambda msg=progress: self.update_status(msg)
                            )

                        except Exception:
                            # Skip failed earnings data
                            completed_count += 1
                            continue

                    # Small delay between chunks to keep UI responsive
                    time.sleep(ui_update_interval)

                # Mark earnings loading complete
                self.call_later(lambda: self.update_status("✅ Earnings data loaded"))

            except Exception as e:
                error_msg = str(e)
                self.call_later(
                    lambda: self.update_status(f"⚠️ Earnings loading error: {error_msg}")
                )

        # Start earnings loading in background
        earnings_thread = threading.Thread(target=chunked_earnings_worker, daemon=True)
        earnings_thread.start()

    def complete_analysis_background(self) -> None:
        """Complete full analysis in background"""
        try:
            # Run in background thread
            import threading

            thread = threading.Thread(
                target=self._complete_analysis_thread, daemon=True
            )
            thread.start()

        except Exception as e:
            self.update_status(f"⚠️ Analysis error: {str(e)}")

    def _complete_analysis_thread(self) -> None:
        """Background thread for completing analysis with chunked processing"""
        try:
            # Run analysis in chunks to keep UI responsive
            self.call_later(self.update_dashboard_data_chunked)

        except Exception as e:
            error_msg = str(e)
            self.call_later(
                lambda: self.update_status(f"⚠️ Analysis error: {error_msg}")
            )

    async def update_dashboard_data_chunked(self) -> None:
        """Update dashboard data with chunked processing for responsiveness"""
        try:
            import asyncio

            # Skip full reload if we're in progressive loading mode
            if self.data_cache.get("loading_phase") in ["critical", "secondary"]:
                self.update_status("🔄 Completing analysis...")
                self._show_loading_notification("Completing analysis...")
            else:
                self.update_status("🔄 Refreshing data...")
                self._show_loading_notification("Refreshing data...")

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
            self.update_status("🧠 Analyzing sentiment...")
            await asyncio.sleep(0.05)  # Yield control to UI

            # Analyze data in chunks
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
            ) = analyze_all_data(
                news_data, government_data, market_data, market_historical_data
            )

            # Phase 2: Update cache incrementally
            self.update_status("💾 Updating cache...")
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

            # Phase 3: Update UI panels in chunks
            await self._update_ui_panels_chunked(
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
            )

            # Update reactive variables
            self.current_sentiment = sentiment_analysis.get("average_sentiment", 0)
            self.last_update = datetime.now().strftime("%H:%M:%S")
            self.update_status(f"✅ Updated at {self.last_update}")

            # Hide loading notification when complete
            self._hide_loading_notification()

        except Exception as e:
            # Handle errors gracefully
            self.notify(f"Error updating data: {str(e)}", severity="error")
            self.update_status(f"❌ Error: {str(e)}")

            # Hide loading notification on error
            self._hide_loading_notification()

    async def _update_ui_panels_chunked(
        self,
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
    ):
        """Update UI panels in chunks to maintain responsiveness"""
        import asyncio

        # Chunk 1: Overview tab panels (most critical)
        self.update_status("🎨 Updating overview...")
        try:
            summary_panel = self.query_one("#summary-panel", SummaryPanel)
            summary_panel.update_data(
                sentiment_analysis, policy_analysis, market_health, market_data
            )
        except Exception:
            pass
        await asyncio.sleep(0.05)  # Yield control to UI

        try:
            tickers_panel = self.query_one("#tickers-panel", TickersPanel)
            tickers_panel.update_data(
                sector_rankings, ticker_rankings, price_changes, current_prices
            )
        except Exception:
            pass
        await asyncio.sleep(0.05)

        # Chunk 2: Sector and multi-ticker panels
        self.update_status("📊 Updating sectors...")
        try:
            sectors_panel = self.query_one("#sectors-panel", SectorsPanel)
            sectors_panel.update_data(sector_rankings, price_changes)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        try:
            multi_ticker_panel = self.query_one("#multi-ticker-panel", MultiTickerPanel)
            multi_ticker_panel.update_data(multi_ticker_articles, cross_ticker_analysis)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        # Chunk 3: Interactive tickers tab
        self.update_status("🏆 Updating tickers...")
        try:
            ticker_table = self.query_one(InteractiveTickerTable)
            ticker_table.update_data(ticker_rankings, price_changes, current_prices)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        # Chunk 4: News tab
        self.update_status("📰 Updating news...")
        try:
            news_tree = self.query_one("#news-tree", NewsTreeView)
            news_tree.update_news(news_data, sentiment_scores, sentiment_details)

            chart = self.query_one(RealTimeChart)
            if sentiment_analysis:
                chart.update_sentiment(sentiment_analysis.get("average_sentiment", 0))
        except Exception:
            pass
        await asyncio.sleep(0.05)

        # Chunk 5: Policy tab
        self.update_status("🏛️ Updating policy...")
        try:
            policy_tree = self.query_one("#policy-tree", PolicyTreeView)
            policy_tree.update_data(policy_analysis)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        try:
            policy_summary_panel = self.query_one(
                "#policy-summary-panel", PolicySummaryPanel
            )
            policy_summary_panel.update_data(policy_analysis)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        try:
            policy_timeline_panel = self.query_one(
                "#policy-timeline-panel", PolicyTimelinePanel
            )
            policy_timeline_panel.update_data(policy_analysis)
        except Exception:
            pass
        await asyncio.sleep(0.05)

        # Chunk 6: Market indices tab
        self.update_status("📈 Updating indices...")
        try:
            indices_panel = self.query_one("#market-indices-panel", MarketIndicesPanel)
            indices_panel.update_data(market_data, market_historical_data)
        except Exception:
            pass
        await asyncio.sleep(0.05)

    async def update_dashboard_data(self) -> None:
        """Update all dashboard data - now optimized for hot loading"""
        try:
            # Skip full reload if we're in progressive loading mode
            if self.data_cache.get("loading_phase") in ["critical", "secondary"]:
                self.update_status("🔄 Completing analysis...")
            else:
                self.update_status("🔄 Refreshing data...")

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
            ) = analyze_all_data(
                news_data, government_data, market_data, market_historical_data
            )

            # Store data for other tabs
            self.data_cache = {
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

            # Update Overview tab panels
            try:
                summary_panel = self.query_one("#summary-panel", SummaryPanel)
                summary_panel.update_data(
                    sentiment_analysis, policy_analysis, market_health, market_data
                )
            except Exception:
                pass

            try:
                tickers_panel = self.query_one("#tickers-panel", TickersPanel)
                tickers_panel.update_data(
                    sector_rankings, ticker_rankings, price_changes, current_prices
                )
            except Exception:
                pass

            try:
                sectors_panel = self.query_one("#sectors-panel", SectorsPanel)
                sectors_panel.update_data(sector_rankings, price_changes)
            except Exception:
                pass

            try:
                multi_ticker_panel = self.query_one(
                    "#multi-ticker-panel", MultiTickerPanel
                )
                multi_ticker_panel.update_data(
                    multi_ticker_articles, cross_ticker_analysis
                )
            except Exception:
                pass

            # Update Interactive Tickers tab
            try:
                ticker_table = self.query_one(InteractiveTickerTable)
                ticker_table.update_data(ticker_rankings, price_changes, current_prices)
            except Exception:
                pass

            # Update News Tree tab
            try:
                news_tree = self.query_one("#news-tree", NewsTreeView)
                news_tree.update_news(news_data, sentiment_scores, sentiment_details)

                chart = self.query_one(RealTimeChart)
                if sentiment_analysis:
                    chart.update_sentiment(
                        sentiment_analysis.get("average_sentiment", 0)
                    )
            except Exception:
                pass

            # Update Policy tab
            try:
                policy_tree = self.query_one("#policy-tree", PolicyTreeView)
                policy_tree.update_data(policy_analysis)
            except Exception:
                pass

            try:
                policy_summary_panel = self.query_one(
                    "#policy-summary-panel", PolicySummaryPanel
                )
                policy_summary_panel.update_data(policy_analysis)
            except Exception:
                pass

            try:
                policy_timeline_panel = self.query_one(
                    "#policy-timeline-panel", PolicyTimelinePanel
                )
                policy_timeline_panel.update_data(policy_analysis)
            except Exception:
                pass

            # Update Market Indices tab panel
            try:
                indices_panel = self.query_one(
                    "#market-indices-panel", MarketIndicesPanel
                )
                indices_panel.update_data(market_data, market_historical_data)
            except Exception:
                pass

            # Update reactive variables
            self.current_sentiment = sentiment_analysis.get("average_sentiment", 0)
            self.last_update = datetime.now().strftime("%H:%M:%S")

            self.update_status(f"✅ Updated at {self.last_update}")

        except Exception as e:
            # Handle errors gracefully
            self.notify(f"Error updating data: {str(e)}", severity="error")
            self.update_status(f"❌ Error: {str(e)}")

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

            # Update tickers panel with available data
            try:
                tickers_panel = self.query_one("#tickers-panel", TickersPanel)
                sector_rankings = self.data_cache.get("sector_rankings", [])
                tickers_panel.update_data(
                    sector_rankings, ticker_rankings, price_changes, current_prices
                )
            except Exception:
                pass

            # Update summary panel with basic market data
            try:
                summary_panel = self.query_one("#summary-panel", SummaryPanel)
                basic_sentiment = {
                    "market_mood": "Loading...",
                    "average_sentiment": 0.0,
                }
                summary_panel.update_data(basic_sentiment, {}, {}, market_data)
            except Exception:
                pass

        except Exception as e:
            self.notify(f"Error updating basic panels: {str(e)}", severity="warning")

    def update_news_panels(self) -> None:
        """Update news-related panels during progressive loading"""
        try:
            news_data = self.data_cache.get("news_data", [])

            # Update news tree with available data
            try:
                news_tree = self.query_one("#news-tree", NewsTreeView)
                # Get sentiment data from cache if available
                sentiment_scores = self.data_cache.get("sentiment_scores", {})
                sentiment_details = self.data_cache.get("sentiment_details", [])
                news_tree.update_news(news_data, sentiment_scores, sentiment_details)
            except Exception:
                pass

            # Update policy tree if government data is available
            government_data = self.data_cache.get("government_data", [])
            if government_data:
                try:
                    policy_tree = self.query_one("#policy-tree", PolicyTreeView)
                    # Create basic policy analysis structure
                    basic_policy_analysis = {
                        "articles": government_data,
                        "categories": {},
                        "sentiment_summary": {"average_sentiment": 0.0},
                    }
                    policy_tree.update_data(basic_policy_analysis)
                except Exception:
                    pass

        except Exception as e:
            self.notify(f"Error updating news panels: {str(e)}", severity="warning")

    def on_background_data_update(self, data_type: str, identifier: str) -> None:
        """Handle background data updates for hot loading with throttling"""
        try:
            import time

            # Throttle background updates to avoid overwhelming the UI
            current_time = time.time()
            if not hasattr(self, "_last_bg_update"):
                self._last_bg_update = {}

            # Only update each data type every 500ms
            if data_type in self._last_bg_update:
                if current_time - self._last_bg_update[data_type] < 0.5:
                    return

            self._last_bg_update[data_type] = current_time

            # DISABLE throttled refresh calls to prevent display corruption
            # if data_type == "prices":
            #     self.call_later(self.refresh_price_panels_throttled)
            # elif data_type == "news":
            #     self.call_later(self.refresh_news_panels_throttled)
            # elif data_type == "market":
            #     self.call_later(self.refresh_market_panels_throttled)

        except Exception:
            # Handle errors silently to avoid disrupting background updates
            pass

    def refresh_price_panels_throttled(self) -> None:
        """Refresh panels that depend on price data with throttling"""
        try:
            import time

            # Throttle price panel updates
            current_time = time.time()
            if not hasattr(self, "_last_price_refresh"):
                self._last_price_refresh = 0

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
                tickers_panel = self.query_one("#tickers-panel", TickersPanel)
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
            import time

            # Throttle news panel updates
            current_time = time.time()
            if not hasattr(self, "_last_news_refresh"):
                self._last_news_refresh = 0

            if current_time - self._last_news_refresh < 2.0:  # Max once per 2 seconds
                return

            self._last_news_refresh = current_time

            # Update news tree if it exists
            try:
                news_tree = self.query_one("#news-tree", NewsTreeView)
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
            import time

            # Throttle market panel updates
            current_time = time.time()
            if not hasattr(self, "_last_market_refresh"):
                self._last_market_refresh = 0

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
                summary_panel = self.query_one("#summary-panel", SummaryPanel)
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
            current_status = getattr(self, "_current_status", "")
            if not any(
                keyword in current_status.lower()
                for keyword in ["loading", "error", "analyzing"]
            ):
                self.update_status(cache_status)

        except Exception:
            pass  # Fail silently

    def on_unmount(self) -> None:
        """Cleanup when dashboard is closed"""
        try:
            if self.background_fetcher:
                self.background_fetcher.stop_background_fetching()
                self.update_status("🛑 Proactive cache system stopped")
        except Exception:
            pass

    def update_status(self, message: str) -> None:
        """Update status bar"""
        try:
            # Track current status for cache statistics display
            self._current_status = message

            status_bar = self.query_one("#status-bar", Static)
            refresh_status = "ON" if self.auto_refresh_enabled else "OFF"
            status_bar.update(f"🔄 Auto-refresh: {refresh_status} | {message}")
        except Exception:
            pass

    def action_refresh(self) -> None:
        """Manual refresh action"""
        self.call_later(self.update_dashboard_data)

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to specific tab (overview, tickers, news, policy)"""
        try:
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = tab_id
        except Exception:
            pass

    def action_export_data(self) -> None:
        """Export current data"""
        self.notify(
            "Export functionality would be implemented here", severity="information"
        )

    def action_open_article_url(self) -> None:
        """Open the currently selected article URL in browser"""
        if self.current_article_url:
            import webbrowser

            try:
                webbrowser.open(self.current_article_url)
                self.notify("Opening article in browser...", severity="information")
            except Exception as e:
                self.notify(f"Error opening URL: {str(e)}", severity="error")
        else:
            self.notify(
                "No article selected. Click on an article in the News tab first.",
                severity="warning",
            )

    def action_reset_column_widths(self) -> None:
        """Reset all column widths to their default values in any adjustable table"""
        try:
            # Get the current active tab
            tabbed_content = self.query_one(TabbedContent)
            current_tab = tabbed_content.active

            # Find the currently focused adjustable table
            adjustable_table = self._get_focused_adjustable_table(current_tab)

            if adjustable_table:
                adjustable_table.reset_column_widths()
                self.notify("Column widths reset to defaults", timeout=2)
            else:
                self.notify(
                    "No adjustable table found in current tab", severity="warning"
                )

        except Exception as e:
            self.notify(f"Column reset failed: {str(e)}", severity="error")


def run_textual_dashboard():
    """Run the Stockholm dashboard"""
    app = StockholmDashboard()
    app.run()


def run_enhanced_textual_dashboard(debug=False):
    """Run the Stockholm dashboard with configuration options"""
    app = StockholmDashboard()

    # Store configuration in the app for use by data fetching
    app.debug_mode = debug

    if debug:
        # Show a brief startup message before launching the dashboard
        print("🚀 Launching Stockholm Dashboard...")
        print("🔧 Debug mode: ON")
        print("📊 Loading interface...\n")

    app.run()


if __name__ == "__main__":
    run_textual_dashboard()
