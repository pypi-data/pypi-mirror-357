#!/usr/bin/env python3
"""
Data Table Components for Stockholm Dashboard
Contains specialized data table widgets for displaying financial and news data
"""

from typing import Dict, List

from rich.text import Text
from textual.widgets import DataTable, Static

from .base_components import AdjustableDataTable


class TickerNewsTable(AdjustableDataTable):
    """Interactive data table for ticker-specific news articles"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Column width configuration - set AFTER super().__init__
        self.column_widths = {
            "#": 5,
            "Headline": 50,
            "Time": 15,
            "Sentiment": 12,
            "Score": 10,
            "Tickers": 20,
            "Source": 20,
        }

        self.articles_data = []  # Store article data for row selection

        # Initialize columns now that column_widths is set
        self.ensure_columns_initialized()

    def _get_default_column_widths(self) -> dict:
        """Get default column widths"""
        return {
            "#": 5,
            "Headline": 50,
            "Time": 15,
            "Sentiment": 12,
            "Score": 10,
            "Tickers": 20,
            "Source": 20,
        }

    def _get_current_data(self):
        """Get current table data"""
        return self.articles_data.copy()

    def _repopulate_data(self, articles_data: list) -> None:
        """Re-populate the table with article data - NO TEXT TRUNCATION"""
        try:
            self.articles_data = articles_data

            # Apply current sort if any
            if self.sort_column:
                sorted_data = self._sort_data(
                    articles_data, self.sort_column, self.sort_reverse
                )
            else:
                sorted_data = articles_data

            # Store the sorted data for future operations
            self.current_data = sorted_data

            # Validate that we have the expected number of columns
            expected_columns = len(self.column_widths)

            for i, article_data in enumerate(sorted_data):
                article = article_data["article"]
                sentiment_detail = article_data["sentiment_detail"]

                # Extract data using the same logic as update_ticker_news
                headline = article.get("headline", "No headline")
                time_ago = article.get("time_ago", "Unknown time")
                sentiment_score = sentiment_detail.get("polarity", 0)

                # Sentiment styling and text
                if sentiment_score > 0.1:
                    sentiment_emoji = "🟢"
                    sentiment_style = "green"
                    sentiment_text = "Positive"
                elif sentiment_score < -0.1:
                    sentiment_emoji = "🔴"
                    sentiment_style = "red"
                    sentiment_text = "Negative"
                else:
                    sentiment_emoji = "🟡"
                    sentiment_style = "yellow"
                    sentiment_text = "Neutral"

                # Get all tickers mentioned in this article
                mentioned_tickers = sentiment_detail.get("mentioned_tickers", [])

                # Create ticker display string (exclude the current ticker we're viewing)
                # Note: This requires access to TickerNewsPanel which will be imported when needed
                try:
                    current_ticker = getattr(
                        self.app.query_one("#ticker-news-panel"),
                        "current_ticker",
                        None,
                    )
                except Exception:
                    current_ticker = None

                other_tickers = (
                    [t for t in mentioned_tickers if t != current_ticker]
                    if current_ticker
                    else mentioned_tickers
                )

                if other_tickers:
                    # Get ticker sentiments for color coding
                    ticker_sentiments = sentiment_detail.get("ticker_sentiments", {})
                    ticker_parts = []

                    # Show up to 4 other tickers with sentiment indicators
                    for ticker in other_tickers[:4]:
                        if ticker in ticker_sentiments:
                            ticker_sentiment = ticker_sentiments[ticker].get(
                                "polarity", 0
                            )
                            if ticker_sentiment > 0.1:
                                ticker_emoji = "🟢"
                            elif ticker_sentiment < -0.1:
                                ticker_emoji = "🔴"
                            else:
                                ticker_emoji = "🟡"
                            ticker_parts.append(f"{ticker_emoji}{ticker}")
                        else:
                            ticker_parts.append(f"⚪{ticker}")

                    # Add count if there are more tickers
                    if len(other_tickers) > 4:
                        ticker_parts.append(f"+{len(other_tickers)-4}")

                    tickers_display = " ".join(ticker_parts)
                else:
                    tickers_display = "—"  # No other tickers mentioned

                # Get source information
                source = article.get("source", "Unknown")

                # Prepare row data
                row_data = [
                    str(i + 1),
                    headline,  # Full headline without truncation
                    time_ago,  # Keep relative time for easy readability
                    Text(f"{sentiment_emoji} {sentiment_text}", style=sentiment_style),
                    Text(f"{sentiment_score:+.3f}", style=sentiment_style),
                    tickers_display,  # New tickers column
                    source,  # Full source without truncation
                ]

                # Ensure row data matches the number of columns
                if len(row_data) == expected_columns:
                    self.add_row(*row_data)
                else:
                    # Skip rows that don't match the expected column count
                    continue
        except Exception as e:
            # If repopulation fails, just clear the table
            # The data will be refreshed on the next update cycle
            self.clear()
            raise e

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection - store article URL for opening"""
        if event.cursor_row < len(self.articles_data):
            article_data = self.articles_data[event.cursor_row]
            article = article_data["article"]
            article_url = article.get("url", "")

            # Store the URL in the app for the open_article_url action
            if hasattr(self.app, "current_article_url"):
                self.app.current_article_url = article_url

            # Show notification with article info
            headline = article.get("headline", "No headline")[:50] + "..."
            if article_url:
                self.app.notify(
                    f"Selected: {headline} (Press 'o' to open)", severity="information"
                )
            else:
                self.app.notify(
                    f"Selected: {headline} (No URL available)", severity="warning"
                )

    def _sort_data(self, data: list, sort_column: str, reverse: bool) -> list:
        """Sort news article data by the specified column"""

        def get_sort_key(article_data):
            article = article_data["article"]
            sentiment_detail = article_data["sentiment_detail"]

            if sort_column == "#":
                # Sort by index (original order)
                return data.index(article_data)
            elif sort_column == "Headline":
                return article.get("headline", "").lower()
            elif sort_column == "Time":
                # Sort by timestamp for proper chronological order
                return article.get("pub_timestamp", 0)
            elif sort_column == "Sentiment":
                # Sort by sentiment category (Positive, Negative, Neutral)
                sentiment_score = sentiment_detail.get("polarity", 0)
                if sentiment_score > 0.1:
                    return "Positive"
                elif sentiment_score < -0.1:
                    return "Negative"
                else:
                    return "Neutral"
            elif sort_column == "Score":
                return sentiment_detail.get("polarity", 0)
            elif sort_column == "Tickers":
                mentioned_tickers = sentiment_detail.get("mentioned_tickers", [])
                return " ".join(mentioned_tickers) if mentioned_tickers else ""
            elif sort_column == "Source":
                return article.get("source", "").lower()
            else:
                return 0  # Default fallback

        try:
            return sorted(data, key=get_sort_key, reverse=reverse)
        except Exception:
            # If sorting fails, return original data
            return data

    def _fast_repopulate(self, sorted_data: list) -> None:
        """Fast repopulation for news table - only clear rows, keep structure"""
        # Clear only the rows, not the entire table structure
        # Note: Textual DataTable.clear() only clears rows by default
        self.clear()

        # Validate that we have the expected number of columns
        expected_columns = len(self.column_widths)

        for i, article_data in enumerate(sorted_data):
            article = article_data["article"]
            sentiment_detail = article_data["sentiment_detail"]

            # Extract data using the same logic as _repopulate_data
            headline = article.get("headline", "No headline")
            time_ago = article.get("time_ago", "Unknown time")
            sentiment_score = sentiment_detail.get("polarity", 0)

            # Sentiment styling and text
            if sentiment_score > 0.1:
                sentiment_emoji = "🟢"
                sentiment_style = "green"
                sentiment_text = "Positive"
            elif sentiment_score < -0.1:
                sentiment_emoji = "🔴"
                sentiment_style = "red"
                sentiment_text = "Negative"
            else:
                sentiment_emoji = "🟡"
                sentiment_style = "yellow"
                sentiment_text = "Neutral"

            # Get all tickers mentioned in this article
            mentioned_tickers = sentiment_detail.get("mentioned_tickers", [])

            # Create ticker display string (exclude the current ticker we're viewing)
            try:
                current_ticker = getattr(
                    self.app.query_one("#ticker-news-panel"),
                    "current_ticker",
                    None,
                )
            except Exception:
                current_ticker = None

            other_tickers = (
                [t for t in mentioned_tickers if t != current_ticker]
                if current_ticker
                else mentioned_tickers
            )

            if other_tickers:
                # Get ticker sentiments for color coding
                ticker_sentiments = sentiment_detail.get("ticker_sentiments", {})
                ticker_parts = []

                # Show up to 4 other tickers with sentiment indicators
                for ticker in other_tickers[:4]:
                    if ticker in ticker_sentiments:
                        ticker_sentiment = ticker_sentiments[ticker].get("polarity", 0)
                        if ticker_sentiment > 0.1:
                            ticker_emoji = "🟢"
                        elif ticker_sentiment < -0.1:
                            ticker_emoji = "🔴"
                        else:
                            ticker_emoji = "🟡"
                        ticker_parts.append(f"{ticker_emoji}{ticker}")
                    else:
                        ticker_parts.append(f"⚪{ticker}")

                # Add count if there are more tickers
                if len(other_tickers) > 4:
                    ticker_parts.append(f"+{len(other_tickers)-4}")

                tickers_display = " ".join(ticker_parts)
            else:
                tickers_display = "—"  # No other tickers mentioned

            # Get source information
            source = article.get("source", "Unknown")

            # Prepare row data
            row_data = [
                str(i + 1),
                headline,  # Full headline without truncation
                time_ago,  # Keep relative time for easy readability
                Text(f"{sentiment_emoji} {sentiment_text}", style=sentiment_style),
                Text(f"{sentiment_score:+.3f}", style=sentiment_style),
                tickers_display,  # New tickers column
                source,  # Full source without truncation
            ]

            # Ensure row data matches the number of columns
            if len(row_data) == expected_columns:
                self.add_row(*row_data)


class InteractiveTickerTable(AdjustableDataTable):
    """Interactive data table for tickers with sorting and filtering"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Column width configuration - set AFTER super().__init__
        self.column_widths = {
            "Rank": 6,
            "Ticker": 8,
            "Price": 10,
            "Change": 13,
            "Sentiment": 12,
            "Articles": 8,
            "Sector": 20,
        }

        # Initialize columns now that column_widths is set
        self.ensure_columns_initialized()

    def _get_default_column_widths(self) -> dict:
        """Get default column widths"""
        return {
            "Rank": 6,
            "Ticker": 8,
            "Price": 10,
            "Change": 13,
            "Sentiment": 12,
            "Articles": 8,
            "Sector": 20,
        }

    def _get_current_data(self):
        """Get current table data"""
        # Return list of row data for rebuilding
        current_rows = []
        for row_index in range(self.row_count):
            try:
                row_data = self.get_row_at(row_index)
                current_rows.append(row_data)
            except (IndexError, Exception):
                break
        return current_rows

    def _repopulate_data(self, data):
        """Re-populate table with data"""
        try:
            # Validate that we have the expected number of columns
            expected_columns = len(self.column_widths)

            for row_data in data:
                # Ensure row data matches the number of columns
                if len(row_data) == expected_columns:
                    self.add_row(*row_data)
                else:
                    # Skip rows that don't match the expected column count
                    # This can happen during column rebuilds with selection indicators
                    continue
        except Exception as e:
            # If repopulation fails, just clear the table
            # The data will be refreshed on the next update cycle
            self.clear()
            raise e

    def update_data(
        self, ticker_rankings: List[Dict], price_changes: Dict, current_prices: Dict
    ):
        """Update table with ALL ticker data including proper sector information"""
        from ..core.sentiment_analyzer import get_ticker_sector

        # Store the raw data for sorting
        self.ticker_rankings = ticker_rankings
        self.price_changes = price_changes
        self.current_prices = current_prices

        # Build the table data
        table_data = []

        # Get cached sentiment details for accurate article counting
        sentiment_details = []
        if hasattr(self.app, "data_cache") and self.app.data_cache:
            sentiment_details = self.app.data_cache.get("sentiment_details", [])

        # Show ALL tickers, not just top 25
        for i, ticker in enumerate(ticker_rankings, 1):
            ticker_symbol = ticker["ticker"]
            price_change = price_changes.get(ticker_symbol, 0.0)
            current_price = current_prices.get(ticker_symbol, 0.0)

            # Get sector information using the sector mapping
            sector = get_ticker_sector(ticker_symbol)

            # Count articles that actually mention this ticker using the sophisticated detection
            # that was already computed during sentiment analysis
            ticker_article_count = 0
            for detail in sentiment_details:
                mentioned_tickers = detail.get("mentioned_tickers", [])
                if ticker_symbol in mentioned_tickers:
                    ticker_article_count += 1

            # Color coding for sentiment (standardized thresholds)
            sentiment_score = ticker["overall_score"]
            if sentiment_score > 0.1:
                sentiment_color = "green"
            elif sentiment_score < -0.1:
                sentiment_color = "red"
            else:
                sentiment_color = "yellow"

            # Price change emoji and color
            if price_change > 0:
                price_emoji = "📈"
                price_color = "green"
            elif price_change < 0:
                price_emoji = "📉"
                price_color = "red"
            else:
                price_emoji = "➡️"
                price_color = "white"

            # Store row data with raw values for sorting
            row_data = {
                "rank": i,
                "ticker": ticker_symbol,
                "price": current_price,
                "price_change": price_change,
                "sentiment": sentiment_score,
                "articles": ticker_article_count,
                "sector": sector,
                "display_data": [
                    str(i),
                    ticker_symbol,
                    f"${current_price:.2f}",
                    Text(f"{price_emoji} {price_change:+.1f}%", style=price_color),
                    Text(f"{sentiment_score:.3f}", style=sentiment_color),
                    str(ticker_article_count),
                    sector,  # Full sector name without truncation
                ],
            }
            table_data.append(row_data)

        # Store current data for sorting
        self.current_data = table_data

        # Apply current sort if any
        if self.sort_column:
            sorted_data = self._sort_data(
                table_data, self.sort_column, self.sort_reverse
            )
        else:
            sorted_data = table_data

        # Clear and populate table
        self.clear()
        for row_data in sorted_data:
            self.add_row(*row_data["display_data"])

    def _sort_data(self, data: list, sort_column: str, reverse: bool) -> list:
        """Sort ticker data by the specified column"""

        def get_sort_key(row_data):
            if sort_column == "Rank":
                return row_data["rank"]
            elif sort_column == "Ticker":
                return row_data["ticker"]
            elif sort_column == "Price":
                return row_data["price"]
            elif sort_column == "Change":
                return row_data["price_change"]
            elif sort_column == "Sentiment":
                return row_data["sentiment"]
            elif sort_column == "Articles":
                return row_data["articles"]
            elif sort_column == "Sector":
                return row_data["sector"]
            else:
                return 0  # Default fallback

        try:
            return sorted(data, key=get_sort_key, reverse=reverse)
        except Exception:
            # If sorting fails, return original data
            return data

    def _fast_repopulate(self, sorted_data: list) -> None:
        """Fast repopulation for ticker table - only clear rows, keep structure"""
        # Clear only the rows, not the entire table structure
        # Note: Textual DataTable.clear() only clears rows by default
        self.clear()

        # Add sorted rows directly without rebuilding table structure
        for row_data in sorted_data:
            self.add_row(*row_data["display_data"])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection - update right panel with detailed ticker information"""
        from ..core.sentiment_analyzer import get_ticker_sector

        row_data = self.get_row_at(event.cursor_row)
        if row_data:
            ticker_symbol = str(row_data[1])
            # Get the full sector name from the mapping
            sector = get_ticker_sector(ticker_symbol)

            # Extract sentiment value from Text object
            sentiment_text = row_data[4]
            if hasattr(sentiment_text, "plain"):
                sentiment_value = float(sentiment_text.plain)
            else:
                # Fallback for string representation
                sentiment_value = float(str(sentiment_text))

            # Get company name from app's data cache
            company_name = ticker_symbol  # Default fallback
            if hasattr(self.app, "data_cache") and self.app.data_cache:
                company_names = self.app.data_cache.get("company_names", {})
                company_name = company_names.get(ticker_symbol, ticker_symbol)

            ticker_data = {
                "ticker": ticker_symbol,
                "company_name": company_name,
                "price": float(str(row_data[2]).replace("$", "")),
                "sentiment": sentiment_value,
                "articles": int(str(row_data[5])),
                "sector": sector,  # Use the full sector name
                "rank": int(str(row_data[0])),  # Rank column
                "price_change": str(row_data[3]),  # Price change column
            }

            # Update the right panel instead of showing a modal
            self._update_ticker_details_panel(ticker_data)

    def _update_ticker_details_panel(self, ticker_data):
        """Update the ticker details panel in the right pane with comprehensive ticker information"""
        try:
            # Update ticker info panel
            ticker_info = self.app.query_one("#ticker-info", Static)
            info_content = self._create_ticker_info_content(ticker_data)
            ticker_info.update(info_content)

            # Update earnings panel
            ticker_earnings = self.app.query_one("#ticker-earnings", Static)
            earnings_content = self._create_ticker_earnings_content(ticker_data)
            ticker_earnings.update(earnings_content)

            # Update the chart widget
            self._update_ticker_chart(ticker_data)

            # Update the news panel with ticker-specific news
            self._update_ticker_news_panel(ticker_data)

        except Exception:
            # Fallback if panel not found
            pass

    def _create_ticker_info_content(self, ticker_data):
        """Create rich content for the ticker info panel (basic info only)"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        # Basic ticker information
        ticker_symbol = ticker_data.get("ticker", "N/A")
        company_name = ticker_data.get("company_name", ticker_symbol)
        price = ticker_data.get("price", 0)
        sentiment = ticker_data.get("sentiment", 0)
        articles = ticker_data.get("articles", 0)
        sector = ticker_data.get("sector", "N/A")
        rank = ticker_data.get("rank", "N/A")
        price_change = ticker_data.get("price_change", "N/A")

        # Create a table for the info panel
        table = Table.grid(padding=0)
        table.add_column("Field", style="bold cyan", width=16)
        table.add_column("Value", width=32)

        # Company Header - Prominent display
        if company_name and company_name != ticker_symbol:
            # Use available space for company name
            display_name = (
                company_name[:45] + "..." if len(company_name) > 45 else company_name
            )
            table.add_row("🏢 Company:", Text(display_name, style="bold white"))
        else:
            table.add_row("🏢 Company:", Text(ticker_symbol, style="bold white"))

        table.add_row("📈 Symbol:", Text(ticker_symbol, style="bold cyan"))
        table.add_row("🏆 Rank:", f"#{rank}")

        # Price information
        table.add_row("💵 Price:", f"${price:.2f}")

        # Parse price change for better display
        if price_change and price_change != "N/A":
            if "📈" in price_change:
                change_style = "green"
            elif "📉" in price_change:
                change_style = "red"
            else:
                change_style = "yellow"
            table.add_row("📊 Change:", Text(price_change, style=change_style))

        # Performance indicator
        if rank != "N/A":
            rank_num = int(rank)
            if rank_num <= 5:
                performance = "🌟 Top Performer"
                perf_style = "green"
            elif rank_num <= 15:
                performance = "📈 Strong"
                perf_style = "green"
            elif rank_num <= 30:
                performance = "📊 Average"
                perf_style = "yellow"
            else:
                performance = "📉 Below Avg"
                perf_style = "red"
            table.add_row("🏆 Performance:", Text(performance, style=perf_style))

        # Sentiment Analysis
        if sentiment > 0.3:
            sentiment_style = "green"
            sentiment_emoji = "🟢"
            sentiment_desc = "Very Positive"
        elif sentiment > 0.1:
            sentiment_style = "green"
            sentiment_emoji = "🟢"
            sentiment_desc = "Positive"
        elif sentiment > -0.1:
            sentiment_style = "yellow"
            sentiment_emoji = "🟡"
            sentiment_desc = "Neutral"
        elif sentiment > -0.3:
            sentiment_style = "red"
            sentiment_emoji = "🔴"
            sentiment_desc = "Negative"
        else:
            sentiment_style = "red"
            sentiment_emoji = "🔴"
            sentiment_desc = "Very Negative"

        table.add_row(
            "🎯 Sentiment:",
            Text(f"{sentiment_emoji} {sentiment:.3f}", style=sentiment_style),
        )
        table.add_row("📝 Category:", Text(sentiment_desc, style=sentiment_style))
        table.add_row("📰 Articles:", f"{articles} analyzed")
        table.add_row("🏢 Sector:", sector)

        # Investment recommendation
        if sentiment > 0.2 and rank != "N/A" and int(rank) <= 10:
            recommendation = "🟢 Strong Buy"
            rec_style = "green"
        elif sentiment > 0.1 and rank != "N/A" and int(rank) <= 20:
            recommendation = "🟡 Moderate Buy"
            rec_style = "yellow"
        elif sentiment < -0.1:
            recommendation = "🔴 Caution"
            rec_style = "red"
        else:
            recommendation = "⚪ Hold/Monitor"
            rec_style = "white"

        table.add_row("💡 Signal:", Text(recommendation, style=rec_style))

        # Return the table wrapped in a panel with title
        return Panel(table, title="📊 Ticker Info", border_style="cyan")

    def _create_ticker_earnings_content(self, ticker_data):
        """Create comprehensive earnings content using quarterly data"""
        ticker_symbol = ticker_data.get("ticker", "N/A")

        try:
            # Import here to avoid circular imports
            from ..core.earnings_fetcher import get_earnings_summary_for_ticker
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            # Get comprehensive earnings data
            earnings_summary = get_earnings_summary_for_ticker(ticker_symbol)

            if earnings_summary.get("status") != "success":
                # Fallback to simple message
                table = Table.grid(padding=0)
                table.add_column("Field", style="bold cyan", width=16)
                table.add_column("Value", width=32)
                table.add_row("📊 Status:", "No quarterly data available")
                return Panel(table, title="💰 Earnings", border_style="green")

            # Extract data
            latest_quarter = earnings_summary.get("latest_quarter")
            analysis = earnings_summary.get("analysis", {})
            trends = analysis.get("trends", {})

            if not latest_quarter:
                table = Table.grid(padding=0)
                table.add_column("Field", style="bold cyan", width=16)
                table.add_column("Value", width=32)
                table.add_row("📊 Status:", "No quarterly data available")
                return Panel(table, title="💰 Earnings", border_style="green")

            # Create comprehensive earnings table
            table = Table.grid(padding=0)
            table.add_column("Field", style="bold cyan", width=16)
            table.add_column("Value", width=32)

            # Quarter header
            quarter_name = latest_quarter.get("quarter", "Latest Quarter")
            table.add_row("📅 Quarter:", f"[bold yellow]{quarter_name}[/bold yellow]")

            # Revenue data
            revenue = latest_quarter.get("metrics", {}).get("revenue")
            if revenue is not None:
                revenue_display = self._format_currency_for_earnings(revenue)
                table.add_row(
                    "💰 Revenue:", f"[bold green]{revenue_display}[/bold green]"
                )
            else:
                table.add_row("💰 Revenue:", "N/A")

            # Net Income data
            net_income = latest_quarter.get("metrics", {}).get("net_income")
            if net_income is not None:
                net_income_display = self._format_currency_for_earnings(net_income)
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
                trend_info = self._format_trend_info_for_earnings(revenue_trend)
                table.add_row("📈 Rev Trend:", trend_info)
            else:
                table.add_row("📈 Rev Trend:", "N/A")

            # Income trend
            income_trend = trends.get("net_income", {})
            if income_trend:
                trend_info = self._format_trend_info_for_earnings(income_trend)
                table.add_row("📊 Inc Trend:", trend_info)
            else:
                table.add_row("📊 Inc Trend:", "N/A")

            # Overall assessment
            overall_assessment = self._calculate_overall_assessment_for_earnings(
                revenue_trend, income_trend, revenue, net_income
            )
            table.add_row("🏆 Overall:", overall_assessment)

            return Panel(table, title="💰 Earnings", border_style="green")

        except Exception as e:
            # Fallback to simple display
            table = Table.grid(padding=0)
            table.add_column("Field", style="bold cyan", width=16)
            table.add_column("Value", width=32)
            table.add_row("📊 Status:", "Earnings data unavailable")
            table.add_row(
                "💡 Info:",
                str(e)[:30] if hasattr(self.app, "debug_mode") else "Check connection",
            )

            return Panel(table, title="💰 Earnings", border_style="green")

    def _format_currency_for_earnings(self, amount: float) -> str:
        """Format currency amounts in billions/millions for earnings display"""
        if abs(amount) >= 1e9:
            return f"${amount/1e9:.1f}B"
        elif abs(amount) >= 1e6:
            return f"${amount/1e6:.0f}M"
        elif abs(amount) >= 1e3:
            return f"${amount/1e3:.0f}K"
        else:
            return f"${amount:.0f}"

    def _format_trend_info_for_earnings(self, trend_data: dict):
        """Format trend information with appropriate styling for earnings"""
        from rich.text import Text

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

    def _calculate_overall_assessment_for_earnings(
        self, revenue_trend: dict, income_trend: dict, revenue: float, net_income: float
    ):
        """Calculate overall financial health assessment for earnings"""
        from rich.text import Text

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

    def _update_ticker_chart(self, ticker_data):
        """Update the ticker chart with price history and overlays using ArticleTimelineChart"""
        try:
            from .charts import ArticleTimelineChart

            ticker_symbol = ticker_data.get("ticker", "N/A")

            # Get the chart widget (now ArticleTimelineChart)
            chart_widget = self.app.query_one("#ticker-chart", ArticleTimelineChart)

            # Get historical price data for this ticker
            historical_data = self._get_ticker_price_history(ticker_symbol)

            if not historical_data or len(historical_data) < 2:
                # No data available - show placeholder
                chart_widget.plt.clear_data()
                chart_widget.plt.clear_figure()
                chart_widget.plt.text(
                    0.5,
                    0.5,
                    f"Loading {ticker_symbol} price data...",
                    alignment="center",
                )
                chart_widget.plt.title(f"{ticker_symbol} - Loading...")
                chart_widget.plt.plotsize(80, 12)
                chart_widget.refresh()
                return

            # Get news data and sentiment details from app cache
            news_data = []
            sentiment_details = []
            if hasattr(self.app, "data_cache") and self.app.data_cache:
                news_data = self.app.data_cache.get("news_data", [])
                sentiment_details = self.app.data_cache.get("sentiment_details", [])

            # Prepare price data in the format expected by ArticleTimelineChart
            price_data = {
                "prices": [item["close"] for item in historical_data],
                "dates": [item["date"] for item in historical_data],
            }

            # Use the ArticleTimelineChart's update_chart method which has working overlays
            # Format articles_data in the expected format for ArticleTimelineChart
            articles_data = []
            if news_data and sentiment_details:
                for i, article in enumerate(news_data):
                    if i < len(sentiment_details):
                        articles_data.append(
                            {
                                "article": article,
                                "sentiment_detail": sentiment_details[
                                    i
                                ],  # Fix: use "sentiment_detail" key
                            }
                        )

            chart_widget.update_chart(ticker_symbol, articles_data, price_data)

        except Exception as e:
            # Fallback if chart update fails
            try:
                from .charts import ArticleTimelineChart

                chart_widget = self.app.query_one("#ticker-chart", ArticleTimelineChart)
                chart_widget.plt.clear_data()
                chart_widget.plt.clear_figure()
                chart_widget.plt.text(
                    0.5, 0.5, f"Chart error: {str(e)[:30]}...", alignment="center"
                )
                chart_widget.plt.title(
                    f"{ticker_data.get('ticker', 'N/A')} - Chart Error"
                )
                chart_widget.plt.plotsize(80, 12)
                chart_widget.refresh()
            except Exception:
                pass  # If even the fallback fails, continue silently

    def _get_ticker_price_history(self, ticker_symbol: str):
        """Get historical price data for a ticker"""
        try:
            import yfinance as yf

            # Get 6 months of historical data
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="6mo")

            if hist.empty:
                return []

            # Convert to list of dictionaries
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append(
                    {"date": date, "close": row["Close"], "timestamp": date.timestamp()}
                )

            return historical_data

        except Exception:
            # If data fetch fails, return empty list
            return []

    def _update_ticker_news_panel(self, ticker_data):
        """Update the ticker news panel with ticker-specific news"""
        try:
            ticker_symbol = ticker_data.get("ticker", "N/A")

            # Get the news panel widget
            news_panel = self.app.query_one("#ticker-news-panel")

            # Get news data and sentiment details from app cache
            news_data = []
            sentiment_details = []
            if hasattr(self.app, "data_cache") and self.app.data_cache:
                news_data = self.app.data_cache.get("news_data", [])
                sentiment_details = self.app.data_cache.get("sentiment_details", [])

            # Update the news panel with the selected ticker and news data
            if hasattr(news_panel, "update_ticker_news"):
                news_panel.update_ticker_news(
                    ticker_symbol, news_data, sentiment_details
                )

        except Exception:
            # If news panel update fails, continue silently
            pass
