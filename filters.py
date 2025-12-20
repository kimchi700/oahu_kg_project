"""
filters.py - Object-Oriented Filter Management
Refactored to use FilterManager class
"""

import pandas as pd
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum


class PredicateType(Enum):
    """Enumeration of predicate types for filtering"""
    COMMUNITY = ['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH']
    LOCATION = 'ORIGINALLY_FROM'
    RESIDENCE = 'LIVES_IN'
    RELIGION = 'HAS_RELIGIOUS_VIEW'
    EDUCATION = 'HAS_EDUCATION_LEVEL'
    GENDER = 'HAS_THE_GENDER'
    SEXUALITY = 'ASSOCIATED_WITH'  # with LGBTQ in object


@dataclass
class FilterValues:
    """Data class to hold all filter values"""
    communities: List[str]
    locations: List[str]
    residence: List[str]
    religions: List[str]
    education_levels: List[str]
    genders: List[str]
    sexualities: List[str]
    
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format"""
        return {
            'communities': self.communities,
            'locations': self.locations,
            'residence': self.residence,
            'religions': self.religions,
            'education_levels': self.education_levels,
            'genders': self.genders,
            'sexualities': self.sexualities
        }


class FilterManager:
    """
    Manages extraction and validation of filter values from knowledge graph data.
    
    Responsibilities:
    - Extract unique values for each filter category
    - Validate filter values
    - Provide filter options for UI components
    """
    
    def __init__(self, triples_df: pd.DataFrame):
        """
        Initialize FilterManager with triples dataframe.
        
        Args:
            triples_df: DataFrame with subject, predicate, object columns
        """
        self.df = triples_df
        self._filter_values: FilterValues = None
    
    def extract_all_filters(self) -> FilterValues:
        """
        Extract all filter values from the dataframe.
        
        Returns:
            FilterValues object containing all filter options
        """
        self._filter_values = FilterValues(
            communities=self._extract_communities(),
            locations=self._extract_locations(),
            residence=self._extract_residence(),
            religions=self._extract_religions(),
            education_levels=self._extract_education_levels(),
            genders=self._extract_genders(),
            sexualities=self._extract_sexualities()
        )
        return self._filter_values
    
    def _extract_communities(self) -> List[str]:
        """Extract unique community names."""
        communities: Set[str] = set()
        
        # Get communities from relationships
        for predicate in PredicateType.COMMUNITY.value:
            matching_rows = self.df[self.df['predicate'] == predicate]
            communities.update(matching_rows['subject'].dropna().unique())
        
        # Get top activity subjects
        activity_subjects = self.df['subject'].value_counts().head(50).index.tolist()
        communities.update(activity_subjects)
        
        # Filter and sort
        return self._clean_and_sort(communities)
    
    def _extract_locations(self) -> List[str]:
        """Extract unique location values (Originally From)."""
        locations: Set[str] = set()
        matching_rows = self.df[self.df['predicate'] == PredicateType.LOCATION.value]
        locations.update(matching_rows['object'].dropna().unique())
        return self._clean_and_sort(locations)
    
    def _extract_residence(self) -> List[str]:
        """Extract unique residence values (Lives In)."""
        residence: Set[str] = set()
        matching_rows = self.df[self.df['predicate'] == PredicateType.RESIDENCE.value]
        residence.update(matching_rows['object'].dropna().unique())
        return self._clean_and_sort(residence)
    
    def _extract_religions(self) -> List[str]:
        """Extract unique religion values."""
        matching_rows = self.df[self.df['predicate'] == PredicateType.RELIGION.value]
        religions = matching_rows['object'].dropna().unique()
        return self._clean_and_sort(religions)
    
    def _extract_education_levels(self) -> List[str]:
        """Extract unique education level values."""
        matching_rows = self.df[self.df['predicate'] == PredicateType.EDUCATION.value]
        education_levels = matching_rows['object'].dropna().unique()
        return self._clean_and_sort(education_levels)
    
    def _extract_genders(self) -> List[str]:
        """Extract unique gender values."""
        matching_rows = self.df[self.df['predicate'] == PredicateType.GENDER.value]
        genders = matching_rows['object'].dropna().unique()
        return self._clean_and_sort(genders)
    
    def _extract_sexualities(self) -> List[str]:
        """Extract unique sexuality values (LGBTQ-related)."""
        sexualities: Set[str] = set()
        lgbtq_mask = (
            (self.df['predicate'] == PredicateType.SEXUALITY.value) &
            (self.df['object'].str.contains('LGBTQ', case=False, na=False))
        )
        lgbtq_nodes = self.df[lgbtq_mask]['object'].unique()
        sexualities.update(lgbtq_nodes)
        return self._clean_and_sort(sexualities)
    
    def _clean_and_sort(self, values) -> List[str]:
        """
        Clean and sort filter values.
        
        Args:
            values: Set or array of values
            
        Returns:
            Sorted list of valid string values
        """
        cleaned = [
            v for v in values 
            if isinstance(v, str) and v != 'nan' and v.strip()
        ]
        return sorted(cleaned)
    
    def get_filter_values(self) -> FilterValues:
        """
        Get filter values (extracts if not already done).
        
        Returns:
            FilterValues object
        """
        if self._filter_values is None:
            self.extract_all_filters()
        return self._filter_values
    
    def get_filter_dict(self) -> Dict[str, List[str]]:
        """
        Get filter values as dictionary.
        
        Returns:
            Dictionary mapping filter names to value lists
        """
        filter_values = self.get_filter_values()
        return filter_values.to_dict()
    
    def validate_filter_values(self, 
                              filter_type: str, 
                              values: List[str]) -> List[str]:
        """
        Validate that filter values exist in the extracted options.
        
        Args:
            filter_type: Type of filter (e.g., 'communities', 'genders')
            values: List of values to validate
            
        Returns:
            List of valid values (subset of input)
        """
        filter_dict = self.get_filter_dict()
        
        if filter_type not in filter_dict:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        valid_values = set(filter_dict[filter_type])
        return [v for v in values if v in valid_values]
    
    def get_filter_count(self, filter_type: str) -> int:
        """
        Get count of available values for a filter type.
        
        Args:
            filter_type: Type of filter
            
        Returns:
            Number of available values
        """
        filter_dict = self.get_filter_dict()
        if filter_type not in filter_dict:
            return 0
        return len(filter_dict[filter_type])
    
    def get_all_filter_counts(self) -> Dict[str, int]:
        """
        Get counts for all filter types.
        
        Returns:
            Dictionary mapping filter types to counts
        """
        filter_dict = self.get_filter_dict()
        return {
            filter_type: len(values)
            for filter_type, values in filter_dict.items()
        }


# Backward compatibility: functional interface
def extract_filter_values(df: pd.DataFrame) -> dict:
    """
    Legacy function - extracts filter values using FilterManager class.
    
    Args:
        df: DataFrame with triples
        
    Returns:
        Dictionary of filter values
    """
    manager = FilterManager(df)
    return manager.get_filter_dict()