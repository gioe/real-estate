"""
RentCast API Response Schemas

This module contains dataclasses and type definitions for all RentCast API responses.
All schemas are based on the official RentCast API documentation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json


class PropertyType(Enum):
    """Property type enumeration."""
    SINGLE_FAMILY = "Single Family"
    CONDO = "Condo"
    TOWNHOUSE = "Townhouse"
    MULTI_FAMILY = "Multi Family"
    APARTMENT = "Apartment"
    MOBILE_HOME = "Mobile Home"
    MANUFACTURED = "Manufactured"
    LAND = "Land"
    COMMERCIAL = "Commercial"
    OTHER = "Other"


class OwnerType(Enum):
    """Property owner type enumeration."""
    INDIVIDUAL = "Individual"
    ORGANIZATION = "Organization"


class HistoryEventType(Enum):
    """Property history event type enumeration."""
    SALE = "Sale"


@dataclass
class Address:
    """Address information for properties or mailing addresses."""
    id: Optional[str] = None
    formatted_address: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create Address from dictionary."""
        return cls(
            id=data.get('id'),
            formatted_address=data.get('formattedAddress'),
            address_line1=data.get('addressLine1'),
            address_line2=data.get('addressLine2'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zipCode')
        )


@dataclass
@dataclass
class HOADetails:
    """Homeowner's Association details."""
    fee: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HOADetails':
        """Create HOADetails from dictionary."""
        return cls(
            fee=data.get('fee')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert HOADetails to dictionary format."""
        return {
            'fee': self.fee
        }


@dataclass
class PropertyFeatures:
    """Property features and characteristics."""
    architecture_type: Optional[str] = None
    cooling: Optional[bool] = None
    cooling_type: Optional[str] = None
    exterior_type: Optional[str] = None
    fireplace: Optional[bool] = None
    fireplace_type: Optional[str] = None
    floor_count: Optional[int] = None
    foundation_type: Optional[str] = None
    garage: Optional[bool] = None
    garage_spaces: Optional[int] = None
    garage_type: Optional[str] = None
    heating: Optional[bool] = None
    heating_type: Optional[str] = None
    pool: Optional[bool] = None
    pool_type: Optional[str] = None
    roof_type: Optional[str] = None
    room_count: Optional[int] = None
    unit_count: Optional[int] = None
    view_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyFeatures':
        """Create PropertyFeatures from dictionary."""
        return cls(
            architecture_type=data.get('architectureType'),
            cooling=data.get('cooling'),
            cooling_type=data.get('coolingType'),
            exterior_type=data.get('exteriorType'),
            fireplace=data.get('fireplace'),
            fireplace_type=data.get('fireplaceType'),
            floor_count=data.get('floorCount'),
            foundation_type=data.get('foundationType'),
            garage=data.get('garage'),
            garage_spaces=data.get('garageSpaces'),
            garage_type=data.get('garageType'),
            heating=data.get('heating'),
            heating_type=data.get('heatingType'),
            pool=data.get('pool'),
            pool_type=data.get('poolType'),
            roof_type=data.get('roofType'),
            room_count=data.get('roomCount'),
            unit_count=data.get('unitCount'),
            view_type=data.get('viewType')
        )


@dataclass
class TaxAssessmentEntry:
    """Tax assessment entry for a specific year."""
    year: int
    value: Optional[float] = None
    land: Optional[float] = None
    improvements: Optional[float] = None
    
    @classmethod
    def from_dict(cls, year: int, data: Dict[str, Any]) -> 'TaxAssessmentEntry':
        """Create TaxAssessmentEntry from dictionary."""
        return cls(
            year=year,
            value=data.get('value'),
            land=data.get('land'),
            improvements=data.get('improvements')
        )


@dataclass
class PropertyTaxEntry:
    """Property tax entry for a specific year."""
    year: int
    total: Optional[float] = None
    
    @classmethod
    def from_dict(cls, year: int, data: Dict[str, Any]) -> 'PropertyTaxEntry':
        """Create PropertyTaxEntry from dictionary."""
        return cls(
            year=year,
            total=data.get('total')
        )


@dataclass
class PropertyHistoryEntry:
    """Property sale history entry."""
    date: str
    event: str = "Sale"  # Currently only "Sale" is supported
    price: Optional[float] = None
    
    @classmethod
    def from_dict(cls, date_key: str, data: Dict[str, Any]) -> 'PropertyHistoryEntry':
        """Create PropertyHistoryEntry from dictionary."""
        return cls(
            date=date_key,
            event=data.get('event', 'Sale'),
            price=data.get('price')
        )


@dataclass
class PropertyOwner:
    """Property owner information."""
    names: Optional[List[str]] = None
    type: Optional[str] = None
    mailing_address: Optional[Address] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyOwner':
        """Create PropertyOwner from dictionary."""
        mailing_address_data = data.get('mailingAddress')
        mailing_address = Address.from_dict(mailing_address_data) if mailing_address_data else None
        
        return cls(
            names=data.get('names'),
            type=data.get('type'),
            mailing_address=mailing_address
        )


@dataclass
class Property:
    """
    Complete property record from RentCast API.
    
    This dataclass represents all fields that can be returned from the RentCast
    properties endpoints (/properties, /properties/random, /properties/{id}).
    """
    
    # Basic property information
    id: Optional[str] = None
    formatted_address: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    
    # Location coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Property characteristics
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_footage: Optional[int] = None
    lot_size: Optional[int] = None
    year_built: Optional[int] = None
    
    # Property identifiers and legal info
    assessor_id: Optional[str] = None
    legal_description: Optional[str] = None
    subdivision: Optional[str] = None
    zoning: Optional[str] = None
    
    # Sale information
    last_sale_date: Optional[str] = None
    last_sale_price: Optional[float] = None
    
    # Complex nested objects
    hoa: Optional[HOADetails] = None
    features: Optional[PropertyFeatures] = None
    tax_assessments: Dict[str, TaxAssessmentEntry] = field(default_factory=dict)
    property_taxes: Dict[str, PropertyTaxEntry] = field(default_factory=dict)
    history: Dict[str, PropertyHistoryEntry] = field(default_factory=dict)
    owner: Optional[PropertyOwner] = None
    
    # Owner occupancy status
    owner_occupied: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Property':
        """
        Create Property from dictionary (API response).
        
        Args:
            data: Dictionary containing property data from API
            
        Returns:
            Property instance
        """
        # Parse HOA details
        hoa_data = data.get('hoa')
        hoa = HOADetails.from_dict(hoa_data) if hoa_data else None
        
        # Parse features
        features_data = data.get('features')
        features = PropertyFeatures.from_dict(features_data) if features_data else None
        
        # Parse tax assessments
        tax_assessments = {}
        tax_assessments_data = data.get('taxAssessments', {})
        for year_str, assessment_data in tax_assessments_data.items():
            try:
                year = int(year_str)
                tax_assessments[year_str] = TaxAssessmentEntry.from_dict(year, assessment_data)
            except (ValueError, TypeError):
                continue
        
        # Parse property taxes
        property_taxes = {}
        property_taxes_data = data.get('propertyTaxes', {})
        for year_str, tax_data in property_taxes_data.items():
            try:
                year = int(year_str)
                property_taxes[year_str] = PropertyTaxEntry.from_dict(year, tax_data)
            except (ValueError, TypeError):
                continue
        
        # Parse history
        history = {}
        history_data = data.get('history', {})
        for date_key, history_entry in history_data.items():
            history[date_key] = PropertyHistoryEntry.from_dict(date_key, history_entry)
        
        # Parse owner
        owner_data = data.get('owner')
        owner = PropertyOwner.from_dict(owner_data) if owner_data else None
        
        return cls(
            id=data.get('id'),
            formatted_address=data.get('formattedAddress'),
            address_line1=data.get('addressLine1'),
            address_line2=data.get('addressLine2'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zipCode'),
            county=data.get('county'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            property_type=data.get('propertyType'),
            bedrooms=data.get('bedrooms'),
            bathrooms=data.get('bathrooms'),
            square_footage=data.get('squareFootage'),
            lot_size=data.get('lotSize'),
            year_built=data.get('yearBuilt'),
            assessor_id=data.get('assessorID'),
            legal_description=data.get('legalDescription'),
            subdivision=data.get('subdivision'),
            zoning=data.get('zoning'),
            last_sale_date=data.get('lastSaleDate'),
            last_sale_price=data.get('lastSalePrice'),
            hoa=hoa,
            features=features,
            tax_assessments=tax_assessments,
            property_taxes=property_taxes,
            history=history,
            owner=owner,
            owner_occupied=data.get('ownerOccupied')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Property to dictionary format (for API requests or serialization).
        
        Returns:
            Dictionary representation of the property
        """
        result = {
            'id': self.id,
            'formattedAddress': self.formatted_address,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'county': self.county,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'propertyType': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'lotSize': self.lot_size,
            'yearBuilt': self.year_built,
            'assessorID': self.assessor_id,
            'legalDescription': self.legal_description,
            'subdivision': self.subdivision,
            'zoning': self.zoning,
            'lastSaleDate': self.last_sale_date,
            'lastSalePrice': self.last_sale_price,
            'ownerOccupied': self.owner_occupied
        }
        
        # Add HOA details if present
        if self.hoa:
            result['hoa'] = {'fee': self.hoa.fee}
        
        # Add features if present
        if self.features:
            result['features'] = {
                'architectureType': self.features.architecture_type,
                'cooling': self.features.cooling,
                'coolingType': self.features.cooling_type,
                'exteriorType': self.features.exterior_type,
                'fireplace': self.features.fireplace,
                'fireplaceType': self.features.fireplace_type,
                'floorCount': self.features.floor_count,
                'foundationType': self.features.foundation_type,
                'garage': self.features.garage,
                'garageSpaces': self.features.garage_spaces,
                'garageType': self.features.garage_type,
                'heating': self.features.heating,
                'heatingType': self.features.heating_type,
                'pool': self.features.pool,
                'poolType': self.features.pool_type,
                'roofType': self.features.roof_type,
                'roomCount': self.features.room_count,
                'unitCount': self.features.unit_count,
                'viewType': self.features.view_type
            }
        
        # Add tax assessments
        if self.tax_assessments:
            result['taxAssessments'] = {}
            for year_str, assessment in self.tax_assessments.items():
                result['taxAssessments'][year_str] = {
                    'year': assessment.year,
                    'value': assessment.value,
                    'land': assessment.land,
                    'improvements': assessment.improvements
                }
        
        # Add property taxes
        if self.property_taxes:
            result['propertyTaxes'] = {}
            for year_str, tax_entry in self.property_taxes.items():
                result['propertyTaxes'][year_str] = {
                    'year': tax_entry.year,
                    'total': tax_entry.total
                }
        
        # Add history
        if self.history:
            result['history'] = {}
            for date_key, history_entry in self.history.items():
                result['history'][date_key] = {
                    'event': history_entry.event,
                    'date': history_entry.date,
                    'price': history_entry.price
                }
        
        # Add owner information
        if self.owner:
            result['owner'] = {
                'names': self.owner.names,
                'type': self.owner.type
            }
            if self.owner.mailing_address:
                result['owner']['mailingAddress'] = {
                    'id': self.owner.mailing_address.id,
                    'formattedAddress': self.owner.mailing_address.formatted_address,
                    'addressLine1': self.owner.mailing_address.address_line1,
                    'addressLine2': self.owner.mailing_address.address_line2,
                    'city': self.owner.mailing_address.city,
                    'state': self.owner.mailing_address.state,
                    'zipCode': self.owner.mailing_address.zip_code
                }
        
        # Remove None values to clean up the result
        return {k: v for k, v in result.items() if v is not None}
    
    def __str__(self) -> str:
        """String representation of the property."""
        return f"Property(id='{self.id}', address='{self.formatted_address}', type='{self.property_type}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the property."""
        return (f"Property(id='{self.id}', formatted_address='{self.formatted_address}', "
                f"property_type='{self.property_type}', bedrooms={self.bedrooms}, "
                f"bathrooms={self.bathrooms}, square_footage={self.square_footage})")


@dataclass
class PropertiesResponse:
    """
    Response wrapper for properties endpoints that return multiple properties.
    
    This handles responses from:
    - GET /properties
    - GET /properties/random
    """
    
    properties: List[Property] = field(default_factory=list)
    total_count: Optional[int] = None
    has_more: Optional[bool] = None
    next_offset: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertiesResponse':
        """
        Create PropertiesResponse from API response dictionary.
        
        Args:
            data: Dictionary containing API response
            
        Returns:
            PropertiesResponse instance
        """
        properties = []
        
        # Handle different response formats
        if 'properties' in data:
            # Standard properties list response
            properties_data = data.get('properties', [])
            if isinstance(properties_data, list):
                for prop_data in properties_data:
                    if isinstance(prop_data, dict):
                        properties.append(Property.from_dict(prop_data))
        elif isinstance(data, list):
            # Direct list of properties
            for prop_data in data:
                if isinstance(prop_data, dict):
                    properties.append(Property.from_dict(prop_data))
        elif isinstance(data, dict) and 'id' in data:
            # Single property response (like /properties/{id})
            properties.append(Property.from_dict(data))
        
        return cls(
            properties=properties,
            total_count=data.get('totalCount') if isinstance(data, dict) else None,
            has_more=data.get('hasMore') if isinstance(data, dict) else None,
            next_offset=data.get('nextOffset') if isinstance(data, dict) else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result: Dict[str, Any] = {
            'properties': [prop.to_dict() for prop in self.properties]
        }
        
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        if self.has_more is not None:
            result['hasMore'] = self.has_more
        if self.next_offset is not None:
            result['nextOffset'] = self.next_offset
        
        return result


# Utility functions for working with property data

def parse_property_response(response_data: Dict[str, Any]) -> Union[Property, PropertiesResponse]:
    """
    Parse a property response from the API, automatically detecting if it's a single 
    property or a list of properties.
    
    Args:
        response_data: Raw API response data
        
    Returns:
        Either a single Property or PropertiesResponse with multiple properties
    """
    if 'id' in response_data and 'formattedAddress' in response_data:
        # Single property response
        return Property.from_dict(response_data)
    else:
        # Multiple properties response
        return PropertiesResponse.from_dict(response_data)


class ListingType(Enum):
    """Listing type enumeration for property listings."""
    STANDARD = "Standard"
    NEW_CONSTRUCTION = "New Construction"
    FORECLOSURE = "Foreclosure"
    SHORT_SALE = "Short Sale"
    AUCTION = "Auction"
    REO = "REO"


class ListingStatus(Enum):
    """Listing status enumeration."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ListingEventType(Enum):
    """Listing history event type enumeration."""
    SALE_LISTING = "Sale Listing"
    RENTAL_LISTING = "Rental Listing"


@dataclass
class Comparable:
    """
    Comparable property information used in AVM calculations.
    
    This dataclass represents comparable properties returned by the 
    /avm/value and /avm/rent/long-term endpoints.
    """
    
    # Property identifiers
    id: Optional[str] = None
    formatted_address: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    
    # Location coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Property characteristics
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_footage: Optional[int] = None
    lot_size: Optional[int] = None
    year_built: Optional[int] = None
    
    # Listing information
    price: Optional[float] = None
    listing_type: Optional[str] = None
    listed_date: Optional[str] = None
    removed_date: Optional[str] = None
    last_seen_date: Optional[str] = None
    days_on_market: Optional[int] = None
    
    # Comparison metrics
    distance: Optional[float] = None
    days_old: Optional[int] = None
    correlation: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comparable':
        """Create Comparable from dictionary."""
        return cls(
            id=data.get('id'),
            formatted_address=data.get('formattedAddress'),
            address_line1=data.get('addressLine1'),
            address_line2=data.get('addressLine2'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zipCode'),
            county=data.get('county'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            property_type=data.get('propertyType'),
            bedrooms=data.get('bedrooms'),
            bathrooms=data.get('bathrooms'),
            square_footage=data.get('squareFootage'),
            lot_size=data.get('lotSize'),
            year_built=data.get('yearBuilt'),
            price=data.get('price'),
            listing_type=data.get('listingType'),
            listed_date=data.get('listedDate'),
            removed_date=data.get('removedDate'),
            last_seen_date=data.get('lastSeenDate'),
            days_on_market=data.get('daysOnMarket'),
            distance=data.get('distance'),
            days_old=data.get('daysOld'),
            correlation=data.get('correlation')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Comparable to dictionary format."""
        return {
            'id': self.id,
            'formattedAddress': self.formatted_address,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'county': self.county,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'propertyType': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'lotSize': self.lot_size,
            'yearBuilt': self.year_built,
            'price': self.price,
            'listingType': self.listing_type,
            'listedDate': self.listed_date,
            'removedDate': self.removed_date,
            'lastSeenDate': self.last_seen_date,
            'daysOnMarket': self.days_on_market,
            'distance': self.distance,
            'daysOld': self.days_old,
            'correlation': self.correlation
        }


@dataclass
class AVMValueResponse:
    """
    Response schema for the /avm/value endpoint.
    
    This dataclass represents the response from the RentCast automated 
    valuation model (AVM) for property value estimates.
    """
    
    # Value estimate information
    price: Optional[float] = None
    price_range_low: Optional[float] = None
    price_range_high: Optional[float] = None
    
    # Subject property location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Comparable properties used in valuation
    comparables: List[Comparable] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AVMValueResponse':
        """Create AVMValueResponse from dictionary."""
        comparables = []
        if data.get('comparables'):
            comparables = [Comparable.from_dict(comp) for comp in data['comparables']]
        
        return cls(
            price=data.get('price'),
            price_range_low=data.get('priceRangeLow'),
            price_range_high=data.get('priceRangeHigh'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            comparables=comparables
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AVMValueResponse to dictionary format."""
        return {
            'price': self.price,
            'priceRangeLow': self.price_range_low,
            'priceRangeHigh': self.price_range_high,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'comparables': [comp.to_dict() for comp in self.comparables]
        }


@dataclass
class AVMRentResponse:
    """
    Response schema for the /avm/rent/long-term endpoint.
    
    This dataclass represents the response from the RentCast automated 
    valuation model (AVM) for property rent estimates.
    """
    
    # Rent estimate information
    rent: Optional[float] = None
    rent_range_low: Optional[float] = None
    rent_range_high: Optional[float] = None
    
    # Subject property location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Comparable properties used in valuation
    comparables: List[Comparable] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AVMRentResponse':
        """Create AVMRentResponse from dictionary."""
        comparables = []
        if data.get('comparables'):
            comparables = [Comparable.from_dict(comp) for comp in data['comparables']]
        
        return cls(
            rent=data.get('rent'),
            rent_range_low=data.get('rentRangeLow'),
            rent_range_high=data.get('rentRangeHigh'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            comparables=comparables
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AVMRentResponse to dictionary format."""
        return {
            'rent': self.rent,
            'rentRangeLow': self.rent_range_low,
            'rentRangeHigh': self.rent_range_high,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'comparables': [comp.to_dict() for comp in self.comparables]
        }


@dataclass
class ListingAgent:
    """
    Listing agent information for property listings.
    
    Contains contact details for the agent representing the seller.
    """
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListingAgent':
        """Create ListingAgent from dictionary."""
        return cls(
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ListingAgent to dictionary format."""
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'website': self.website
        }


@dataclass
class ListingOffice:
    """
    Listing office information for property listings.
    
    Contains contact details for the office/broker representing the seller.
    """
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListingOffice':
        """Create ListingOffice from dictionary."""
        return cls(
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ListingOffice to dictionary format."""
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'website': self.website
        }


@dataclass
class Builder:
    """
    Builder information for new construction listings.
    
    Contains details about the property builder and development.
    """
    name: Optional[str] = None
    development: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Builder':
        """Create Builder from dictionary."""
        return cls(
            name=data.get('name'),
            development=data.get('development'),
            phone=data.get('phone'),
            website=data.get('website')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Builder to dictionary format."""
        return {
            'name': self.name,
            'development': self.development,
            'phone': self.phone,
            'website': self.website
        }


@dataclass
class ListingHistoryEntry:
    """
    Historical listing entry for a specific date.
    
    Contains information about past listing events and price changes.
    """
    date: str
    event: Optional[str] = None
    price: Optional[float] = None
    listing_type: Optional[str] = None
    listed_date: Optional[str] = None
    removed_date: Optional[str] = None
    days_on_market: Optional[int] = None
    
    @classmethod
    def from_dict(cls, date_key: str, data: Dict[str, Any]) -> 'ListingHistoryEntry':
        """Create ListingHistoryEntry from dictionary."""
        return cls(
            date=date_key,
            event=data.get('event'),
            price=data.get('price'),
            listing_type=data.get('listingType'),
            listed_date=data.get('listedDate'),
            removed_date=data.get('removedDate'),
            days_on_market=data.get('daysOnMarket')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ListingHistoryEntry to dictionary format."""
        return {
            'event': self.event,
            'price': self.price,
            'listingType': self.listing_type,
            'listedDate': self.listed_date,
            'removedDate': self.removed_date,
            'daysOnMarket': self.days_on_market
        }


@dataclass
class PropertyListing:
    """
    Property listing from the /listings endpoint.
    
    This dataclass represents both sale and rental listings with all
    available fields from the RentCast listings API.
    """
    
    # Basic property information
    id: Optional[str] = None
    formatted_address: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    
    # Location coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Property characteristics
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_footage: Optional[int] = None
    lot_size: Optional[int] = None
    year_built: Optional[int] = None
    
    # HOA information
    hoa: Optional[HOADetails] = None
    
    # Listing information
    status: Optional[str] = None
    price: Optional[float] = None
    listing_type: Optional[str] = None
    listed_date: Optional[str] = None
    removed_date: Optional[str] = None
    created_date: Optional[str] = None
    last_seen_date: Optional[str] = None
    days_on_market: Optional[int] = None
    
    # MLS information
    mls_name: Optional[str] = None
    mls_number: Optional[str] = None
    
    # Agent and office information
    listing_agent: Optional[ListingAgent] = None
    listing_office: Optional[ListingOffice] = None
    
    # Builder information (for new construction)
    builder: Optional[Builder] = None
    
    # Listing history
    history: Dict[str, ListingHistoryEntry] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyListing':
        """Create PropertyListing from dictionary."""
        # Parse HOA details
        hoa_data = data.get('hoa')
        hoa = HOADetails.from_dict(hoa_data) if hoa_data else None
        
        # Parse listing agent
        agent_data = data.get('listingAgent')
        listing_agent = ListingAgent.from_dict(agent_data) if agent_data else None
        
        # Parse listing office
        office_data = data.get('listingOffice')
        listing_office = ListingOffice.from_dict(office_data) if office_data else None
        
        # Parse builder
        builder_data = data.get('builder')
        builder = Builder.from_dict(builder_data) if builder_data else None
        
        # Parse history
        history = {}
        history_data = data.get('history', {})
        for date_key, history_entry_data in history_data.items():
            history[date_key] = ListingHistoryEntry.from_dict(date_key, history_entry_data)
        
        return cls(
            id=data.get('id'),
            formatted_address=data.get('formattedAddress'),
            address_line1=data.get('addressLine1'),
            address_line2=data.get('addressLine2'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zipCode'),
            county=data.get('county'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            property_type=data.get('propertyType'),
            bedrooms=data.get('bedrooms'),
            bathrooms=data.get('bathrooms'),
            square_footage=data.get('squareFootage'),
            lot_size=data.get('lotSize'),
            year_built=data.get('yearBuilt'),
            hoa=hoa,
            status=data.get('status'),
            price=data.get('price'),
            listing_type=data.get('listingType'),
            listed_date=data.get('listedDate'),
            removed_date=data.get('removedDate'),
            created_date=data.get('createdDate'),
            last_seen_date=data.get('lastSeenDate'),
            days_on_market=data.get('daysOnMarket'),
            mls_name=data.get('mlsName'),
            mls_number=data.get('mlsNumber'),
            listing_agent=listing_agent,
            listing_office=listing_office,
            builder=builder,
            history=history
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PropertyListing to dictionary format."""
        result = {
            'id': self.id,
            'formattedAddress': self.formatted_address,
            'addressLine1': self.address_line1,
            'addressLine2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'county': self.county,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'propertyType': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'lotSize': self.lot_size,
            'yearBuilt': self.year_built,
            'status': self.status,
            'price': self.price,
            'listingType': self.listing_type,
            'listedDate': self.listed_date,
            'removedDate': self.removed_date,
            'createdDate': self.created_date,
            'lastSeenDate': self.last_seen_date,
            'daysOnMarket': self.days_on_market,
            'mlsName': self.mls_name,
            'mlsNumber': self.mls_number
        }
        
        # Add HOA details if present
        if self.hoa:
            result['hoa'] = self.hoa.to_dict()
        
        # Add agent information if present
        if self.listing_agent:
            result['listingAgent'] = self.listing_agent.to_dict()
        
        # Add office information if present
        if self.listing_office:
            result['listingOffice'] = self.listing_office.to_dict()
        
        # Add builder information if present
        if self.builder:
            result['builder'] = self.builder.to_dict()
        
        # Add history
        if self.history:
            result['history'] = {}
            for date_key, history_entry in self.history.items():
                result['history'][date_key] = history_entry.to_dict()
        
        # Remove None values to clean up the result
        return {k: v for k, v in result.items() if v is not None}
    
    def __str__(self) -> str:
        """String representation of the listing."""
        status_str = f" ({self.status})" if self.status else ""
        price_str = f" - ${self.price:,}" if self.price else ""
        return f"Listing(id='{self.id}', address='{self.formatted_address}'{status_str}{price_str})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the listing."""
        return (f"PropertyListing(id='{self.id}', formatted_address='{self.formatted_address}', "
                f"status='{self.status}', price={self.price}, bedrooms={self.bedrooms}, "
                f"bathrooms={self.bathrooms}, listing_type='{self.listing_type}')")


@dataclass
class ListingsResponse:
    """
    Response wrapper for /listings endpoint that returns multiple listings.
    
    This handles paginated responses from the listings API.
    """
    
    listings: List[PropertyListing] = field(default_factory=list)
    total_count: Optional[int] = None
    has_more: Optional[bool] = None
    next_offset: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListingsResponse':
        """Create ListingsResponse from API response dictionary."""
        listings = []
        
        # Handle different response formats
        if 'listings' in data:
            # Standard listings response
            listings_data = data.get('listings', [])
            if isinstance(listings_data, list):
                for listing_data in listings_data:
                    if isinstance(listing_data, dict):
                        listings.append(PropertyListing.from_dict(listing_data))
        elif isinstance(data, list):
            # Direct list of listings
            for listing_data in data:
                if isinstance(listing_data, dict):
                    listings.append(PropertyListing.from_dict(listing_data))
        elif isinstance(data, dict) and 'id' in data:
            # Single listing response
            listings.append(PropertyListing.from_dict(data))
        
        return cls(
            listings=listings,
            total_count=data.get('totalCount') if isinstance(data, dict) else None,
            has_more=data.get('hasMore') if isinstance(data, dict) else None,
            next_offset=data.get('nextOffset') if isinstance(data, dict) else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result: Dict[str, Any] = {
            'listings': [listing.to_dict() for listing in self.listings]
        }
        
        if self.total_count is not None:
            result['totalCount'] = self.total_count
        if self.has_more is not None:
            result['hasMore'] = self.has_more
        if self.next_offset is not None:
            result['nextOffset'] = self.next_offset
        
        return result


@dataclass
class SaleStatistics:
    """
    Sale market statistics for a group of properties.
    
    Contains statistical fields calculated based on active sale listings.
    """
    
    # Price statistics
    average_price: Optional[float] = None
    median_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Price per square foot statistics
    average_price_per_square_foot: Optional[float] = None
    median_price_per_square_foot: Optional[float] = None
    min_price_per_square_foot: Optional[float] = None
    max_price_per_square_foot: Optional[float] = None
    
    # Square footage statistics
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    
    # Days on market statistics
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    
    # Listing counts
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaleStatistics':
        """Create SaleStatistics from dictionary."""
        return cls(
            average_price=data.get('averagePrice'),
            median_price=data.get('medianPrice'),
            min_price=data.get('minPrice'),
            max_price=data.get('maxPrice'),
            average_price_per_square_foot=data.get('averagePricePerSquareFoot'),
            median_price_per_square_foot=data.get('medianPricePerSquareFoot'),
            min_price_per_square_foot=data.get('minPricePerSquareFoot'),
            max_price_per_square_foot=data.get('maxPricePerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SaleStatistics to dictionary format."""
        return {
            'averagePrice': self.average_price,
            'medianPrice': self.median_price,
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'averagePricePerSquareFoot': self.average_price_per_square_foot,
            'medianPricePerSquareFoot': self.median_price_per_square_foot,
            'minPricePerSquareFoot': self.min_price_per_square_foot,
            'maxPricePerSquareFoot': self.max_price_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class RentalStatistics:
    """
    Rental market statistics for a group of properties.
    
    Contains statistical fields calculated based on active rental listings.
    """
    
    # Rent statistics
    average_rent: Optional[float] = None
    median_rent: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    
    # Rent per square foot statistics
    average_rent_per_square_foot: Optional[float] = None
    median_rent_per_square_foot: Optional[float] = None
    min_rent_per_square_foot: Optional[float] = None
    max_rent_per_square_foot: Optional[float] = None
    
    # Square footage statistics
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    
    # Days on market statistics
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    
    # Listing counts
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RentalStatistics':
        """Create RentalStatistics from dictionary."""
        return cls(
            average_rent=data.get('averageRent'),
            median_rent=data.get('medianRent'),
            min_rent=data.get('minRent'),
            max_rent=data.get('maxRent'),
            average_rent_per_square_foot=data.get('averageRentPerSquareFoot'),
            median_rent_per_square_foot=data.get('medianRentPerSquareFoot'),
            min_rent_per_square_foot=data.get('minRentPerSquareFoot'),
            max_rent_per_square_foot=data.get('maxRentPerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert RentalStatistics to dictionary format."""
        return {
            'averageRent': self.average_rent,
            'medianRent': self.median_rent,
            'minRent': self.min_rent,
            'maxRent': self.max_rent,
            'averageRentPerSquareFoot': self.average_rent_per_square_foot,
            'medianRentPerSquareFoot': self.median_rent_per_square_foot,
            'minRentPerSquareFoot': self.min_rent_per_square_foot,
            'maxRentPerSquareFoot': self.max_rent_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class SaleDataByPropertyType:
    """Sale statistics grouped by property type."""
    property_type: Optional[str] = None
    
    # Include all sale statistics
    average_price: Optional[float] = None
    median_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price_per_square_foot: Optional[float] = None
    median_price_per_square_foot: Optional[float] = None
    min_price_per_square_foot: Optional[float] = None
    max_price_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaleDataByPropertyType':
        """Create SaleDataByPropertyType from dictionary."""
        return cls(
            property_type=data.get('propertyType'),
            average_price=data.get('averagePrice'),
            median_price=data.get('medianPrice'),
            min_price=data.get('minPrice'),
            max_price=data.get('maxPrice'),
            average_price_per_square_foot=data.get('averagePricePerSquareFoot'),
            median_price_per_square_foot=data.get('medianPricePerSquareFoot'),
            min_price_per_square_foot=data.get('minPricePerSquareFoot'),
            max_price_per_square_foot=data.get('maxPricePerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'propertyType': self.property_type,
            'averagePrice': self.average_price,
            'medianPrice': self.median_price,
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'averagePricePerSquareFoot': self.average_price_per_square_foot,
            'medianPricePerSquareFoot': self.median_price_per_square_foot,
            'minPricePerSquareFoot': self.min_price_per_square_foot,
            'maxPricePerSquareFoot': self.max_price_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class SaleDataByBedrooms:
    """Sale statistics grouped by number of bedrooms."""
    bedrooms: Optional[str] = None
    
    # Include all sale statistics
    average_price: Optional[float] = None
    median_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price_per_square_foot: Optional[float] = None
    median_price_per_square_foot: Optional[float] = None
    min_price_per_square_foot: Optional[float] = None
    max_price_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaleDataByBedrooms':
        """Create SaleDataByBedrooms from dictionary."""
        return cls(
            bedrooms=data.get('bedrooms'),
            average_price=data.get('averagePrice'),
            median_price=data.get('medianPrice'),
            min_price=data.get('minPrice'),
            max_price=data.get('maxPrice'),
            average_price_per_square_foot=data.get('averagePricePerSquareFoot'),
            median_price_per_square_foot=data.get('medianPricePerSquareFoot'),
            min_price_per_square_foot=data.get('minPricePerSquareFoot'),
            max_price_per_square_foot=data.get('maxPricePerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'bedrooms': self.bedrooms,
            'averagePrice': self.average_price,
            'medianPrice': self.median_price,
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'averagePricePerSquareFoot': self.average_price_per_square_foot,
            'medianPricePerSquareFoot': self.median_price_per_square_foot,
            'minPricePerSquareFoot': self.min_price_per_square_foot,
            'maxPricePerSquareFoot': self.max_price_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class RentalDataByPropertyType:
    """Rental statistics grouped by property type."""
    property_type: Optional[str] = None
    
    # Include all rental statistics
    average_rent: Optional[float] = None
    median_rent: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    average_rent_per_square_foot: Optional[float] = None
    median_rent_per_square_foot: Optional[float] = None
    min_rent_per_square_foot: Optional[float] = None
    max_rent_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RentalDataByPropertyType':
        """Create RentalDataByPropertyType from dictionary."""
        return cls(
            property_type=data.get('propertyType'),
            average_rent=data.get('averageRent'),
            median_rent=data.get('medianRent'),
            min_rent=data.get('minRent'),
            max_rent=data.get('maxRent'),
            average_rent_per_square_foot=data.get('averageRentPerSquareFoot'),
            median_rent_per_square_foot=data.get('medianRentPerSquareFoot'),
            min_rent_per_square_foot=data.get('minRentPerSquareFoot'),
            max_rent_per_square_foot=data.get('maxRentPerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'propertyType': self.property_type,
            'averageRent': self.average_rent,
            'medianRent': self.median_rent,
            'minRent': self.min_rent,
            'maxRent': self.max_rent,
            'averageRentPerSquareFoot': self.average_rent_per_square_foot,
            'medianRentPerSquareFoot': self.median_rent_per_square_foot,
            'minRentPerSquareFoot': self.min_rent_per_square_foot,
            'maxRentPerSquareFoot': self.max_rent_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class RentalDataByBedrooms:
    """Rental statistics grouped by number of bedrooms."""
    bedrooms: Optional[str] = None
    
    # Include all rental statistics
    average_rent: Optional[float] = None
    median_rent: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    average_rent_per_square_foot: Optional[float] = None
    median_rent_per_square_foot: Optional[float] = None
    min_rent_per_square_foot: Optional[float] = None
    max_rent_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RentalDataByBedrooms':
        """Create RentalDataByBedrooms from dictionary."""
        return cls(
            bedrooms=data.get('bedrooms'),
            average_rent=data.get('averageRent'),
            median_rent=data.get('medianRent'),
            min_rent=data.get('minRent'),
            max_rent=data.get('maxRent'),
            average_rent_per_square_foot=data.get('averageRentPerSquareFoot'),
            median_rent_per_square_foot=data.get('medianRentPerSquareFoot'),
            min_rent_per_square_foot=data.get('minRentPerSquareFoot'),
            max_rent_per_square_foot=data.get('maxRentPerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'bedrooms': self.bedrooms,
            'averageRent': self.average_rent,
            'medianRent': self.median_rent,
            'minRent': self.min_rent,
            'maxRent': self.max_rent,
            'averageRentPerSquareFoot': self.average_rent_per_square_foot,
            'medianRentPerSquareFoot': self.median_rent_per_square_foot,
            'minRentPerSquareFoot': self.min_rent_per_square_foot,
            'maxRentPerSquareFoot': self.max_rent_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }


@dataclass
class SaleHistoryEntry:
    """
    Historical sale market statistics for a specific month.
    
    Contains monthly historical data including overall stats and breakdowns.
    """
    date: Optional[str] = None
    
    # Overall statistics (inheriting from SaleStatistics)
    average_price: Optional[float] = None
    median_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price_per_square_foot: Optional[float] = None
    median_price_per_square_foot: Optional[float] = None
    min_price_per_square_foot: Optional[float] = None
    max_price_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    # Breakdown by property type and bedrooms
    data_by_property_type: List[SaleDataByPropertyType] = field(default_factory=list)
    data_by_bedrooms: List[SaleDataByBedrooms] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, date_key: str, data: Dict[str, Any]) -> 'SaleHistoryEntry':
        """Create SaleHistoryEntry from dictionary."""
        # Parse data by property type
        data_by_property_type = []
        if data.get('dataByPropertyType'):
            data_by_property_type = [
                SaleDataByPropertyType.from_dict(item) 
                for item in data['dataByPropertyType']
            ]
        
        # Parse data by bedrooms
        data_by_bedrooms = []
        if data.get('dataByBedrooms'):
            data_by_bedrooms = [
                SaleDataByBedrooms.from_dict(item) 
                for item in data['dataByBedrooms']
            ]
        
        return cls(
            date=data.get('date', f"{date_key}-01T00:00:00.000Z"),
            average_price=data.get('averagePrice'),
            median_price=data.get('medianPrice'),
            min_price=data.get('minPrice'),
            max_price=data.get('maxPrice'),
            average_price_per_square_foot=data.get('averagePricePerSquareFoot'),
            median_price_per_square_foot=data.get('medianPricePerSquareFoot'),
            min_price_per_square_foot=data.get('minPricePerSquareFoot'),
            max_price_per_square_foot=data.get('maxPricePerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings'),
            data_by_property_type=data_by_property_type,
            data_by_bedrooms=data_by_bedrooms
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            'date': self.date,
            'averagePrice': self.average_price,
            'medianPrice': self.median_price,
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'averagePricePerSquareFoot': self.average_price_per_square_foot,
            'medianPricePerSquareFoot': self.median_price_per_square_foot,
            'minPricePerSquareFoot': self.min_price_per_square_foot,
            'maxPricePerSquareFoot': self.max_price_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }
        
        if self.data_by_property_type:
            result['dataByPropertyType'] = [item.to_dict() for item in self.data_by_property_type]
        
        if self.data_by_bedrooms:
            result['dataByBedrooms'] = [item.to_dict() for item in self.data_by_bedrooms]
        
        return result


@dataclass
class RentalHistoryEntry:
    """
    Historical rental market statistics for a specific month.
    
    Contains monthly historical data including overall stats and breakdowns.
    """
    date: Optional[str] = None
    
    # Overall statistics (inheriting from RentalStatistics)
    average_rent: Optional[float] = None
    median_rent: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    average_rent_per_square_foot: Optional[float] = None
    median_rent_per_square_foot: Optional[float] = None
    min_rent_per_square_foot: Optional[float] = None
    max_rent_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    # Breakdown by property type and bedrooms
    data_by_property_type: List[RentalDataByPropertyType] = field(default_factory=list)
    data_by_bedrooms: List[RentalDataByBedrooms] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, date_key: str, data: Dict[str, Any]) -> 'RentalHistoryEntry':
        """Create RentalHistoryEntry from dictionary."""
        # Parse data by property type
        data_by_property_type = []
        if data.get('dataByPropertyType'):
            data_by_property_type = [
                RentalDataByPropertyType.from_dict(item) 
                for item in data['dataByPropertyType']
            ]
        
        # Parse data by bedrooms
        data_by_bedrooms = []
        if data.get('dataByBedrooms'):
            data_by_bedrooms = [
                RentalDataByBedrooms.from_dict(item) 
                for item in data['dataByBedrooms']
            ]
        
        return cls(
            date=data.get('date', f"{date_key}-01T00:00:00.000Z"),
            average_rent=data.get('averageRent'),
            median_rent=data.get('medianRent'),
            min_rent=data.get('minRent'),
            max_rent=data.get('maxRent'),
            average_rent_per_square_foot=data.get('averageRentPerSquareFoot'),
            median_rent_per_square_foot=data.get('medianRentPerSquareFoot'),
            min_rent_per_square_foot=data.get('minRentPerSquareFoot'),
            max_rent_per_square_foot=data.get('maxRentPerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings'),
            data_by_property_type=data_by_property_type,
            data_by_bedrooms=data_by_bedrooms
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            'date': self.date,
            'averageRent': self.average_rent,
            'medianRent': self.median_rent,
            'minRent': self.min_rent,
            'maxRent': self.max_rent,
            'averageRentPerSquareFoot': self.average_rent_per_square_foot,
            'medianRentPerSquareFoot': self.median_rent_per_square_foot,
            'minRentPerSquareFoot': self.min_rent_per_square_foot,
            'maxRentPerSquareFoot': self.max_rent_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }
        
        if self.data_by_property_type:
            result['dataByPropertyType'] = [item.to_dict() for item in self.data_by_property_type]
        
        if self.data_by_bedrooms:
            result['dataByBedrooms'] = [item.to_dict() for item in self.data_by_bedrooms]
        
        return result


@dataclass
class MarketSaleData:
    """
    Complete sale market data for a zip code.
    
    Contains current statistics, breakdowns, and historical data.
    """
    last_updated_date: Optional[str] = None
    
    # Current overall statistics
    average_price: Optional[float] = None
    median_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price_per_square_foot: Optional[float] = None
    median_price_per_square_foot: Optional[float] = None
    min_price_per_square_foot: Optional[float] = None
    max_price_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    # Breakdown by property type and bedrooms
    data_by_property_type: List[SaleDataByPropertyType] = field(default_factory=list)
    data_by_bedrooms: List[SaleDataByBedrooms] = field(default_factory=list)
    
    # Historical data
    history: Dict[str, SaleHistoryEntry] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketSaleData':
        """Create MarketSaleData from dictionary."""
        # Parse data by property type
        data_by_property_type = []
        if data.get('dataByPropertyType'):
            data_by_property_type = [
                SaleDataByPropertyType.from_dict(item) 
                for item in data['dataByPropertyType']
            ]
        
        # Parse data by bedrooms
        data_by_bedrooms = []
        if data.get('dataByBedrooms'):
            data_by_bedrooms = [
                SaleDataByBedrooms.from_dict(item) 
                for item in data['dataByBedrooms']
            ]
        
        # Parse history
        history = {}
        history_data = data.get('history', {})
        for date_key, history_entry_data in history_data.items():
            history[date_key] = SaleHistoryEntry.from_dict(date_key, history_entry_data)
        
        return cls(
            last_updated_date=data.get('lastUpdatedDate'),
            average_price=data.get('averagePrice'),
            median_price=data.get('medianPrice'),
            min_price=data.get('minPrice'),
            max_price=data.get('maxPrice'),
            average_price_per_square_foot=data.get('averagePricePerSquareFoot'),
            median_price_per_square_foot=data.get('medianPricePerSquareFoot'),
            min_price_per_square_foot=data.get('minPricePerSquareFoot'),
            max_price_per_square_foot=data.get('maxPricePerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings'),
            data_by_property_type=data_by_property_type,
            data_by_bedrooms=data_by_bedrooms,
            history=history
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            'lastUpdatedDate': self.last_updated_date,
            'averagePrice': self.average_price,
            'medianPrice': self.median_price,
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'averagePricePerSquareFoot': self.average_price_per_square_foot,
            'medianPricePerSquareFoot': self.median_price_per_square_foot,
            'minPricePerSquareFoot': self.min_price_per_square_foot,
            'maxPricePerSquareFoot': self.max_price_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }
        
        if self.data_by_property_type:
            result['dataByPropertyType'] = [item.to_dict() for item in self.data_by_property_type]
        
        if self.data_by_bedrooms:
            result['dataByBedrooms'] = [item.to_dict() for item in self.data_by_bedrooms]
        
        if self.history:
            result['history'] = {}
            for date_key, history_entry in self.history.items():
                result['history'][date_key] = history_entry.to_dict()
        
        return result


@dataclass
class MarketRentalData:
    """
    Complete rental market data for a zip code.
    
    Contains current statistics, breakdowns, and historical data.
    """
    last_updated_date: Optional[str] = None
    
    # Current overall statistics
    average_rent: Optional[float] = None
    median_rent: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    average_rent_per_square_foot: Optional[float] = None
    median_rent_per_square_foot: Optional[float] = None
    min_rent_per_square_foot: Optional[float] = None
    max_rent_per_square_foot: Optional[float] = None
    average_square_footage: Optional[float] = None
    median_square_footage: Optional[float] = None
    min_square_footage: Optional[float] = None
    max_square_footage: Optional[float] = None
    average_days_on_market: Optional[float] = None
    median_days_on_market: Optional[float] = None
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    new_listings: Optional[int] = None
    total_listings: Optional[int] = None
    
    # Breakdown by property type and bedrooms
    data_by_property_type: List[RentalDataByPropertyType] = field(default_factory=list)
    data_by_bedrooms: List[RentalDataByBedrooms] = field(default_factory=list)
    
    # Historical data
    history: Dict[str, RentalHistoryEntry] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketRentalData':
        """Create MarketRentalData from dictionary."""
        # Parse data by property type
        data_by_property_type = []
        if data.get('dataByPropertyType'):
            data_by_property_type = [
                RentalDataByPropertyType.from_dict(item) 
                for item in data['dataByPropertyType']
            ]
        
        # Parse data by bedrooms
        data_by_bedrooms = []
        if data.get('dataByBedrooms'):
            data_by_bedrooms = [
                RentalDataByBedrooms.from_dict(item) 
                for item in data['dataByBedrooms']
            ]
        
        # Parse history
        history = {}
        history_data = data.get('history', {})
        for date_key, history_entry_data in history_data.items():
            history[date_key] = RentalHistoryEntry.from_dict(date_key, history_entry_data)
        
        return cls(
            last_updated_date=data.get('lastUpdatedDate'),
            average_rent=data.get('averageRent'),
            median_rent=data.get('medianRent'),
            min_rent=data.get('minRent'),
            max_rent=data.get('maxRent'),
            average_rent_per_square_foot=data.get('averageRentPerSquareFoot'),
            median_rent_per_square_foot=data.get('medianRentPerSquareFoot'),
            min_rent_per_square_foot=data.get('minRentPerSquareFoot'),
            max_rent_per_square_foot=data.get('maxRentPerSquareFoot'),
            average_square_footage=data.get('averageSquareFootage'),
            median_square_footage=data.get('medianSquareFootage'),
            min_square_footage=data.get('minSquareFootage'),
            max_square_footage=data.get('maxSquareFootage'),
            average_days_on_market=data.get('averageDaysOnMarket'),
            median_days_on_market=data.get('medianDaysOnMarket'),
            min_days_on_market=data.get('minDaysOnMarket'),
            max_days_on_market=data.get('maxDaysOnMarket'),
            new_listings=data.get('newListings'),
            total_listings=data.get('totalListings'),
            data_by_property_type=data_by_property_type,
            data_by_bedrooms=data_by_bedrooms,
            history=history
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            'lastUpdatedDate': self.last_updated_date,
            'averageRent': self.average_rent,
            'medianRent': self.median_rent,
            'minRent': self.min_rent,
            'maxRent': self.max_rent,
            'averageRentPerSquareFoot': self.average_rent_per_square_foot,
            'medianRentPerSquareFoot': self.median_rent_per_square_foot,
            'minRentPerSquareFoot': self.min_rent_per_square_foot,
            'maxRentPerSquareFoot': self.max_rent_per_square_foot,
            'averageSquareFootage': self.average_square_footage,
            'medianSquareFootage': self.median_square_footage,
            'minSquareFootage': self.min_square_footage,
            'maxSquareFootage': self.max_square_footage,
            'averageDaysOnMarket': self.average_days_on_market,
            'medianDaysOnMarket': self.median_days_on_market,
            'minDaysOnMarket': self.min_days_on_market,
            'maxDaysOnMarket': self.max_days_on_market,
            'newListings': self.new_listings,
            'totalListings': self.total_listings
        }
        
        if self.data_by_property_type:
            result['dataByPropertyType'] = [item.to_dict() for item in self.data_by_property_type]
        
        if self.data_by_bedrooms:
            result['dataByBedrooms'] = [item.to_dict() for item in self.data_by_bedrooms]
        
        if self.history:
            result['history'] = {}
            for date_key, history_entry in self.history.items():
                result['history'][date_key] = history_entry.to_dict()
        
        return result


@dataclass
class MarketStatistics:
    """
    Complete market statistics response from the /markets endpoint.
    
    Contains both sale and rental market data for a specific zip code.
    """
    id: Optional[str] = None
    zip_code: Optional[str] = None
    sale_data: Optional[MarketSaleData] = None
    rental_data: Optional[MarketRentalData] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketStatistics':
        """Create MarketStatistics from dictionary."""
        # Parse sale data
        sale_data = None
        sale_data_raw = data.get('saleData')
        if sale_data_raw:
            sale_data = MarketSaleData.from_dict(sale_data_raw)
        
        # Parse rental data
        rental_data = None
        rental_data_raw = data.get('rentalData')
        if rental_data_raw:
            rental_data = MarketRentalData.from_dict(rental_data_raw)
        
        return cls(
            id=data.get('id'),
            zip_code=data.get('zipCode'),
            sale_data=sale_data,
            rental_data=rental_data
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result: Dict[str, Any] = {
            'id': self.id,
            'zipCode': self.zip_code
        }
        
        if self.sale_data:
            result['saleData'] = self.sale_data.to_dict()
        
        if self.rental_data:
            result['rentalData'] = self.rental_data.to_dict()
        
        return result
    
    def __str__(self) -> str:
        """String representation of the market statistics."""
        return f"MarketStatistics(zip_code='{self.zip_code}', id='{self.id}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the market statistics."""
        sale_listings = self.sale_data.total_listings if self.sale_data else 0
        rental_listings = self.rental_data.total_listings if self.rental_data else 0
        return (f"MarketStatistics(zip_code='{self.zip_code}', "
                f"sale_listings={sale_listings}, rental_listings={rental_listings})")


def filter_properties_by_criteria(
    properties: List[Property], 
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[float] = None,
    max_bathrooms: Optional[float] = None,
    min_sqft: Optional[int] = None,
    max_sqft: Optional[int] = None,
    property_types: Optional[List[str]] = None,
    min_year_built: Optional[int] = None,
    max_year_built: Optional[int] = None
) -> List[Property]:
    """
    Filter a list of properties by various criteria.
    
    Args:
        properties: List of Property objects to filter
        min_bedrooms: Minimum number of bedrooms
        max_bedrooms: Maximum number of bedrooms
        min_bathrooms: Minimum number of bathrooms
        max_bathrooms: Maximum number of bathrooms
        min_sqft: Minimum square footage
        max_sqft: Maximum square footage
        property_types: List of acceptable property types
        min_year_built: Minimum year built
        max_year_built: Maximum year built
        
    Returns:
        Filtered list of properties
    """
    filtered = properties
    
    if min_bedrooms is not None:
        filtered = [p for p in filtered if p.bedrooms is not None and p.bedrooms >= min_bedrooms]
    
    if max_bedrooms is not None:
        filtered = [p for p in filtered if p.bedrooms is not None and p.bedrooms <= max_bedrooms]
    
    if min_bathrooms is not None:
        filtered = [p for p in filtered if p.bathrooms is not None and p.bathrooms >= min_bathrooms]
    
    if max_bathrooms is not None:
        filtered = [p for p in filtered if p.bathrooms is not None and p.bathrooms <= max_bathrooms]
    
    if min_sqft is not None:
        filtered = [p for p in filtered if p.square_footage is not None and p.square_footage >= min_sqft]
    
    if max_sqft is not None:
        filtered = [p for p in filtered if p.square_footage is not None and p.square_footage <= max_sqft]
    
    if property_types is not None:
        filtered = [p for p in filtered if p.property_type in property_types]
    
    if min_year_built is not None:
        filtered = [p for p in filtered if p.year_built is not None and p.year_built >= min_year_built]
    
    if max_year_built is not None:
        filtered = [p for p in filtered if p.year_built is not None and p.year_built <= max_year_built]
    
    return filtered
