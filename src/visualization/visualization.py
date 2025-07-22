"""
Visualization Module

This module handles generating graphs and visualizations for real estate data analysis.
Creates various types of charts including price trends, market analysis, and geographic distributions.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class GraphGenerator:
    """Main class for generating real estate data visualizations."""
    
    def __init__(self, visualization_config: Dict[str, Any]):
        """
        Initialize the graph generator with configuration.
        
        Args:
            visualization_config: Dictionary containing visualization settings
        """
        self.config = visualization_config
        self.figure_size = self.config.get('figure_size', (12, 8))
        self.dpi = self.config.get('dpi', 300)
        self.format = self.config.get('format', 'png')
        
    def generate_all_graphs(self, analysis_results: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate all graphs based on analysis results.
        
        Args:
            analysis_results: Results from RealEstateAnalyzer
            output_dir: Directory to save graphs
            
        Returns:
            List of generated file paths
        """
        logger.info("Generating all visualization graphs")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        try:
            # Price analysis graphs
            if 'price_analysis' in analysis_results:
                files = self._generate_price_analysis_graphs(
                    analysis_results['price_analysis'], 
                    output_path
                )
                generated_files.extend(files)
            
            # Market trends graphs
            if 'market_trends' in analysis_results:
                files = self._generate_market_trends_graphs(
                    analysis_results['market_trends'],
                    output_path
                )
                generated_files.extend(files)
            
            # Location analysis graphs
            if 'location_analysis' in analysis_results:
                files = self._generate_location_analysis_graphs(
                    analysis_results['location_analysis'],
                    output_path
                )
                generated_files.extend(files)
            
            # Property type analysis graphs
            if 'property_type_analysis' in analysis_results:
                files = self._generate_property_type_graphs(
                    analysis_results['property_type_analysis'],
                    output_path
                )
                generated_files.extend(files)
            
            # Time on market analysis
            if 'time_on_market' in analysis_results:
                files = self._generate_time_on_market_graphs(
                    analysis_results['time_on_market'],
                    output_path
                )
                generated_files.extend(files)
            
            # Investment opportunities visualization
            if 'investment_opportunities' in analysis_results:
                files = self._generate_investment_opportunity_graphs(
                    analysis_results['investment_opportunities'],
                    output_path
                )
                generated_files.extend(files)
            
            # Generate summary dashboard
            summary_file = self._generate_summary_dashboard(analysis_results, output_path)
            if summary_file:
                generated_files.append(summary_file)
            
            logger.info(f"Generated {len(generated_files)} visualization files")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error generating graphs: {str(e)}")
            return generated_files
    
    def _generate_price_analysis_graphs(self, price_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate price analysis visualizations."""
        files = []
        
        try:
            # Price distribution histogram
            if 'price_statistics' in price_data:
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                stats = price_data['price_statistics']
                
                # Create a mock distribution for visualization (in real scenario, you'd have the actual data)
                # This is a placeholder - you'd pass actual price data
                ax.axvline(stats['median'], color='red', linestyle='--', label=f"Median: ${stats['median']:,.0f}")
                ax.axvline(stats['mean'], color='blue', linestyle='--', label=f"Mean: ${stats['mean']:,.0f}")
                
                plt.title('Price Distribution Analysis')
                plt.xlabel('Price ($)')
                plt.ylabel('Frequency')
                plt.legend()
                
                file_path = output_dir / f'price_distribution.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
            
            # Price ranges bar chart
            if 'price_ranges' in price_data:
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                ranges = price_data['price_ranges']
                categories = list(ranges.keys())
                values = list(ranges.values())
                
                bars = ax.bar(categories, values)
                ax.set_title('Property Count by Price Range')
                ax.set_xlabel('Price Range')
                ax.set_ylabel('Number of Properties')
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                file_path = output_dir / f'price_ranges.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error generating price analysis graphs: {str(e)}")
        
        return files
    
    def _generate_market_trends_graphs(self, trends_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate market trends visualizations."""
        files = []
        
        try:
            if 'monthly_stats' not in trends_data:
                return files
            
            monthly_data = trends_data['monthly_stats']
            
            # Price trend over time
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figure_size[0], self.figure_size[1] * 1.2))
            
            # Mock data for demonstration - in real implementation, you'd extract from monthly_data
            months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
            avg_prices = [450000, 455000, 460000, 465000, 470000, 475000]  # Example data
            property_counts = [120, 135, 150, 140, 160, 155]  # Example data
            
            # Average price trend
            ax1.plot(months, avg_prices, marker='o', linewidth=2, markersize=8)
            ax1.set_title('Average Property Price Trend')
            ax1.set_ylabel('Average Price ($)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Property volume trend
            ax2.bar(months, property_counts, alpha=0.7)
            ax2.set_title('Property Listing Volume')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Number of Listings')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            file_path = output_dir / f'market_trends.{self.format}'
            plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            files.append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error generating market trends graphs: {str(e)}")
        
        return files
    
    def _generate_location_analysis_graphs(self, location_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate location analysis visualizations."""
        files = []
        
        try:
            # Top cities by property count
            if 'hotspots' in location_data:
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                hotspots = location_data['hotspots']
                cities = list(hotspots.keys())[:10]  # Top 10 cities
                counts = list(hotspots.values())[:10]
                
                bars = ax.barh(cities, counts)
                ax.set_title('Top Cities by Property Listings')
                ax.set_xlabel('Number of Properties')
                
                # Add value labels
                for bar, count in zip(bars, counts):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2,
                           f'{count}', ha='left', va='center', padding=5)
                
                file_path = output_dir / f'top_cities.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
            
            # Average price by city (if available)
            if 'cities' in location_data:
                # This would use actual city price data
                # Placeholder implementation
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                # Mock data for demonstration
                sample_cities = ['San Francisco', 'New York', 'Los Angeles', 'Seattle', 'Austin']
                sample_prices = [850000, 620000, 720000, 580000, 480000]
                
                bars = ax.bar(sample_cities, sample_prices)
                ax.set_title('Average Property Price by City')
                ax.set_ylabel('Average Price ($)')
                
                # Format y-axis as currency
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                
                # Add value labels
                for bar, price in zip(bars, sample_prices):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'${price:,.0f}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                file_path = output_dir / f'price_by_city.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
                
        except Exception as e:
            logger.error(f"Error generating location analysis graphs: {str(e)}")
        
        return files
    
    def _generate_property_type_graphs(self, property_type_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate property type analysis visualizations."""
        files = []
        
        try:
            if 'type_distribution' in property_type_data:
                # Property type distribution pie chart
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                distribution = property_type_data['type_distribution']
                labels = list(distribution.keys())
                sizes = list(distribution.values())
                
                # Create pie chart
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                
                # Beautify the text
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                ax.set_title('Property Distribution by Type')
                
                file_path = output_dir / f'property_type_distribution.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error generating property type graphs: {str(e)}")
        
        return files
    
    def _generate_time_on_market_graphs(self, time_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate time on market visualizations."""
        files = []
        
        try:
            if 'categories' in time_data:
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                categories = time_data['categories']
                labels = ['0-30 days', '31-90 days', '91-180 days', '180+ days']
                values = [
                    categories.get('quick_sale_0_30_days', 0),
                    categories.get('normal_31_90_days', 0),
                    categories.get('slow_91_180_days', 0),
                    categories.get('stale_over_180_days', 0)
                ]
                
                colors = ['green', 'yellow', 'orange', 'red']
                bars = ax.bar(labels, values, color=colors, alpha=0.7)
                
                ax.set_title('Properties by Days on Market')
                ax.set_ylabel('Number of Properties')
                ax.set_xlabel('Days on Market Range')
                
                # Add value labels
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                file_path = output_dir / f'days_on_market.{self.format}'
                plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                files.append(str(file_path))
                
        except Exception as e:
            logger.error(f"Error generating time on market graphs: {str(e)}")
        
        return files
    
    def _generate_investment_opportunity_graphs(self, investment_data: Dict[str, Any], output_dir: Path) -> List[str]:
        """Generate investment opportunity visualizations."""
        files = []
        
        try:
            # Create a summary of investment opportunities
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Opportunity counts
            opportunity_types = ['Underpriced', 'Long on Market', 'Hot Market Deals']
            counts = [
                len(investment_data.get('underpriced_properties', [])),
                len(investment_data.get('long_on_market', [])),
                len(investment_data.get('hot_market_deals', []))
            ]
            
            ax1.bar(opportunity_types, counts, color=['green', 'orange', 'blue'], alpha=0.7)
            ax1.set_title('Investment Opportunities by Type')
            ax1.set_ylabel('Number of Properties')
            
            # Add value labels
            for i, (bar, count) in enumerate(zip(ax1.patches, counts)):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{count}', ha='center', va='bottom')
            
            # Mock visualization for other quadrants
            ax2.text(0.5, 0.5, 'Price vs Value\nScatter Plot\n(Requires actual data)', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Price vs Value Analysis')
            
            ax3.text(0.5, 0.5, 'Geographic Distribution\nof Opportunities\n(Requires location data)', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Geographic Opportunity Map')
            
            ax4.text(0.5, 0.5, 'ROI Potential\nEstimation\n(Requires market data)', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('ROI Potential Analysis')
            
            plt.tight_layout()
            file_path = output_dir / f'investment_opportunities.{self.format}'
            plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            files.append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error generating investment opportunity graphs: {str(e)}")
        
        return files
    
    def _generate_summary_dashboard(self, analysis_results: Dict[str, Any], output_dir: Path) -> Optional[str]:
        """Generate a summary dashboard with key metrics."""
        try:
            fig = plt.figure(figsize=(20, 14))
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # Market summary
            if 'market_summary' in analysis_results:
                summary = analysis_results['market_summary']
                
                ax1 = fig.add_subplot(gs[0, 0])
                ax1.text(0.1, 0.8, 'MARKET SUMMARY', fontsize=16, fontweight='bold')
                ax1.text(0.1, 0.6, f"Total Properties: {summary.get('total_properties', 'N/A')}", fontsize=12)
                ax1.text(0.1, 0.4, f"Median Price: ${summary.get('price_summary', {}).get('median_price', 0):,.0f}", fontsize=12)
                ax1.text(0.1, 0.2, f"Average Price: ${summary.get('price_summary', {}).get('average_price', 0):,.0f}", fontsize=12)
                ax1.set_xlim(0, 1)
                ax1.set_ylim(0, 1)
                ax1.axis('off')
            
            # Add other summary visualizations
            # This would include mini versions of the main charts
            
            plt.suptitle('Real Estate Market Analysis Dashboard', fontsize=20, fontweight='bold')
            
            file_path = output_dir / f'dashboard_summary.{self.format}'
            plt.savefig(file_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error generating summary dashboard: {str(e)}")
            return None
