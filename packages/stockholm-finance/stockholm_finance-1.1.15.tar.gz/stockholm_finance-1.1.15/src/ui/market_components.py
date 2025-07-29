#!/usr/bin/env python3
"""
Market Components for Stockholm Dashboard

This module contains all market-specific UI components that handle market indices,
market data display, and market-related visualizations. These components are
specialized for displaying financial market information and indices.

Extracted from panel_components.py during modular refactoring.
"""

from typing import Dict

from rich.table import Table
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Collapsible, Static
from textual_plotext import PlotextPlot


class MarketIndexCard(Static):
    """Individual market index card with collapsible chart"""

    def __init__(self, index_ticker: str, index_name: str, **kwargs):
        super().__init__(**kwargs)
        self.index_ticker = index_ticker
        self.index_name = index_name
        self.border_title = f"📈 {index_name} ({index_ticker})"

    def compose(self) -> ComposeResult:
        with Collapsible(
            title=f"📊 {self.index_name} ({self.index_ticker})", collapsed=True
        ):
            # Basic info section
            yield Static("Loading index data...", id=f"info-{self.index_ticker}")
            # Chart section
            yield PlotextPlot(id=f"chart-{self.index_ticker}", classes="index-chart")

    def update_data(self, market_data: Dict, historical_data: Dict = None):
        """Update the index card with current and historical data"""
        try:
            # Get current data for this index
            index_data = market_data.get(self.index_ticker, {})

            if not index_data:
                info_widget = self.query_one(f"#info-{self.index_ticker}", Static)
                info_widget.update("No data available")
                return

            # Create info table
            table = Table()
            table.add_column("Metric", style="bold cyan", width=15)
            table.add_column("Value", width=20)

            # Current price and change
            current_price = index_data.get("current_price", 0)
            price_change = index_data.get("price_change", 0)
            change_emoji = (
                "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
            )

            table.add_row("💰 Current", f"${current_price:.2f}")
            table.add_row("📊 Change", f"{change_emoji} {price_change:+.2f}%")

            # Additional metrics if available
            if "volume" in index_data:
                volume = index_data["volume"]
                table.add_row("📊 Volume", f"{volume:,.0f}")

            if "market_cap" in index_data:
                market_cap = index_data["market_cap"]
                table.add_row("💎 Market Cap", f"${market_cap/1e12:.1f}T")

            # Update info widget
            info_widget = self.query_one(f"#info-{self.index_ticker}", Static)
            info_widget.update(table)

            # Update chart if historical data is available
            if historical_data and self.index_ticker in historical_data:
                self._update_chart(historical_data[self.index_ticker])
            else:
                # Show message if no historical data
                try:
                    chart_widget = self.query_one(
                        f"#chart-{self.index_ticker}", PlotextPlot
                    )
                    chart_widget.plt.clear_data()
                    chart_widget.plt.clear_figure()
                    if not historical_data:
                        chart_widget.plt.text(
                            0.5, 0.5, "No historical data available", alignment="center"
                        )
                    else:
                        chart_widget.plt.text(
                            0.5,
                            0.5,
                            f"No data for {self.index_ticker}",
                            alignment="center",
                        )
                    chart_widget.plt.title(f"{self.index_name} - No Data")
                    chart_widget.plt.plotsize(40, 8)
                except Exception:
                    pass

        except Exception as e:
            # Fallback display
            info_widget = self.query_one(f"#info-{self.index_ticker}", Static)
            info_widget.update(f"Error loading data: {str(e)[:50]}...")

    def _update_chart(self, hist_data):
        """Update the chart with historical data"""
        try:
            chart_widget = self.query_one(f"#chart-{self.index_ticker}", PlotextPlot)

            if not hist_data:
                return

            # Extract prices and dates - handle multiple formats
            prices = None

            if isinstance(hist_data, tuple) and len(hist_data) == 2:
                # Handle tuple format (prices, dates) from cached_get_market_indices_historical_data
                prices, dates = hist_data
                if not prices or len(prices) < 2:
                    return
            elif isinstance(hist_data, dict) and "prices" in hist_data:
                # Handle dict format with "prices" key
                prices = hist_data["prices"]
            elif isinstance(hist_data, list):
                # Extract prices from list of dictionaries
                prices = [float(d.get("close", 0)) for d in hist_data]
            else:
                return

            if not prices or len(prices) < 2:
                return

            # Clear and plot
            chart_widget.plt.clear_data()
            chart_widget.plt.clear_figure()

            # Use indices for x-axis
            x_values = list(range(len(prices)))
            chart_widget.plt.plot(x_values, prices, marker="braille", color="cyan")
            chart_widget.plt.title(f"{self.index_name} - 6 Month Trend")
            chart_widget.plt.xlabel("Days")
            chart_widget.plt.ylabel("Price")
            chart_widget.plt.plotsize(40, 8)

        except Exception as e:
            # Chart update failed - show error for debugging
            try:
                chart_widget = self.query_one(
                    f"#chart-{self.index_ticker}", PlotextPlot
                )
                chart_widget.plt.clear_data()
                chart_widget.plt.clear_figure()
                chart_widget.plt.text(
                    0.5, 0.5, f"Chart error: {str(e)[:30]}...", alignment="center"
                )
                chart_widget.plt.title(f"{self.index_name} - Error")
                chart_widget.plt.plotsize(40, 8)
            except Exception:
                pass


class MarketIndicesPanel(ScrollableContainer):
    """Panel containing all market index cards"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "📈 Market Indices Overview"
        self.index_cards = {}

    def compose(self) -> ComposeResult:
        # Import here to avoid circular imports
        from ..config.config import MARKET_INDICES

        # Create cards for each market index
        for ticker, name in MARKET_INDICES.items():
            card = MarketIndexCard(ticker, name, id=f"card-{ticker}")
            self.index_cards[ticker] = card
            yield card

    def update_data(self, market_data: Dict, historical_data: Dict = None):
        """Update all index cards with current and historical data"""
        for _ticker, card in self.index_cards.items():
            card.update_data(market_data, historical_data)
