"""
Chart components for the Stockholm dashboard.

This module contains chart widgets for displaying financial data and sentiment analysis.
"""

from typing import List, Dict
from textual.widgets import Static
from textual_plotext import PlotextPlot
from rich.panel import Panel


class ArticleTimelineChart(PlotextPlot):
    """Chart showing article publication timeline correlated with stock price - SAME as ticker info chart but focused date range"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "📈 Article Timeline with Sentiment Indicators"

        # Initialize with a default empty chart to prevent render errors
        self.plt.clear_data()
        self.plt.clear_figure()
        self.plt.text("Loading chart data...", 0.5, 0.5, alignment="center")
        self.plt.title("Chart - Loading...")
        self.plt.plotsize(80, 12)

    def update_chart(
        self, ticker_symbol: str, articles_data: List[Dict], price_data: Dict = None
    ):
        """Update chart using EXACT same data source as Headlines tab"""
        try:
            # Use EXACT same data source as Headlines tab
            # Get news data from app cache (same as Headlines tab)
            if not hasattr(self.app, "data_cache") or not self.app.data_cache:
                self.plt.clear_data()
                self.plt.clear_figure()
                self.plt.text(0.5, 0.5, "No data cache available", alignment="center")
                self.plt.title(f"{ticker_symbol} - No Cache")
                self.plt.plotsize(80, 12)
                self.refresh()
                return

            news_data = self.app.data_cache.get("news_data", [])
            sentiment_details = self.app.data_cache.get("sentiment_details", [])

            if not news_data or not sentiment_details:
                self.plt.clear_data()
                self.plt.clear_figure()
                self.plt.text(0.5, 0.5, "No news data available", alignment="center")
                self.plt.title(f"{ticker_symbol} - No News Data")
                self.plt.plotsize(80, 12)
                self.refresh()
                return

            # Filter articles using EXACT same logic as Headlines tab
            # (EXACT same as TickerNewsPanel.update_ticker_news in panel_components.py)
            ticker_articles = []
            for i, article in enumerate(news_data):
                # Check if ticker is mentioned using the pre-computed mentioned_tickers list
                if i < len(sentiment_details):
                    mentioned_tickers = sentiment_details[i].get(
                        "mentioned_tickers", []
                    )
                    if ticker_symbol in mentioned_tickers:
                        article_data = {
                            "article": article,
                            "sentiment_detail": sentiment_details[i],
                            "index": i,
                        }
                        ticker_articles.append(article_data)

            if not ticker_articles:
                self.plt.clear_data()
                self.plt.clear_figure()
                self.plt.text(
                    0.5,
                    0.5,
                    f"No articles found for {ticker_symbol}",
                    alignment="center",
                )
                self.plt.title(f"{ticker_symbol} - No Articles")
                self.plt.plotsize(80, 12)
                self.refresh()
                return

            # Get article dates for determining focused range
            article_dates = []
            for article_data in ticker_articles:
                article = article_data["article"]
                pub_timestamp = article.get("pub_timestamp")
                if pub_timestamp:
                    try:
                        import pandas as pd

                        article_date = pd.to_datetime(pub_timestamp, unit="s")
                        article_dates.append(article_date)
                    except Exception:
                        continue

            if not article_dates:
                self.plt.clear_data()
                self.plt.clear_figure()
                self.plt.text(0.5, 0.5, "No valid article dates", alignment="center")
                self.plt.title(f"{ticker_symbol} - Invalid Date Data")
                self.plt.plotsize(80, 12)
                self.refresh()
                return

            # Get focused price data (same approach as ticker info but different date range)
            prices, dates = self._get_focused_ticker_price_history(
                ticker_symbol, article_dates
            )

            if len(prices) < 2:
                self.plt.clear_data()
                self.plt.clear_figure()
                self.plt.text(0.5, 0.5, "No price data available", alignment="center")
                self.plt.title(f"{ticker_symbol} - No Data")
                self.plt.plotsize(80, 12)
                self.refresh()
                return

            # Clear previous plot
            self.plt.clear_data()
            self.plt.clear_figure()

            # EXACT same plotting approach as ticker info chart
            chart_x_values = list(range(len(prices)))
            self.plt.plot(
                chart_x_values, prices, marker="braille", color="cyan", fillx=True
            )

            # Get article data for this ticker within the chart date range using Headlines tab data
            article_dates_in_range, article_sentiments = (
                self._get_ticker_article_dates_from_headlines_data(
                    ticker_symbol, dates, ticker_articles
                )
            )

            # Get earnings data for this ticker within the chart date range
            earnings_dates_in_range = self._get_ticker_earnings_dates_in_range(
                ticker_symbol, dates
            )

            # Add earnings markers first (so they appear behind article markers)
            if earnings_dates_in_range:
                for earnings_date in earnings_dates_in_range:
                    # Find x position for this earnings date
                    x_pos = None
                    price_for_date = None

                    # Find x position and price for this date
                    for j, date in enumerate(dates):
                        if date.date() == earnings_date.date():
                            x_pos = j
                            price_for_date = prices[j]
                            break

                    if x_pos is not None and price_for_date is not None:
                        # Plot earnings diamond at top of chart for better visibility
                        try:
                            # Position diamond at the top of the chart (max price level)
                            y_max = max(prices)
                            self.plt.scatter(
                                [x_pos],
                                [y_max],
                                color="orange",
                                marker="♦",
                            )
                        except Exception:
                            try:
                                # Fallback: try "orange+" for brighter orange
                                y_max = max(prices)
                                self.plt.scatter(
                                    [x_pos],
                                    [y_max],
                                    color="orange+",
                                    marker="♦",
                                )
                            except Exception:
                                # Final fallback: skip earnings plotting if it fails
                                pass

            # Add article markers using EXACT same approach as ticker info chart with stacking
            if article_dates_in_range and article_sentiments:
                # Group articles by date for stacking
                articles_by_date = {}
                for article_date, sentiment in zip(
                    article_dates_in_range, article_sentiments
                ):
                    date_key = article_date.date()
                    if date_key not in articles_by_date:
                        articles_by_date[date_key] = []
                    articles_by_date[date_key].append((article_date, sentiment))

                # Plot article markers with sentiment-based colors and stacking
                for date_key, articles_on_date in articles_by_date.items():
                    x_pos = None
                    price_for_date = None

                    # Find x position and price for this date
                    for j, date in enumerate(dates):
                        if date.date() == date_key:
                            x_pos = j
                            price_for_date = prices[j]
                            break

                    if x_pos is not None and price_for_date is not None:
                        # Calculate price range for stacking with enhanced visibility
                        price_range = max(prices) - min(prices)
                        stack_offset = (
                            price_range * 0.03
                        )  # 3% of price range per stack level for better visibility

                        # Debug logging for stacking
                        if hasattr(self.app, "verbose_mode") and self.app.verbose_mode:
                            print(
                                f"🔍 STACKING DEBUG: {len(articles_on_date)} articles on {date_key}, stack_offset={stack_offset:.2f}"
                            )

                        # Sort articles by sentiment for proper layering (neutral first, then positive/negative on top)
                        # This ensures colored triangles are visible on top of neutral circles
                        def sentiment_sort_key(article):
                            sentiment = article[1]
                            if (
                                abs(sentiment) <= 0.1
                            ):  # Neutral articles first (bottom layer) - standardized threshold
                                return (0, sentiment)
                            else:  # Positive/negative articles last (top layer)
                                return (1, sentiment)

                        articles_on_date.sort(key=sentiment_sort_key)

                        for stack_index, (_, sentiment) in enumerate(articles_on_date):
                            # Calculate stacked position first
                            total_articles = len(articles_on_date)
                            center_offset = (total_articles - 1) * stack_offset / 2
                            stacked_price = (
                                price_for_date
                                + (stack_index * stack_offset)
                                - center_offset
                            )

                            # Enhanced sentiment visualization with distinct shapes and colors
                            if (
                                sentiment > 0.1
                            ):  # Positive sentiment (standardized threshold)
                                # Green triangle pointing up for positive news
                                marker_color = "green"
                                marker_symbol = "▲"
                                if (
                                    hasattr(self.app, "verbose_mode")
                                    and self.app.verbose_mode
                                ):
                                    print(
                                        f"📈 Plotting GREEN ▲ for positive sentiment: {sentiment:.3f}"
                                    )

                            elif (
                                sentiment < -0.1
                            ):  # Negative sentiment (standardized threshold)
                                # Red triangle pointing down for negative news
                                marker_color = "red"
                                marker_symbol = "▼"
                                if (
                                    hasattr(self.app, "verbose_mode")
                                    and self.app.verbose_mode
                                ):
                                    print(
                                        f"📉 Plotting RED ▼ for negative sentiment: {sentiment:.3f}"
                                    )

                            else:  # Neutral sentiment
                                # Orange circle for neutral news
                                marker_color = "orange"
                                marker_symbol = "●"
                                if (
                                    hasattr(self.app, "verbose_mode")
                                    and self.app.verbose_mode
                                ):
                                    print(
                                        f"🟠 Plotting ORANGE ● for neutral sentiment: {sentiment:.3f}"
                                    )

                            # Plot sentiment marker with enhanced visibility
                            try:
                                self.plt.scatter(
                                    [x_pos],
                                    [stacked_price],
                                    color=marker_color,
                                    marker=marker_symbol,
                                )
                            except Exception as e:
                                # Fallback to basic plotting if scatter fails
                                if (
                                    hasattr(self.app, "verbose_mode")
                                    and self.app.verbose_mode
                                ):
                                    print(f"⚠️ Scatter plot failed, using fallback: {e}")
                                self.plt.plot(
                                    [x_pos],
                                    [stacked_price],
                                    color=marker_color,
                                    marker=marker_symbol,
                                )

                # Create article data for influence lines (use original approach)
                article_data = list(zip(article_dates_in_range, article_sentiments))
                article_data.sort(key=lambda x: x[0])  # Sort by date

                for i, (_, _) in enumerate(article_data):
                    # Add influence section line (vertical line from this article to next)
                    if len(prices) > 0 and len(dates) > 0:  # Ensure we have data
                        if i < len(article_data) - 1:  # Not the last article
                            next_article_date = article_data[i + 1][0]
                            next_x_pos = self._get_x_position_for_date(
                                next_article_date, dates
                            )
                            if next_x_pos is not None and next_x_pos > 0:
                                # Draw vertical line at the end of this article's influence period
                                influence_x = max(
                                    0, next_x_pos - 0.5
                                )  # Slightly before next article
                                min_price = min(prices)
                                max_price = max(prices)

                                # Draw influence section line
                                try:
                                    influence_y_values = [min_price, max_price]
                                    influence_x_values = [influence_x, influence_x]
                                    self.plt.plot(
                                        influence_x_values,
                                        influence_y_values,
                                        color="gray",
                                        marker="",
                                        linestyle="--",
                                    )
                                except Exception:
                                    pass  # Skip if plotting fails
                        else:
                            # Last article - draw line to end of chart
                            if len(dates) > 1:
                                end_x = len(dates) - 1
                                min_price = min(prices)
                                max_price = max(prices)

                                # Draw final influence section line
                                try:
                                    influence_y_values = [min_price, max_price]
                                    influence_x_values = [end_x, end_x]
                                    self.plt.plot(
                                        influence_x_values,
                                        influence_y_values,
                                        color="gray",
                                        marker="",
                                        linestyle="--",
                                    )
                                except Exception:
                                    pass  # Skip if plotting fails

            # EXACT same x-axis formatting as ticker info chart
            if dates:
                date_labels = [date.strftime("%m/%d") for date in dates]
                step = max(1, len(date_labels) // 12)  # Show about 12 labels
                x_ticks = list(range(0, len(date_labels), step))
                x_labels = [date_labels[i] for i in x_ticks]
                self.plt.xticks(x_ticks, x_labels)

            # EXACT same title format as ticker info chart but with focused range info
            min_price = min(prices)
            max_price = max(prices)
            price_range = f"Range: ${min_price:.2f} - ${max_price:.2f}"
            article_count = len(article_dates_in_range) if article_dates_in_range else 0

            # Calculate 6-month date range for title
            import pandas as pd

            chart_start_date = dates[0].strftime("%m/%d") if dates else "N/A"
            chart_end_date = dates[-1].strftime("%m/%d") if dates else "N/A"
            date_info = f"6 Months {chart_start_date}-{chart_end_date}"

            # Enhanced title with sentiment legend
            sentiment_legend = (
                "🟢▲ Positive | 🔴▼ Negative | 🟠● Neutral | 🟠♦ Earnings"
            )
            self.plt.title(
                f"{ticker_symbol} - {date_info} | {price_range} | {article_count} Articles\n{sentiment_legend}"
            )

            # EXACT same styling as ticker info chart
            self.plt.xlabel("Date")
            self.plt.ylabel("Price ($)")
            self.plt.grid(True, True)
            self.plt.plotsize(80, 12)  # Same size as ticker info chart

            self.refresh()

        except Exception as e:
            # Fallback display
            self.plt.clear_data()
            self.plt.clear_figure()
            self.plt.text(
                0.5, 0.5, f"Chart error: {str(e)[:30]}...", alignment="center"
            )
            self.plt.title(f"{ticker_symbol} - Chart Error")
            self.plt.plotsize(80, 12)
            self.refresh()

    def _get_price_data_for_range(self, ticker_symbol: str, article_dates: List):
        """Get stock price data covering the article date range (legacy method)"""
        try:
            import yfinance as yf
            import pandas as pd

            if not article_dates:
                return [], []

            # Determine date range (add buffer around article dates)
            start_date = min(article_dates) - pd.Timedelta(days=7)
            end_date = max(article_dates) + pd.Timedelta(days=7)

            # Fetch stock data
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(start=start_date, end=end_date)

            if not hist.empty:
                prices = hist["Close"].tolist()
                dates = hist.index.tolist()
                return prices, dates
            else:
                return [], []

        except Exception:
            return [], []

    def _get_focused_ticker_price_history(
        self, ticker_symbol: str, article_dates: List
    ):
        """Get focused price history using only trading days"""
        try:
            import yfinance as yf
            import pandas as pd

            # Always show 6 months of data regardless of article dates
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=180)  # 6 months = ~180 days

            # Get trading data - this will only include trading days
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(start=start_date, end=end_date + pd.Timedelta(days=10))

            if not hist.empty:
                # Return EXACT same format as ticker info chart
                prices = hist["Close"].tolist()
                dates = hist.index.tolist()
                return prices, dates
            else:
                return [], []

        except Exception:
            return [], []

    def _get_ticker_article_dates_focused(
        self, ticker_symbol: str, chart_dates_range: List, articles_data: List[Dict]
    ):
        """Get article dates using EXACT same approach as Headlines tab"""
        try:
            import pandas as pd

            # Use EXACT same approach as Headlines tab (TickerNewsPanel.update_ticker_news)
            # Get news data from app cache (same as Headlines tab)
            if not hasattr(self.app, "data_cache") or not self.app.data_cache:
                return [], []

            news_data = self.app.data_cache.get("news_data", [])
            sentiment_details = self.app.data_cache.get("sentiment_details", [])

            if not news_data or not sentiment_details:
                return [], []

            # Get the date range for filtering
            if not chart_dates_range:
                return [], []

            start_date = chart_dates_range[0]
            end_date = chart_dates_range[-1]

            article_dates = []
            article_sentiments = []

            # Filter articles that mention this ticker using EXACT same logic as Headlines tab
            for i, article in enumerate(news_data):
                if i >= len(sentiment_details):
                    continue

                # Check if ticker is mentioned using the pre-computed mentioned_tickers list
                # (EXACT same logic as Headlines tab in panel_components.py line 55)
                mentioned_tickers = sentiment_details[i].get("mentioned_tickers", [])
                if ticker_symbol not in mentioned_tickers:
                    continue

                # Get publication timestamp
                pub_timestamp = article.get("pub_timestamp")
                if pub_timestamp:
                    try:
                        # EXACT same date conversion as ticker info chart
                        article_date = pd.to_datetime(
                            pub_timestamp, unit="s"
                        ).tz_localize("UTC")

                        # Convert to same timezone as chart dates if needed
                        if hasattr(start_date, "tz") and start_date.tz:
                            article_date = article_date.tz_convert(start_date.tz)
                        else:
                            article_date = article_date.tz_localize(None)

                        # Map article to nearest trading day if it falls on non-trading day
                        mapped_date = self._map_to_nearest_trading_day(
                            article_date, chart_dates_range
                        )

                        # Check if mapped date is within chart date range
                        if mapped_date and start_date <= mapped_date <= end_date:
                            article_dates.append(mapped_date)

                            # Use EXACT same sentiment logic as Headlines tab
                            # (EXACT same as panel_components.py line 118)
                            sentiment_detail = sentiment_details[i]
                            sentiment_score = sentiment_detail.get("polarity", 0.0)

                            article_sentiments.append(sentiment_score)

                    except Exception:
                        continue

            return article_dates, article_sentiments

        except Exception:
            return [], []

    def _get_ticker_article_dates_from_headlines_data(
        self, ticker_symbol: str, chart_dates_range: List, ticker_articles: List[Dict]
    ):
        """Get article dates using the EXACT same filtered data as Headlines tab"""
        try:
            import pandas as pd

            # Get the date range for filtering
            if not chart_dates_range:
                return [], []

            start_date = chart_dates_range[0]
            end_date = chart_dates_range[-1]

            article_dates = []
            article_sentiments = []

            # Process the already-filtered ticker articles (same as Headlines tab)
            for article_data in ticker_articles:
                article = article_data["article"]
                sentiment_detail = article_data["sentiment_detail"]

                # Get publication timestamp
                pub_timestamp = article.get("pub_timestamp")
                if pub_timestamp:
                    try:
                        # EXACT same date conversion as ticker info chart
                        article_date = pd.to_datetime(
                            pub_timestamp, unit="s"
                        ).tz_localize("UTC")

                        # Convert to same timezone as chart dates if needed
                        if hasattr(start_date, "tz") and start_date.tz:
                            article_date = article_date.tz_convert(start_date.tz)
                        else:
                            article_date = article_date.tz_localize(None)

                        # Map article to nearest trading day if it falls on non-trading day
                        mapped_date = self._map_to_nearest_trading_day(
                            article_date, chart_dates_range
                        )

                        # Check if mapped date is within chart date range
                        if mapped_date and start_date <= mapped_date <= end_date:
                            article_dates.append(mapped_date)

                            # Use EXACT same sentiment logic as Headlines tab
                            # (EXACT same as panel_components.py line 118)
                            sentiment_score = sentiment_detail.get("polarity", 0.0)
                            article_sentiments.append(sentiment_score)

                    except Exception:
                        continue

            return article_dates, article_sentiments

        except Exception:
            return [], []

    def _get_ticker_earnings_dates_in_range(
        self, ticker_symbol: str, chart_dates_range: List
    ):
        """Get earnings dates for this ticker within the chart date range using cached data"""
        try:
            # Get the date range for filtering
            if not chart_dates_range:
                return []

            start_date = chart_dates_range[0]
            end_date = chart_dates_range[-1]

            # Try to get earnings data from the app's cache first
            earnings_data = None
            if (
                hasattr(self.app, "data_cache")
                and "earnings_data" in self.app.data_cache
            ):
                earnings_data = self.app.data_cache["earnings_data"].get(ticker_symbol)

            # If not in cache, fetch it directly
            if not earnings_data:
                from src.core.earnings_fetcher import (
                    cached_get_ticker_quarterly_earnings,
                )

                earnings_data = cached_get_ticker_quarterly_earnings(ticker_symbol)

            if not earnings_data or not earnings_data.get("quarters"):
                return []
            earnings_dates_in_range = []

            # Process quarters and extract dates within range
            for quarter in earnings_data["quarters"]:
                try:
                    # Parse the quarter date (format: "YYYY-MM-DD")
                    quarter_date_str = quarter.get("date")
                    if not quarter_date_str:
                        continue

                    import pandas as pd

                    # Parse the date and convert to pandas Timestamp for consistency with chart dates
                    earnings_date = pd.to_datetime(quarter_date_str)

                    # Convert to same timezone as chart dates if needed
                    if hasattr(start_date, "tz") and start_date.tz:
                        if earnings_date.tzinfo is None:
                            earnings_date = earnings_date.tz_localize("UTC").tz_convert(
                                start_date.tz
                            )
                        else:
                            earnings_date = earnings_date.tz_convert(start_date.tz)
                    else:
                        if earnings_date.tzinfo is not None:
                            earnings_date = earnings_date.tz_localize(None)

                    # Map earnings date to nearest trading day if it falls on non-trading day
                    mapped_date = self._map_to_nearest_trading_day(
                        earnings_date, chart_dates_range
                    )

                    # Check if mapped date is within chart date range
                    if mapped_date and start_date <= mapped_date <= end_date:
                        earnings_dates_in_range.append(mapped_date)

                except (ValueError, TypeError):
                    continue

            return earnings_dates_in_range

        except Exception:
            # If earnings fetching fails, just return empty list (don't break the chart)
            return []

    def _map_to_nearest_trading_day(self, article_date, chart_dates_range):
        """
        Map article published on non-trading day to the nearest (last) trading day.

        This is necessary because:
        1. Articles can be published on weekends/holidays when markets are closed
        2. Stock price charts only contain trading days (Mon-Fri, excluding holidays)
        3. We need to map weekend articles to the last available trading day for visualization

        Algorithm:
        - Normalize dates to remove time components for accurate comparison
        - Search backwards through trading days to find the last one <= article date
        - If article is from before all trading data, use the earliest trading day

        Args:
            article_date: When the article was published (can be any day)
            chart_dates_range: List of available trading days from price data

        Returns:
            datetime: The nearest trading day for chart positioning
        """
        try:
            if not chart_dates_range:
                return article_date  # Fallback to original date

            import pandas as pd

            # Convert article date to normalized date for comparison (removes time component)
            # This ensures we're comparing dates only, not datetime with time
            if hasattr(article_date, "normalize"):
                article_date_norm = article_date.normalize()
            else:
                article_date_norm = pd.Timestamp(article_date).normalize()

            # Find the last trading day that is <= article date
            # We search backwards because we want the most recent trading day before/on article date
            last_trading_day = None
            for chart_date in reversed(chart_dates_range):
                # Normalize chart date for comparison
                if hasattr(chart_date, "normalize"):
                    chart_date_norm = chart_date.normalize()
                else:
                    chart_date_norm = pd.Timestamp(chart_date).normalize()

                # If this trading day is on or before the article date, use it
                if chart_date_norm <= article_date_norm:
                    last_trading_day = chart_date
                    break

            # Edge case: If no trading day found before article date (article is very old),
            # use the last available trading day as fallback
            if last_trading_day is None and chart_dates_range:
                last_trading_day = chart_dates_range[-1]

            return last_trading_day if last_trading_day is not None else article_date

        except Exception:
            # Robust fallback: if any date parsing fails, return original date
            return article_date  # Fallback to original date

    def _find_price_at_date(self, article_date, price_dates, prices):
        """Find the price and x-position closest to the article date"""
        try:
            if not price_dates or not prices:
                return None, None

            # Find closest date
            closest_idx = min(
                range(len(price_dates)),
                key=lambda i: abs((price_dates[i] - article_date).total_seconds()),
            )

            return prices[closest_idx], closest_idx

        except Exception:
            return None, None

    def _plot_articles_only(self, article_dates, article_sentiments):
        """Plot just article timeline when no price data available (legacy method)"""
        try:
            # Create a simple timeline with prominent markers for each article
            for i, sentiment in enumerate(article_sentiments):
                if sentiment > 0.1:
                    color = "green"
                    marker_symbol = "▲"  # Up triangle for positive
                elif sentiment < -0.1:
                    color = "red"
                    marker_symbol = "▼"  # Down triangle for negative
                else:
                    color = "orange"
                    marker_symbol = "●"  # Circle for neutral

                # Draw thick vertical line for each article
                line_y_values = []
                line_x_values = []

                # Create multiple points for a thick vertical line
                for step in range(11):
                    y_val = step / 10  # From 0 to 1
                    line_y_values.append(y_val)
                    line_x_values.append(i)

                # Plot the vertical line
                self.plt.plot(
                    line_x_values, line_y_values, color=color, marker="braille"
                )

                # Add prominent marker at top
                self.plt.scatter([i], [1.1], color=color, marker=marker_symbol)

            # Format x-axis with actual publication dates
            if len(article_dates) > 0:
                x_ticks = list(range(len(article_dates)))
                x_labels = [
                    article_dates[i].strftime("%Y-%m-%d") for i in x_ticks
                ]  # Full calendar dates
                self.plt.xticks(x_ticks, x_labels)

                # Add date labels above each marker for clarity
                for i, article_date in enumerate(article_dates):
                    date_str = article_date.strftime("%m/%d")
                    try:
                        # Try to add text label above the marker
                        self.plt.text(date_str, i, 1.2)
                    except Exception:
                        # If text doesn't work, the x-axis labels will show the dates
                        pass

        except Exception:
            pass

    def _plot_focused_articles_only(self, article_dates, article_sentiments):
        """Plot FOCUSED article timeline when no price data available - enhanced for sentiment visibility"""
        try:
            if not article_dates or not article_sentiments:
                return

            # Sort articles by date for better timeline visualization
            sorted_data = sorted(
                zip(article_dates, article_sentiments), key=lambda x: x[0]
            )
            sorted_dates, sorted_sentiments = zip(*sorted_data)

            # Create enhanced timeline with better sentiment visualization
            for i, sentiment in enumerate(sorted_sentiments):
                # Enhanced sentiment color coding
                if sentiment > 0.1:
                    color = "green"
                    marker_symbol = "▲"  # Up triangle for positive
                elif sentiment < -0.1:
                    color = "red"
                    marker_symbol = "▼"  # Down triangle for negative
                else:
                    color = "orange"
                    marker_symbol = "●"  # Circle for neutral

                # Create sentiment-based height for visual impact
                base_height = 0.5
                sentiment_height = base_height + (
                    sentiment * 0.3
                )  # Scale sentiment to height
                sentiment_height = max(
                    0.1, min(0.9, sentiment_height)
                )  # Clamp between 0.1 and 0.9

                # Draw enhanced vertical line with sentiment-based styling
                line_y_values = []
                line_x_values = []

                # Create multiple points for a thick vertical line from 0 to sentiment height
                for step in range(15):  # More points for smoother line
                    y_val = (step / 14) * sentiment_height  # Scale to sentiment height
                    line_y_values.append(y_val)
                    line_x_values.append(i)

                # Plot the vertical line
                self.plt.plot(
                    line_x_values, line_y_values, color=color, marker="braille"
                )

                # Add prominent marker at the sentiment height
                self.plt.scatter(
                    [i], [sentiment_height], color=color, marker=marker_symbol
                )

                # Add additional markers for maximum visibility
                self.plt.scatter(
                    [i], [sentiment_height + 0.05], color=color, marker=marker_symbol
                )
                self.plt.scatter(
                    [i], [sentiment_height - 0.05], color=color, marker=marker_symbol
                )

            # Enhanced x-axis formatting for focused view
            if len(sorted_dates) > 0:
                x_ticks = list(range(len(sorted_dates)))
                # Use more detailed date format for focused view
                x_labels = [sorted_dates[i].strftime("%m/%d %H:%M") for i in x_ticks]
                self.plt.xticks(x_ticks, x_labels)

            # Set appropriate y-axis range for sentiment visualization
            self.plt.ylim(0, 1.2)

        except Exception:
            pass

    def _interpolate_price_for_date(self, article_date, chart_dates, chart_prices):
        """Find the price at or closest to the article publication date"""
        try:
            import pandas as pd

            if not chart_dates or not chart_prices:
                return None

            # Convert to pandas for easier date handling
            price_series = pd.Series(chart_prices, index=chart_dates)

            # Find the closest date
            closest_date = min(
                chart_dates, key=lambda x: abs((x - article_date).total_seconds())
            )

            # Return the price at that date
            return price_series[closest_date]

        except Exception:
            return None

    def _get_x_position_for_date(self, article_date, chart_dates):
        """Get the x-axis position for the article date on the chart"""
        try:
            if not chart_dates:
                return None

            # Find the closest date index
            closest_idx = min(
                range(len(chart_dates)),
                key=lambda i: abs((chart_dates[i] - article_date).total_seconds()),
            )

            return closest_idx

        except Exception:
            return None


class RealTimeChart(Static):
    """Real-time sentiment chart using ASCII/Unicode characters"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentiment_history = []
        self.border_title = "📈 Sentiment Trend"

    def update_sentiment(self, sentiment_score: float):
        """Add new sentiment data point"""
        self.sentiment_history.append(sentiment_score)
        if len(self.sentiment_history) > 50:  # Keep last 50 points
            self.sentiment_history.pop(0)

        self._render_chart()

    def _render_chart(self):
        """Render the ASCII chart"""
        if len(self.sentiment_history) < 2:
            self.update("📈 Collecting data...")
            return

        # Create simple sparkline chart
        chart_chars = "▁▂▃▄▅▆▇█"
        chart_data = []

        # Normalize data to 0-7 range for chart characters
        min_val = min(self.sentiment_history)
        max_val = max(self.sentiment_history)

        if max_val == min_val:
            # All values are the same
            chart_data = ["▄"] * len(self.sentiment_history[-30:])
        else:
            for val in self.sentiment_history[-30:]:
                normalized = (val - min_val) / (max_val - min_val)
                char_index = min(7, max(0, int(normalized * 7)))
                chart_data.append(chart_chars[char_index])

        # Create chart display
        chart_line = "".join(chart_data)
        current_val = self.sentiment_history[-1]

        # Determine trend
        if len(self.sentiment_history) >= 2:
            trend = (
                "📈"
                if self.sentiment_history[-1] > self.sentiment_history[-2]
                else "📉"
            )
        else:
            trend = "➡️"

        chart_text = f"Trend: {chart_line}\n"
        chart_text += f"Current: {current_val:+.3f} {trend}\n"
        chart_text += f"Range: {min_val:.3f} to {max_val:.3f}"

        self.update(Panel(chart_text, title="📈 Live Sentiment"))
