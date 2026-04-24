"""
Intelligence Model — Leadership + Consumer Sentiment + Relationship Tracking

This module defines the data structures for:
1. Executive profiles and career timelines
2. Consumer sentiment collection (Reddit, Twitter, Glassdoor, etc.)
3. Influence relationships (how execs affect consumer/market sentiment)
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import DATE, TEXT, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from envestero.db.models import Base, TickerInfo


class Executive(Base):
    """Key company leaders and their career trajectory."""
    __tablename__ = "executives"
    __table_args__ = (
        UniqueConstraint("ticker_id", "name", "role", name="uq_exec_ticker_name_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Identity
    name: Mapped[str]
    role: Mapped[str]  # CEO, CTO, CFO, COO, President, etc.
    title: Mapped[Optional[str]]  # Full title: "Chief Executive Officer"

    # Career Timeline
    start_date: Mapped[date] = mapped_column(DATE)
    end_date: Mapped[Optional[date]] = mapped_column(DATE)  # NULL if current
    is_current: Mapped[bool] = mapped_column(default=True)

    # Background
    bio_summary: Mapped[Optional[str]] = mapped_column(TEXT)
    previous_roles: Mapped[Optional[str]]  # JSON: [{"company": "...", "role": "...", "years": "..."}]
    education: Mapped[Optional[str]]  # JSON: [{"institution": "...", "degree": "..."}]

    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )

    # Relationships
    ticker: Mapped[TickerInfo] = relationship(back_populates="executives")
    tenure_events: Mapped[list["ExecutiveEvent"]] = relationship(back_populates="executive")
    sentiment_impacts: Mapped[list["ExecutiveSentimentImpact"]] = relationship(
        back_populates="executive"
    )
    consumer_influences: Mapped[list["ExecutiveConsumerInfluence"]] = relationship(
        back_populates="executive"
    )


class ExecutiveEvent(Base):
    """Track executive joins, departures, promotions, retirements."""
    __tablename__ = "executive_events"
    __table_args__ = (
        UniqueConstraint("executive_id", "event_date", name="uq_exec_event_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Event Details
    event_type: Mapped[str]  # APPOINTED, RESIGNED, PROMOTED, RETIRED, REJOINED
    event_date: Mapped[date] = mapped_column(DATE)
    announcement_date: Mapped[Optional[date]] = mapped_column(DATE)

    # Role Transition
    role_previous: Mapped[Optional[str]]  # Prior role if promotion
    role_new: Mapped[str]  # Current role

    # Impact Assessment
    market_reaction_pct: Mapped[Optional[float]]  # Stock % change on announcement day
    sentiment_shift: Mapped[Optional[float]]  # News sentiment change (-1.0 to +1.0)
    investor_confidence: Mapped[Optional[str]]  # "positive", "negative", "neutral"

    # Context
    reason: Mapped[Optional[str]]  # Why they left (retirement, new opportunity, etc.)
    replacement: Mapped[Optional[str]]  # Name of successor
    notes: Mapped[Optional[str]] = mapped_column(TEXT)

    # Relationships
    executive: Mapped[Executive] = relationship(back_populates="tenure_events")
    ticker: Mapped[TickerInfo] = relationship()


class ExecutiveSentimentImpact(Base):
    """How individual executives correlate with news sentiment."""
    __tablename__ = "executive_sentiment_impact"
    __table_args__ = (
        UniqueConstraint(
            "executive_id", "period_start", "period_end", name="uq_exec_sentiment_period"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Time Period
    period_start: Mapped[date] = mapped_column(DATE)
    period_end: Mapped[date] = mapped_column(DATE)

    # Mention Analysis
    articles_mentioning: Mapped[int]  # How many articles mentioned this exec
    articles_total: Mapped[int]  # Total articles in period (for % calculation)

    # Sentiment When Mentioned
    sentiment_when_mentioned: Mapped[float]  # Avg sentiment in articles with exec
    sentiment_when_not_mentioned: Mapped[float]  # Baseline sentiment
    sentiment_difference: Mapped[float]  # How much exec affects sentiment

    # Influence Scoring
    influence_score: Mapped[float]  # 0-1, importance of this exec to sentiment
    correlation_coefficient: Mapped[Optional[float]]  # Pearson correlation

    # Keywords/Topics
    associated_keywords: Mapped[Optional[str]]  # JSON: ["innovation", "growth", "scandal"]
    associated_topics: Mapped[Optional[str]]  # JSON: ["product", "strategy", "leadership"]

    # Metadata
    computed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))

    executive: Mapped[Executive] = relationship(back_populates="sentiment_impacts")


class ConsumerSentiment(Base):
    """Track consumer/customer perception from social media, reviews, etc."""
    __tablename__ = "consumer_sentiment"
    __table_args__ = (
        UniqueConstraint("ticker_id", "date", "source", "category", name="uq_consumer_daily"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Time & Source
    date: Mapped[date] = mapped_column(DATE)
    source: Mapped[str]  # "reddit", "twitter", "glassdoor", "appstore", "trustpilot"

    # Sentiment
    sentiment_score: Mapped[float]  # -1.0 to +1.0
    sentiment_label: Mapped[str]  # "positive", "neutral", "negative"

    # Volume & Engagement
    mentions_count: Mapped[int]
    engagement_rate: Mapped[Optional[float]]  # Normalized 0-1 (likes, retweets, etc)
    avg_engagement_per_mention: Mapped[Optional[float]]

    # Category
    category: Mapped[str]
    # "product_quality", "customer_service", "price", "brand", "leadership",
    # "innovation", "sustainability", "diversity"

    # Sample Data
    sample_texts: Mapped[Optional[str]] = mapped_column(TEXT)  # JSON list of quotes
    top_keywords: Mapped[Optional[str]]  # JSON list of trending words

    # Metadata
    collected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))

    ticker: Mapped[TickerInfo] = relationship()


class ExecutiveConsumerInfluence(Base):
    """How leadership changes correlate with consumer sentiment shifts."""
    __tablename__ = "executive_consumer_influence"

    id: Mapped[int] = mapped_column(primary_key=True)
    executive_id: Mapped[int] = mapped_column(ForeignKey("executives.id"))
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Timeline
    period_start: Mapped[date] = mapped_column(DATE)  # Before executive change
    period_end: Mapped[date] = mapped_column(DATE)  # After executive change

    # Consumer Sentiment Shift
    consumer_sentiment_before: Mapped[float]
    consumer_sentiment_after: Mapped[float]
    sentiment_change_pct: Mapped[float]  # % change

    # Stock Price Movement
    price_change_pct: Mapped[float]
    correlation_to_consumer: Mapped[Optional[float]]  # Does price follow consumer sentiment?
    time_lag_days: Mapped[Optional[int]]  # Days between sentiment shift and price move

    # Analysis
    key_changes: Mapped[Optional[str]] = mapped_column(TEXT)  # JSON: ["product launched", ...]
    causality_confidence: Mapped[float]  # 0-1, how confident is the relationship
    notes: Mapped[Optional[str]] = mapped_column(TEXT)

    executive: Mapped[Executive] = relationship(back_populates="consumer_influences")


class InfluenceNetwork(Base):
    """Directional influence relationships between market entities."""
    __tablename__ = "influence_network"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("ticker_info.id"))

    # Source Entity
    source_type: Mapped[str]  # "executive", "event", "consumer_sentiment", "market_condition"
    source_id: Mapped[int]  # ID of the entity (executive_id, event_id, etc)
    source_description: Mapped[Optional[str]]

    # Target Entity
    target_type: Mapped[str]  # "consumer_sentiment", "news_sentiment", "stock_price", "employee_satisfaction"
    target_id: Mapped[Optional[int]]  # ID if applicable
    target_description: Mapped[Optional[str]]

    # Relationship Strength
    influence_strength: Mapped[float]  # 0-1, how strong the relationship
    direction: Mapped[str]  # "positive", "negative", "neutral"
    time_lag_days: Mapped[Optional[int]]  # Does X affect Y after N days?

    # Evidence
    sample_size: Mapped[int]  # How many data points support this?
    confidence: Mapped[float]  # 0-1, statistical confidence
    p_value: Mapped[Optional[float]]  # Statistical significance

    # Timeline
    observed_start: Mapped[date] = mapped_column(DATE)
    observed_end: Mapped[date] = mapped_column(DATE)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(TEXT)
    computed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))

    ticker: Mapped[TickerInfo] = relationship()
