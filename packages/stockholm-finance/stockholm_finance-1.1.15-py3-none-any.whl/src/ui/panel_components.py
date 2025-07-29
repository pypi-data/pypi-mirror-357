#!/usr/bin/env python3
"""
Panel Components for Stockholm Dashboard

This module contains all panel classes that display specific types of information
in organized sections of the dashboard. Panels are self-contained UI components
that handle data display and updates for different aspects of market analysis.

Extracted from textual_dashboard.py during modular refactoring.
"""

from datetime import datetime
from typing import Dict, List

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Static

# Import base components

# Import data table components
from .data_tables import TickerNewsTable


class ComprehensiveEarningsPanel(Static):
    """Comprehensive earnings panel showing quarterly data, trends, and analysis"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "💰 Earnings Analysis"
        self.current_ticker = None

    def update_ticker_earnings(self, ticker_symbol: str):
        """Update panel with comprehensive earnings data for the specified ticker"""
        self.current_ticker = ticker_symbol

        try:
            # Import here to avoid circular imports
            from ..core.earnings_fetcher import get_earnings_summary_for_ticker

            # Get comprehensive earnings data
            earnings_summary = get_earnings_summary_for_ticker(ticker_symbol)

            if earnings_summary.get("status") != "success":
                self.update("📊 No earnings data available for this ticker")
                return

            # Extract data
            latest_quarter = earnings_summary.get("latest_quarter")
            analysis = earnings_summary.get("analysis", {})
            trends = analysis.get("trends", {})

            if not latest_quarter:
                self.update("📊 No quarterly data available")
                return

            # Create comprehensive earnings table
            table = Table()
            table.add_column("Metric", style="bold cyan", width=15)
            table.add_column("Value", width=25)

            # Quarter header
            quarter_name = latest_quarter.get("quarter", "Latest Quarter")
            table.add_row("📅 Quarter:", f"[bold yellow]{quarter_name}[/bold yellow]")

            # Revenue data
            revenue = latest_quarter.get("metrics", {}).get("revenue")
            if revenue is not None:
                revenue_display = self._format_currency(revenue)
                table.add_row(
                    "💰 Revenue:", f"[bold green]{revenue_display}[/bold green]"
                )
            else:
                table.add_row("💰 Revenue:", "N/A")

            # Net Income data
            net_income = latest_quarter.get("metrics", {}).get("net_income")
            if net_income is not None:
                net_income_display = self._format_currency(net_income)
                income_style = "green" if net_income > 0 else "red"
                table.add_row(
                    "💵 Net Income:", Text(net_income_display, style=income_style)
                )
            else:
                table.add_row("💵 Net Income:", "N/A")

            # Calculate and display margin
            if revenue is not None and net_income is not None and revenue != 0:
                margin = (net_income / revenue) * 100
                margin_style = (
                    "green" if margin > 10 else "yellow" if margin > 0 else "red"
                )
                table.add_row("📊 Margin:", Text(f"{margin:.1f}%", style=margin_style))
            else:
                table.add_row("📊 Margin:", "N/A")

            # Revenue trend
            revenue_trend = trends.get("revenue", {})
            if revenue_trend:
                trend_info = self._format_trend_info(revenue_trend)
                table.add_row("📈 Rev Trend:", trend_info)
            else:
                table.add_row("📈 Rev Trend:", "N/A")

            # Income trend
            income_trend = trends.get("net_income", {})
            if income_trend:
                trend_info = self._format_trend_info(income_trend)
                table.add_row("📊 Inc Trend:", trend_info)
            else:
                table.add_row("📊 Inc Trend:", "N/A")

            # Overall assessment
            overall_assessment = self._calculate_overall_assessment(
                revenue_trend, income_trend, revenue, net_income
            )
            table.add_row("🏆 Overall:", overall_assessment)

            self.update(table)

        except Exception as e:
            self.update(f"❌ Error loading earnings data: {str(e)}")

    def _format_currency(self, amount: float) -> str:
        """Format currency amounts in billions/millions"""
        if abs(amount) >= 1e9:
            return f"${amount/1e9:.1f}B"
        elif abs(amount) >= 1e6:
            return f"${amount/1e6:.0f}M"
        elif abs(amount) >= 1e3:
            return f"${amount/1e3:.0f}K"
        else:
            return f"${amount:.0f}"

    def _format_trend_info(self, trend_data: dict) -> Text:
        """Format trend information with appropriate styling"""
        trend = trend_data.get("trend", "stable")
        avg_growth = trend_data.get("avg_growth", 0)

        if trend == "improving":
            emoji = "📈"
            style = "green"
            status = "Stable" if abs(avg_growth) < 5 else "Growing"
        elif trend == "declining":
            emoji = "📉"
            style = "red"
            status = "Declining"
        else:
            emoji = "➡️"
            style = "yellow"
            status = "Stable"

        return Text(f"{emoji} {status} ({avg_growth:+.1f}%)", style=style)

    def _calculate_overall_assessment(
        self, revenue_trend: dict, income_trend: dict, revenue: float, net_income: float
    ) -> Text:
        """Calculate overall financial health assessment"""
        score = 0

        # Revenue trend scoring
        if revenue_trend:
            rev_trend = revenue_trend.get("trend", "stable")
            if rev_trend == "improving":
                score += 2
            elif rev_trend == "stable":
                score += 1

        # Income trend scoring
        if income_trend:
            inc_trend = income_trend.get("trend", "stable")
            if inc_trend == "improving":
                score += 2
            elif inc_trend == "stable":
                score += 1

        # Profitability scoring
        if revenue and net_income:
            if net_income > 0:
                margin = (net_income / revenue) * 100
                if margin > 15:
                    score += 2
                elif margin > 5:
                    score += 1

        # Overall assessment
        if score >= 5:
            return Text("🟢 Strong", style="green")
        elif score >= 3:
            return Text("🟡 Moderate", style="yellow")
        else:
            return Text("🔴 Weak", style="red")


class TickerNewsPanel(Vertical):
    """Panel displaying news articles and timeline chart for the selected ticker"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_ticker = None

    def compose(self) -> ComposeResult:
        # News articles table (full height)
        with ScrollableContainer(id="news-table-container", classes="news-table-panel"):
            yield Static(
                "📊 Select a ticker to view related news articles",
                id="ticker-news-placeholder",
            )
            yield TickerNewsTable(id="ticker-news-table", classes="hidden")

    def update_ticker_news(
        self, ticker_symbol: str, news_data: List[Dict], sentiment_details: List[Dict]
    ):
        """Update the news panel with articles related to the selected ticker"""
        self.current_ticker = ticker_symbol

        # Filter news articles that mention this ticker using the sophisticated detection
        # that was already computed during sentiment analysis
        ticker_articles = []
        for i, article in enumerate(news_data):
            # Check if ticker is mentioned using the pre-computed mentioned_tickers list
            if i < len(sentiment_details):
                mentioned_tickers = sentiment_details[i].get("mentioned_tickers", [])
                if ticker_symbol in mentioned_tickers:
                    article_data = {
                        "article": article,
                        "sentiment_detail": sentiment_details[i],
                        "index": i,
                    }
                    ticker_articles.append(article_data)

        # Get the table and placeholder widgets
        news_table = self.query_one("#ticker-news-table", TickerNewsTable)
        placeholder = self.query_one("#ticker-news-placeholder", Static)

        if not ticker_articles:
            # Show placeholder, hide table
            placeholder.update(f"📰 No recent news articles found for {ticker_symbol}")
            placeholder.remove_class("hidden")
            news_table.add_class("hidden")
            return

        # Hide placeholder, show table
        placeholder.add_class("hidden")
        news_table.remove_class("hidden")

        # Clear and populate the table
        news_table.clear()
        news_table.articles_data = ticker_articles  # Store for row selection

        # Add columns if not already present
        if not news_table.columns:
            news_table.add_columns(
                "#", "Headline", "Time", "Sentiment", "Score", "Tickers", "Source"
            )

        # Populate the table with ticker-specific articles
        for i, article_data in enumerate(ticker_articles):
            article = article_data["article"]
            sentiment_detail = article_data["sentiment_detail"]

            # Get article details
            headline = article.get("headline", "No headline")
            pub_timestamp = article.get("pub_timestamp", 0)

            # Calculate time ago
            if pub_timestamp:
                try:
                    pub_date = datetime.fromtimestamp(pub_timestamp)
                    time_diff = datetime.now() - pub_date
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} days ago"
                    else:
                        hours = time_diff.seconds // 3600
                        if hours > 0:
                            time_ago = f"{hours} hours ago"
                        else:
                            minutes = time_diff.seconds // 60
                            time_ago = f"{minutes} minutes ago"
                except Exception:
                    time_ago = "Unknown"
            else:
                time_ago = "Unknown"

            # Get sentiment information (using correct field names from sentiment analyzer)
            sentiment_score = sentiment_detail.get("polarity", 0.0)
            sentiment_category = sentiment_detail.get("category", "Neutral")

            # Sentiment display
            if sentiment_category == "Positive":
                sentiment_emoji = "🟢"
                sentiment_text = "Positive"
                sentiment_style = "green"
            elif sentiment_category == "Negative":
                sentiment_emoji = "🔴"
                sentiment_text = "Negative"
                sentiment_style = "red"
            else:
                sentiment_emoji = "🟡"
                sentiment_text = "Neutral"
                sentiment_style = "yellow"

            # Get all tickers mentioned in this article
            mentioned_tickers = sentiment_detail.get("mentioned_tickers", [])

            # Create ticker display string (exclude the current ticker we're viewing)
            other_tickers = [t for t in mentioned_tickers if t != ticker_symbol]
            if other_tickers:
                # Show up to 3 other tickers
                tickers_display = " ".join([f"🟡{t}" for t in other_tickers[:3]])
                if len(other_tickers) > 3:
                    tickers_display += f" +{len(other_tickers)-3}"
            else:
                tickers_display = "—"

            # Get source information
            source = article.get("source", "Unknown")

            # Add row to table - NO TEXT TRUNCATION
            news_table.add_row(
                str(i),
                headline,  # Full headline without truncation
                time_ago,  # Keep relative time for easy readability
                Text(f"{sentiment_emoji} {sentiment_text}", style=sentiment_style),
                Text(f"{sentiment_score:+.3f}", style=sentiment_style),
                tickers_display,  # New tickers column
                source,  # Full source without truncation
            )

        # Force a UI update to ensure sentiment styling is properly rendered
        try:
            # Schedule a refresh to ensure the table renders properly
            self.call_later(lambda: None)  # This forces a UI update cycle
        except Exception:
            pass  # Fail silently if refresh fails


class SummaryPanel(Static):
    """Enhanced panel showing market summary (policy moved to dedicated tab)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "📊 Market Overview"

    def update_data(
        self, sentiment_analysis, policy_analysis, market_health, market_data=None
    ):
        """Update the summary panel with market data (policy analysis in separate tab)"""
        # Market sentiment
        market_mood = sentiment_analysis.get("market_mood", "N/A")
        market_score = sentiment_analysis.get("average_sentiment", 0)
        market_emoji = self._get_mood_emoji(market_score, market_mood)

        # Note: recommendation and market_trend variables removed as they were unused

        # Article count
        total_articles = sentiment_analysis.get("total_articles", 0)

        # Sentiment distribution - get percentages directly from sentiment_analysis
        positive_pct = sentiment_analysis.get("positive_percentage", 0)
        negative_pct = sentiment_analysis.get("negative_percentage", 0)

        # Create summary table
        table = Table()
        table.add_column("Category", style="bold cyan", width=20)
        table.add_column("Value", width=40)

        # MARKET SENTIMENT SECTION
        table.add_row("📊 MARKET SENTIMENT", "")
        table.add_row("", f"{market_emoji} {market_mood} ({market_score:+.3f})")
        table.add_row(
            "", f"📈 {positive_pct:.0f}% Positive | 📉 {negative_pct:.0f}% Negative"
        )
        table.add_row("", f"📊 {total_articles} Articles Analyzed")
        table.add_row("", "")

        # MARKET INDICES SECTION
        if market_data:
            # Create a single formatted string with all indices
            indices_lines = []
            for ticker, data in list(market_data.items())[:5]:  # Show all 5 indices
                change = data.get("price_change", 0)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                # Use shorter names for better fit
                name_map = {
                    "S&P 500": "S&P 500",
                    "NASDAQ": "NASDAQ",
                    "Dow Jones": "Dow",
                    "Russell 2000": "Russell",
                    "Total Stock Market": "Total Market",
                }
                name = data.get("name", ticker)
                short_name = name_map.get(name, name)
                indices_lines.append(f"{emoji} {short_name}: {change:+.1f}%")

            # Add all indices as a single formatted entry
            indices_text = " | ".join(indices_lines)
            table.add_row("📈 MARKET INDICES", indices_text)
            table.add_row("", "")

        self.update(table)

    def _get_mood_emoji(self, score: float, mood: str) -> str:
        """Get appropriate emoji for market mood"""
        if score > 0.1:
            return "😊"
        elif score < -0.1:
            return "😟"
        else:
            return "😐"


class TickersPanel(Static):
    """Enhanced panel showing top performing tickers with detailed metrics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "🏆 Top Sentiment Performers"

    def update_data(
        self, _sector_rankings, ticker_rankings, price_changes, current_prices
    ):
        """Update the tickers panel with new data"""
        if not ticker_rankings:
            self.update("Loading ticker sentiment data...")
            return

        table = Table()
        table.add_column("Rank", style="bold cyan", width=4)
        table.add_column("Ticker", style="bold", width=8)
        table.add_column("Price & Change", width=18)
        table.add_column("Sentiment", width=10)

        # Add header row
        table.title = "Top 6 Tickers by Sentiment Score"

        # Add top tickers
        for i, ticker_data in enumerate(ticker_rankings[:6], 1):
            ticker_symbol = ticker_data["ticker"]
            sentiment_score = ticker_data.get(
                "overall_score", ticker_data.get("sentiment_score", 0.0)
            )

            # Price information
            current_price = current_prices.get(ticker_symbol, 0.0)
            price_change = price_changes.get(ticker_symbol, 0.0)

            # Price display with emoji
            price_emoji = (
                "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
            )
            price_display = f"{price_emoji} ${current_price:.2f} ({price_change:+.1f}%)"

            # Sentiment styling
            if sentiment_score > 0.1:
                sentiment_style = "green"
            elif sentiment_score < -0.1:
                sentiment_style = "red"
            else:
                sentiment_style = "yellow"

            table.add_row(
                f"{i}",
                ticker_symbol,
                price_display,
                Text(f"{sentiment_score:.3f}", style=sentiment_style),
            )

        self.update(table)


class SectorsPanel(Static):
    """Enhanced panel showing top performing sectors with detailed metrics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "🏭 Sector Performance Rankings"

    def update_data(self, sector_rankings, price_changes):
        """Update the sectors panel with new data"""
        if not sector_rankings:
            self.update("No sector data available")
            return

        table = Table()
        table.add_column("Rank", style="bold cyan", width=4)
        table.add_column("Sector", width=14)
        table.add_column("Strength", width=8)
        table.add_column("Top Ticker", width=12)

        table.title = "Top 5 Sectors by Sentiment Strength"

        # Add top sectors
        for i, sector in enumerate(sector_rankings[:5], 1):
            # Sector sentiment emoji (standardized thresholds)
            avg_sentiment = sector["average_sentiment"]
            if avg_sentiment > 0.1:
                emoji = "🟢"
                sentiment_style = "green"
            elif avg_sentiment < -0.1:
                emoji = "🔴"
                sentiment_style = "red"
            else:
                emoji = "🟡"
                sentiment_style = "yellow"

            # Top ticker info
            top_ticker = sector["top_ticker"]
            price_change = price_changes.get(top_ticker, 0.0)
            price_emoji = (
                "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
            )

            table.add_row(
                f"{i}",
                f"{emoji} {sector['sector'][:12]}",
                Text(f"{sector['sector_strength']:.2f}", style=sentiment_style),
                f"{price_emoji} {top_ticker}",
            )

        self.update(table)


class MultiTickerPanel(Static):
    """Enhanced panel showing multi-ticker analysis with clear metrics"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "🔄 Cross-Ticker Analysis"

    def update_data(self, multi_ticker_articles, cross_ticker_analysis):
        """Update the multi-ticker panel with new data"""
        if not multi_ticker_articles:
            self.update("No multi-ticker articles found")
            return

        table = Table()
        table.add_column("Category", style="bold cyan", width=20)
        table.add_column("Value", width=30)

        # Analysis summary
        table.add_row("📊 ANALYSIS SUMMARY", "")
        table.add_row("", f"Multi-ticker Articles: {len(multi_ticker_articles)}")

        if cross_ticker_analysis:
            conflicts = cross_ticker_analysis.get("sentiment_conflicts", [])
            pairs = cross_ticker_analysis.get("ticker_pairs", [])
            table.add_row("", f"Sentiment Conflicts: {len(conflicts)}")
            table.add_row("", f"Ticker Pairs Found: {len(pairs)}")

        # Show top conflicts
        if cross_ticker_analysis.get("sentiment_conflicts"):
            table.add_row("⚠️ TOP CONFLICTS", "")
            for i, conflict in enumerate(
                cross_ticker_analysis["sentiment_conflicts"][:3], 1
            ):
                pos_tickers = ", ".join(conflict["positive_tickers"][:2])
                neg_tickers = ", ".join(conflict["negative_tickers"][:2])
                table.add_row("", f"{i}. 🟢 {pos_tickers} vs 🔴 {neg_tickers}")

        self.update(table)


class PolicySummaryPanel(Static):
    """Comprehensive policy analysis summary panel"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "🏛️ Government Policy Analysis"

    def update_data(self, policy_analysis):
        """Update the policy summary panel with comprehensive data"""
        if not policy_analysis:
            self.update("No policy data available")
            return

        table = Table()
        table.add_column("Category", style="bold cyan", width=20)
        table.add_column("Details", width=50)

        # Policy sentiment overview
        policy_sentiment = policy_analysis.get("policy_sentiment", {})
        avg_sentiment = policy_sentiment.get("average_sentiment", 0)
        sentiment_emoji = (
            "🟢" if avg_sentiment > 0.1 else "🔴" if avg_sentiment < -0.1 else "🟡"
        )

        table.add_row("📊 POLICY SENTIMENT", "")
        table.add_row("", f"{sentiment_emoji} Average: {avg_sentiment:+.3f}")

        # Policy categories
        categories = policy_analysis.get("policy_categories", {})
        if categories:
            table.add_row("", "")
            table.add_row("🏛️ POLICY AREAS", "")
            for category, data in list(categories.items())[:5]:
                count = data.get("count", 0)
                sentiment = data.get("average_sentiment", 0)
                emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                table.add_row(
                    "", f"{emoji} {category}: {count} articles ({sentiment:+.2f})"
                )

        # Recent policy developments
        recent_policies = policy_analysis.get("recent_developments", [])
        if recent_policies:
            table.add_row("", "")
            table.add_row("📰 RECENT DEVELOPMENTS", "")
            for i, policy in enumerate(recent_policies[:3], 1):
                title = policy.get("title", "Unknown")[:40] + "..."
                sentiment = policy.get("sentiment", 0)
                emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                table.add_row("", f"{i}. {emoji} {title}")

        self.update(table)


# MarketIndexCard and MarketIndicesPanel have been moved to market_components.py
