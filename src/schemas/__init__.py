"""
Schemas Module

This package contains data schemas and models for API responses
and database structures.
"""

from .rentcast_schemas import (
    Property, PropertiesResponse, PropertyType, OwnerType, HistoryEventType,
    Address, HOADetails, PropertyFeatures, TaxAssessmentEntry, PropertyTaxEntry,
    PropertyHistoryEntry, PropertyOwner, Comparable, AVMValueResponse, AVMRentResponse,
    ListingAgent, ListingOffice, Builder, ListingHistoryEntry, PropertyListing,
    ListingsResponse, SaleStatistics, RentalStatistics, SaleDataByPropertyType,
    SaleDataByBedrooms, RentalDataByPropertyType, RentalDataByBedrooms,
    parse_property_response
)

__all__ = [
    'Property', 'PropertiesResponse', 'PropertyType', 'OwnerType', 'HistoryEventType',
    'Address', 'HOADetails', 'PropertyFeatures', 'TaxAssessmentEntry', 'PropertyTaxEntry',
    'PropertyHistoryEntry', 'PropertyOwner', 'Comparable', 'AVMValueResponse', 'AVMRentResponse',
    'ListingAgent', 'ListingOffice', 'Builder', 'ListingHistoryEntry', 'PropertyListing',
    'ListingsResponse', 'SaleStatistics', 'RentalStatistics', 'SaleDataByPropertyType',
    'SaleDataByBedrooms', 'RentalDataByPropertyType', 'RentalDataByBedrooms',
    'parse_property_response'
]
