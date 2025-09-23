from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.abstract_models import AbstractTimestampedModel
from accounts.models import UserModel


class UserActivity(AbstractTimestampedModel):
    """Track user activity and behavior patterns."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activities')
    
    # Activity details
    activity_type = models.CharField(_("Activity Type"), max_length=50, choices=[
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('order_created', _('Order Created')),
        ('order_viewed', _('Order Viewed')),
        ('bid_submitted', _('Bid Submitted')),
        ('chat_message', _('Chat Message')),
        ('payment_made', _('Payment Made')),
        ('profile_updated', _('Profile Updated')),
        ('search_performed', _('Search Performed')),
        ('service_viewed', _('Service Viewed')),
    ])
    
    # Context
    context_data = models.JSONField(_("Context Data"), default=dict)
    ip_address = models.GenericIPAddressField(_("IP Address"), null=True, blank=True)
    user_agent = models.TextField(_("User Agent"), blank=True)
    session_id = models.CharField(_("Session ID"), max_length=100, blank=True)
    
    # Related objects
    related_object_type = models.CharField(_("Related Object Type"), max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(_("Related Object ID"), null=True, blank=True)
    
    # Performance
    response_time = models.FloatField(_("Response Time (seconds)"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("User Activity")
        verbose_name_plural = _("User Activities")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}... [#{self.id}]"


class OrderAnalytics(AbstractTimestampedModel):
    """Analytics data for orders and services."""
    date = models.DateField(_("Date"), unique=True)
    
    # Order counts
    total_orders = models.PositiveIntegerField(_("Total Orders"), default=0)
    new_orders = models.PositiveIntegerField(_("New Orders"), default=0)
    completed_orders = models.PositiveIntegerField(_("Completed Orders"), default=0)
    cancelled_orders = models.PositiveIntegerField(_("Cancelled Orders"), default=0)
    
    # Financial metrics
    total_revenue = models.DecimalField(_("Total Revenue"), max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(_("Average Order Value"), max_digits=10, decimal_places=2, default=0)
    total_fees = models.DecimalField(_("Total Fees"), max_digits=10, decimal_places=2, default=0)
    
    # Service metrics
    total_bids = models.PositiveIntegerField(_("Total Bids"), default=0)
    average_bids_per_order = models.DecimalField(_("Average Bids per Order"), max_digits=5, decimal_places=2, default=0)
    
    # User metrics
    active_clients = models.PositiveIntegerField(_("Active Clients"), default=0)
    active_providers = models.PositiveIntegerField(_("Active Providers"), default=0)
    new_users = models.PositiveIntegerField(_("New Users"), default=0)
    
    class Meta:
        verbose_name = _("Order Analytics")
        verbose_name_plural = _("Order Analytics")
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}... [#{self.id}]"


class ServiceCategoryAnalytics(AbstractTimestampedModel):
    """Analytics for service categories."""
    date = models.DateField(_("Date"))
    category = models.ForeignKey('core.ServiceCategory', on_delete=models.CASCADE, related_name='analytics')
    
    # Metrics
    order_count = models.PositiveIntegerField(_("Order Count"), default=0)
    total_revenue = models.DecimalField(_("Total Revenue"), max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(_("Average Order Value"), max_digits=10, decimal_places=2, default=0)
    bid_count = models.PositiveIntegerField(_("Bid Count"), default=0)
    completion_rate = models.DecimalField(_("Completion Rate (%)"), max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _("Service Category Analytics")
        verbose_name_plural = _("Service Category Analytics")
        ordering = ['-date', 'category']
        unique_together = ['date', 'category']
        indexes = [
            models.Index(fields=['category', 'date']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.date}... [#{self.id}]"


class UserRetentionAnalytics(AbstractTimestampedModel):
    """User retention and engagement analytics."""
    date = models.DateField(_("Date"))
    user_type = models.CharField(_("User Type"), max_length=20, choices=[
        ('client', _('Client')),
        ('service_provider', _('Service Provider')),
    ])
    
    # Cohort metrics
    cohort_size = models.PositiveIntegerField(_("Cohort Size"), default=0)
    day_1_retention = models.DecimalField(_("Day 1 Retention (%)"), max_digits=5, decimal_places=2, default=0)
    day_7_retention = models.DecimalField(_("Day 7 Retention (%)"), max_digits=5, decimal_places=2, default=0)
    day_30_retention = models.DecimalField(_("Day 30 Retention (%)"), max_digits=5, decimal_places=2, default=0)
    
    # Engagement metrics
    average_sessions_per_user = models.DecimalField(_("Average Sessions per User"), max_digits=5, decimal_places=2, default=0)
    average_session_duration = models.FloatField(_("Average Session Duration (minutes)"), default=0)
    
    class Meta:
        verbose_name = _("User Retention Analytics")
        verbose_name_plural = _("User Retention Analytics")
        ordering = ['-date', 'user_type']
        unique_together = ['date', 'user_type']
    
    def __str__(self):
        return f"{self.get_user_type_display()} Retention - {self.date}... [#{self.id}]"


class SearchAnalytics(AbstractTimestampedModel):
    """Analytics for search functionality."""
    date = models.DateField(_("Date"))
    
    # Search metrics
    total_searches = models.PositiveIntegerField(_("Total Searches"), default=0)
    unique_searchers = models.PositiveIntegerField(_("Unique Searchers"), default=0)
    searches_with_results = models.PositiveIntegerField(_("Searches with Results"), default=0)
    searches_without_results = models.PositiveIntegerField(_("Searches without Results"), default=0)
    
    # Popular search terms
    top_search_terms = models.JSONField(_("Top Search Terms"), default=list)
    top_categories_searched = models.JSONField(_("Top Categories Searched"), default=list)
    
    # Conversion metrics
    searches_leading_to_orders = models.PositiveIntegerField(_("Searches Leading to Orders"), default=0)
    search_to_order_conversion_rate = models.DecimalField(_("Search to Order Conversion Rate (%)"), max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _("Search Analytics")
        verbose_name_plural = _("Search Analytics")
        ordering = ['-date']
    
    def __str__(self):
        return f"Search Analytics for {self.date}... [#{self.id}]"


class PerformanceMetrics(AbstractTimestampedModel):
    """System performance and technical metrics."""
    date = models.DateField(_("Date"))
    time_period = models.CharField(_("Time Period"), max_length=20, choices=[
        ('hourly', _('Hourly')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ], default='daily')
    
    # Performance metrics
    average_response_time = models.FloatField(_("Average Response Time (ms)"), default=0)
    max_response_time = models.FloatField(_("Max Response Time (ms)"), default=0)
    min_response_time = models.FloatField(_("Min Response Time (ms)"), default=0)
    
    # Error metrics
    total_errors = models.PositiveIntegerField(_("Total Errors"), default=0)
    error_rate = models.DecimalField(_("Error Rate (%)"), max_digits=5, decimal_places=2, default=0)
    
    # System metrics
    active_users = models.PositiveIntegerField(_("Active Users"), default=0)
    concurrent_users = models.PositiveIntegerField(_("Concurrent Users"), default=0)
    database_queries = models.PositiveIntegerField(_("Database Queries"), default=0)
    
    # Infrastructure
    cpu_usage = models.DecimalField(_("CPU Usage (%)"), max_digits=5, decimal_places=2, default=0)
    memory_usage = models.DecimalField(_("Memory Usage (%)"), max_digits=5, decimal_places=2, default=0)
    disk_usage = models.DecimalField(_("Disk Usage (%)"), max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _("Performance Metrics")
        verbose_name_plural = _("Performance Metrics")
        ordering = ['-date', 'time_period']
        unique_together = ['date', 'time_period']
    
    def __str__(self):
        return f"Performance Metrics - {self.date} ({self.get_time_period_display()})... [#{self.id}]"


class BusinessMetrics(AbstractTimestampedModel):
    """Key business performance indicators."""
    date = models.DateField(_("Date"))
    
    # Financial KPIs
    gross_merchandise_volume = models.DecimalField(_("Gross Merchandise Volume"), max_digits=12, decimal_places=2, default=0)
    net_revenue = models.DecimalField(_("Net Revenue"), max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField(_("Profit Margin (%)"), max_digits=5, decimal_places=2, default=0)
    
    # Operational KPIs
    order_fulfillment_rate = models.DecimalField(_("Order Fulfillment Rate (%)"), max_digits=5, decimal_places=2, default=0)
    average_order_processing_time = models.FloatField(_("Average Order Processing Time (hours)"), default=0)
    customer_satisfaction_score = models.DecimalField(_("Customer Satisfaction Score"), max_digits=3, decimal_places=2, default=0)
    
    # Growth metrics
    month_over_month_growth = models.DecimalField(_("Month over Month Growth (%)"), max_digits=6, decimal_places=2, default=0)
    year_over_year_growth = models.DecimalField(_("Year over Year Growth (%)"), max_digits=6, decimal_places=2, default=0)
    
    # Market metrics
    market_share = models.DecimalField(_("Market Share (%)"), max_digits=5, decimal_places=2, default=0)
    competitive_position = models.CharField(_("Competitive Position"), max_length=20, choices=[
        ('leader', _('Market Leader')),
        ('challenger', _('Market Challenger')),
        ('follower', _('Market Follower')),
        ('niche', _('Niche Player')),
    ], blank=True)
    
    class Meta:
        verbose_name = _("Business Metrics")
        verbose_name_plural = _("Business Metrics")
        ordering = ['-date']
    
    def __str__(self):
        return f"Business Metrics for {self.date}... [#{self.id}]"
