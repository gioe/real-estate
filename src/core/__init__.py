"""
Core Module

This package contains the core business logic for the real estate analyzer,
including data analysis, fetching, database operations, and deal analysis pipeline.
"""

from .data_analyzer import RealEstateAnalyzer
from .data_fetcher import RealEstateDataFetcher, PaginationManager, APIResponse
from .database import DatabaseManager, PaginationParams, PaginatedResult
from .deal_analyzer import BasicDealAnalyzer, DealScore
from .deal_analysis_pipeline import DealAnalysisPipeline

__all__ = [
    # Core classes
    'RealEstateAnalyzer',
    'RealEstateDataFetcher',
    'DatabaseManager',
    
    # Deal Analysis Pipeline
    'BasicDealAnalyzer',
    'DealScore',
    'DealAnalysisPipeline',
    'RealEstateDataFetcher',
    'PaginationManager',
    'APIResponse',
    'DatabaseManager',
    'PaginationParams', 
    'PaginatedResult'
]
