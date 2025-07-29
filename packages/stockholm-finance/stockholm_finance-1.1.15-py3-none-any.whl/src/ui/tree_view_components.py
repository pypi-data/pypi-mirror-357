#!/usr/bin/env python3
"""
Tree View Components for Stockholm Dashboard

This module contains all tree view and timeline components that organize and display
hierarchical data structures. These components handle news articles, policy data,
and timeline visualizations in tree-like structures.

Extracted from textual_dashboard.py during modular refactoring.
"""

from typing import Dict, List

from rich.table import Table
from textual.widgets import Static, Tree


class NewsTreeView(Tree):
    """Interactive tree view for news articles organized by sentiment"""

    def __init__(self, **kwargs):
        super().__init__("📰 Recent News", **kwargs)
        self.show_root = False

    def update_news(
        self,
        news_data: List[Dict],
        sentiment_scores: List[float],
        sentiment_details: List[Dict],
    ):
        """Update tree with news data organized by sentiment, showing all analyzed articles with their tickers"""
        self.clear()

        # Create sentiment category nodes
        positive_node = self.root.add("🟢 Positive News", expand=True)
        neutral_node = self.root.add("🟡 Neutral News", expand=True)
        negative_node = self.root.add("🔴 Negative News", expand=True)

        # Process all analyzed articles (not just first 20)
        max_articles = min(
            len(news_data), len(sentiment_scores), len(sentiment_details)
        )
        combined_data = list(
            zip(
                news_data[:max_articles],
                sentiment_scores[:max_articles],
                sentiment_details[:max_articles],
            )
        )

        # Sort by publication date (newest first)
        combined_data.sort(key=lambda x: x[0].get("pub_timestamp", 0), reverse=True)

        for article, sentiment_score, sentiment_detail in combined_data:
            headline = article.get("headline", "No headline")
            time_ago = article.get("time_ago", "Unknown time")

            # Get mentioned tickers from sentiment analysis
            mentioned_tickers = sentiment_detail.get("mentioned_tickers", [])

            # Create ticker display string with sentiment colors
            if mentioned_tickers:
                # Show up to 3 tickers with their sentiment colors
                ticker_sentiments = sentiment_detail.get("ticker_sentiments", {})
                ticker_parts = []
                for ticker in mentioned_tickers[:3]:
                    if ticker in ticker_sentiments:
                        ticker_sentiment = ticker_sentiments[ticker].get(
                            "sentiment_score", 0
                        )
                        ticker_emoji = (
                            "🟢"
                            if ticker_sentiment > 0.1
                            else "🔴" if ticker_sentiment < -0.1 else "🟡"
                        )
                        ticker_parts.append(f"{ticker_emoji}{ticker}")
                    else:
                        # Fallback to neutral if no sentiment data
                        ticker_parts.append(f"🟡{ticker}")

                ticker_display = " ".join(ticker_parts)
                if len(mentioned_tickers) > 3:
                    ticker_display += f" +{len(mentioned_tickers)-3}"
            else:
                ticker_display = "📊 General Market"

            # Create node text with metadata
            node_text = f"[{time_ago}] {ticker_display}: {headline}"

            # Add to appropriate category based on sentiment
            if sentiment_score > 0.1:
                leaf = positive_node.add_leaf(node_text)
            elif sentiment_score < -0.1:
                leaf = negative_node.add_leaf(node_text)
            else:
                leaf = neutral_node.add_leaf(node_text)

            # Store article data for modal display
            leaf.data = {
                "article": article,
                "sentiment_score": sentiment_score,
                "sentiment_detail": sentiment_detail,
                "mentioned_tickers": mentioned_tickers,
            }

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection - update right panel with comprehensive article details"""
        if hasattr(event.node, "data") and event.node.data:
            article_data = event.node.data
            article = article_data["article"]
            sentiment_score = article_data["sentiment_score"]
            sentiment_detail = article_data["sentiment_detail"]
            mentioned_tickers = article_data["mentioned_tickers"]

            # Store the URL in the app for the 'o' key binding
            article_url = article.get("url", "")
            self.app.current_article_url = article_url

            # Create detailed article information
            headline = article.get("headline", "No headline")
            summary = article.get("summary", "No summary available")
            source = article.get("source", "Unknown source")
            time_ago = article.get("time_ago", "Unknown time")

            # Sentiment analysis details
            sentiment_category = sentiment_detail.get("sentiment_category", "Neutral")
            confidence = sentiment_detail.get("confidence", 0.0)

            # Create comprehensive details table
            table = Table()
            table.add_column("Field", style="bold cyan", width=20)
            table.add_column("Details", width=60)

            # Article metadata
            table.add_row("📰 Headline", headline)
            table.add_row("🕒 Published", time_ago)
            table.add_row("📡 Source", source)

            # Sentiment analysis
            sentiment_emoji = (
                "🟢"
                if sentiment_score > 0.1
                else "🔴" if sentiment_score < -0.1 else "🟡"
            )
            table.add_row(
                "📊 Sentiment",
                f"{sentiment_emoji} {sentiment_category} ({sentiment_score:+.3f})",
            )
            table.add_row("🎯 Confidence", f"{confidence:.1%}")

            # Mentioned tickers with individual sentiments
            if mentioned_tickers:
                ticker_sentiments = sentiment_detail.get("ticker_sentiments", {})
                ticker_details = []
                for ticker in mentioned_tickers:
                    if ticker in ticker_sentiments:
                        ticker_sentiment = ticker_sentiments[ticker].get(
                            "sentiment_score", 0
                        )
                        ticker_emoji = (
                            "🟢"
                            if ticker_sentiment > 0.1
                            else "🔴" if ticker_sentiment < -0.1 else "🟡"
                        )
                        ticker_details.append(
                            f"{ticker_emoji} {ticker} ({ticker_sentiment:+.2f})"
                        )
                    else:
                        ticker_details.append(f"⚪ {ticker}")
                table.add_row("🏢 Tickers", " | ".join(ticker_details))
            else:
                table.add_row("🏢 Tickers", "📊 General Market News")

            # Article summary
            table.add_row(
                "📝 Summary", summary[:200] + "..." if len(summary) > 200 else summary
            )

            # URL for reference
            if article_url:
                table.add_row("🔗 URL", f"Press 'o' to open: {article_url[:50]}...")

            # Update the details panel
            try:
                details_panel = self.app.query_one("#news-details", Static)
                details_panel.update(table)
            except Exception:
                # If details panel doesn't exist, show notification
                self.app.notify(f"Selected: {headline[:50]}...")


class PolicyTreeView(Tree):
    """Tree view for policy articles organized by sentiment, similar to NewsTreeView"""

    def __init__(self, **kwargs):
        super().__init__("🏛️ Policy Articles", **kwargs)
        self.border_title = "🏛️ Government Policy Articles"
        self.show_root = False

    def update_data(self, policy_analysis):
        """Update the tree with policy articles organized by sentiment"""
        # Clear existing tree
        self.clear()

        if not policy_analysis:
            return

        # Create sentiment category nodes
        positive_node = self.root.add("🟢 Positive Policy News", expand=True)
        neutral_node = self.root.add("🟡 Neutral Policy News", expand=True)
        negative_node = self.root.add("🔴 Negative Policy News", expand=True)

        # Get policy articles from different possible sources
        policy_articles = []

        # Check for high impact articles first
        if "high_impact_articles" in policy_analysis:
            policy_articles.extend(policy_analysis["high_impact_articles"])

        # Check for general articles
        if "articles" in policy_analysis:
            policy_articles.extend(policy_analysis["articles"])

        # Check for recent developments
        if "recent_developments" in policy_analysis:
            policy_articles.extend(policy_analysis["recent_developments"])

        # Check for policy categories
        if "policy_categories" in policy_analysis:
            for category_name, category_data in policy_analysis[
                "policy_categories"
            ].items():
                if "articles" in category_data:
                    # Add category info to articles
                    for article in category_data["articles"]:
                        article["category"] = category_name
                    policy_articles.extend(category_data["articles"])

        # Remove duplicates based on headline or URL
        seen_articles = set()
        unique_articles = []
        for article in policy_articles:
            identifier = article.get("headline", "") + article.get("url", "")
            if identifier not in seen_articles:
                seen_articles.add(identifier)
                unique_articles.append(article)

        # Sort by publication date (newest first)
        def get_datetime_for_sorting(article):
            """Parse datetime string to get timestamp for sorting"""
            try:
                datetime_str = article.get("datetime", "")
                if datetime_str:
                    from datetime import datetime
                    import re

                    # Remove any timezone suffix (CDT, CST, UTC, etc.)
                    dt_str = re.sub(r"\s+[A-Z]{3,4}$", "", datetime_str.strip())
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    return dt.timestamp()
                return 0
            except Exception:
                # Fallback: try to extract date from time_ago if datetime parsing fails
                try:
                    time_ago = article.get("time_ago", "")
                    if "days ago" in time_ago:
                        days = int(time_ago.split()[0])
                        return -days * 86400  # Negative for reverse sorting
                    elif "hours ago" in time_ago:
                        hours = int(time_ago.split()[0])
                        return -hours * 3600
                    elif "minutes ago" in time_ago:
                        minutes = int(time_ago.split()[0])
                        return -minutes * 60
                except Exception:
                    pass
                return 0

        unique_articles.sort(key=get_datetime_for_sorting, reverse=True)

        # Limit to reasonable number for performance
        unique_articles = unique_articles[:50]

        for article in unique_articles:
            headline = article.get(
                "headline", "No headline"
            )  # Full headline without truncation

            # Get sentiment score
            sentiment = article.get("sentiment", 0)
            time_ago = article.get("time_ago", "Unknown")
            category = article.get("category", "Policy")

            # Create node text with metadata
            node_text = f"[{time_ago}] {category}: {headline}"

            # Add to appropriate category based on sentiment
            if sentiment > 0.1:
                leaf = positive_node.add_leaf(node_text)
            elif sentiment < -0.1:
                leaf = negative_node.add_leaf(node_text)
            else:
                leaf = neutral_node.add_leaf(node_text)

            # Store article data for modal display
            leaf.data = {
                "article": article,
                "sentiment": sentiment,
                "category": category,
            }

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection - store URL for 'o' key and show notification"""
        if hasattr(event.node, "data") and event.node.data:
            article_data = event.node.data
            article_url = article_data["article"].get("url", "")
            headline = article_data["article"].get("headline", "No headline")

            # Store the URL in the app for the 'o' key binding (same as NewsTreeView)
            self.app.current_article_url = article_url

            # Show notification with article info
            sentiment = article_data["sentiment"]
            category = article_data["category"]
            sentiment_emoji = (
                "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
            )

            self.app.notify(
                f"{sentiment_emoji} {category}: {headline[:60]}... (Press 'o' to open)",
                timeout=3,
            )


class PolicyTimelinePanel(Static):
    """Panel showing policy timeline and trends"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "📈 Policy Sentiment Timeline"

    def update_data(self, policy_analysis):
        """Update the timeline panel with policy trend data"""
        if not policy_analysis:
            self.update("No policy data available")
            return

        # Create timeline table
        table = Table()
        table.add_column("Metric", style="bold cyan", width=20)
        table.add_column("Value", width=40)

        # Policy sentiment trend
        policy_sentiment = policy_analysis.get("policy_sentiment", {})
        avg_sentiment = policy_sentiment.get("average_sentiment", 0)
        sentiment_emoji = (
            "🟢" if avg_sentiment > 0.1 else "🔴" if avg_sentiment < -0.1 else "🟡"
        )

        table.add_row("📊 POLICY TRENDS", "")
        table.add_row("", f"{sentiment_emoji} Current Sentiment: {avg_sentiment:+.3f}")

        # Policy categories trend
        categories = policy_analysis.get("policy_categories", {})
        if categories:
            table.add_row("", "")
            table.add_row("🏛️ TOP CATEGORIES", "")

            # Sort categories by sentiment
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: x[1].get("average_sentiment", 0),
                reverse=True,
            )

            for i, (category, data) in enumerate(sorted_categories[:5], 1):
                count = data.get("count", 0)
                sentiment = data.get("average_sentiment", 0)
                emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                table.add_row(
                    "", f"{i}. {emoji} {category}: {count} articles ({sentiment:+.2f})"
                )

        # Recent developments
        recent_developments = policy_analysis.get("recent_developments", [])
        if recent_developments:
            table.add_row("", "")
            table.add_row("📰 RECENT ACTIVITY", "")
            for i, development in enumerate(recent_developments[:3], 1):
                title = development.get("title", "Unknown")[:30] + "..."
                sentiment = development.get("sentiment", 0)
                emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                table.add_row("", f"{i}. {emoji} {title}")

        # Market impact assessment
        impact_score = policy_analysis.get("market_impact_score", 0)
        if impact_score != 0:
            table.add_row("", "")
            table.add_row("💼 MARKET IMPACT", "")
            impact_text = self._get_impact_assessment(impact_score)
            impact_emoji = (
                "🟢" if impact_score > 0.05 else "🔴" if impact_score < -0.05 else "🟡"
            )
            table.add_row("", f"{impact_emoji} {impact_text} ({impact_score:+.3f})")

        self.update(table)

    def _get_impact_assessment(self, impact_score):
        """Get market impact assessment text"""
        if impact_score > 0.2:
            return "Strongly Positive"
        elif impact_score > 0.05:
            return "Moderately Positive"
        elif impact_score > -0.05:
            return "Neutral"
        elif impact_score > -0.2:
            return "Moderately Negative"
        else:
            return "Strongly Negative"
