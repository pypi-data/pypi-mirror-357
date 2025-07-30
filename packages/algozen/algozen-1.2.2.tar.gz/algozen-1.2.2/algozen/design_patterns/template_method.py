"""
Template Method Pattern Implementation.

This module provides an implementation of the Template Method pattern, which defines
the skeleton of an algorithm in the superclass but lets subclasses override specific
steps of the algorithm without changing its structure.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
import os
import json
import csv
from datetime import datetime

T = TypeVar('T')

class DataExporter(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of some
    algorithm, composed of calls to (usually) abstract primitive operations.
    
    Concrete subclasses should implement these operations, but leave the template
    method itself intact.
    """
    def export_data(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        The template method defines the skeleton of an algorithm.
        
        Args:
            data: The data to be exported.
            output_path: The path where the exported file should be saved.
            
        Raises:
            ValueError: If the data is empty or invalid.
        """
        if not data:
            raise ValueError("No data to export")
        
        # Validate data (hook)
        self._validate_data(data)
        
        # Prepare output directory
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export the data
        self._export(data, output_path)
        
        # Post-export hook
        self._post_export(output_path)
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Hook method for data validation. Subclasses can override this method
        to provide custom validation logic.
        
        Args:
            data: The data to validate.
            
        Raises:
            ValueError: If the data is invalid.
        """
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("Data must be a list of dictionaries")
    
    @abstractmethod
    def _export(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Primitive operation that must be overridden by subclasses to implement
        the actual export logic.
        
        Args:
            data: The data to export.
            output_path: The path where the exported file should be saved.
        """
        pass
    
    def _post_export(self, output_path: str) -> None:
        """
        Hook method called after the export is complete. Subclasses can override
        this method to perform any post-export operations.
        
        Args:
            output_path: The path where the exported file was saved.
        """
        print(f"Data successfully exported to {output_path}")

class JSONExporter(DataExporter):
    """
    Concrete class that implements the JSON export algorithm.
    """
    def _export(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to a JSON file.
        
        Args:
            data: The data to export.
            output_path: The path where the JSON file should be saved.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _post_export(self, output_path: str) -> None:
        """
        Add a timestamp to the exported file.
        
        Args:
            output_path: The path to the exported file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"JSON export completed at {timestamp}")

class CSVExporter(DataExporter):
    """
    Concrete class that implements the CSV export algorithm.
    """
    def _export(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to a CSV file.
        
        Args:
            data: The data to export.
            output_path: The path where the CSV file should be saved.
            
        Raises:
            ValueError: If the data is not a list of dictionaries with consistent keys.
        """
        if not data:
            return
            
        # Get all unique keys from all dictionaries
        fieldnames = set()
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("All items in data must be dictionaries")
            fieldnames.update(item.keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(data)
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Validate that all items in the data are dictionaries.
        
        Args:
            data: The data to validate.
            
        Raises:
            ValueError: If any item is not a dictionary.
        """
        super()._validate_data(data)
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("All items in data must be dictionaries")

class ReportGenerator(ABC):
    """
    Another example of the Template Method pattern for generating reports.
    """
    def generate_report(self) -> str:
        """
        The template method that defines the skeleton of the report generation algorithm.
        
        Returns:
            The generated report as a string.
        """
        report = []
        report.append(self._get_header())
        report.append(self._get_title())
        report.append(self._get_body())
        report.append(self._get_footer())
        return "\n".join(report)
    
    def _get_header(self) -> str:
        """
        Hook method for the report header.
        
        Returns:
            The report header as a string.
        """
        return ""
    
    @abstractmethod
    def _get_title(self) -> str:
        """
        Abstract method for the report title.
        
        Returns:
            The report title as a string.
        """
        pass
    
    @abstractmethod
    def _get_body(self) -> str:
        """
        Abstract method for the report body.
        
        Returns:
            The report body as a string.
        """
        pass
    
    def _get_footer(self) -> str:
        """
        Hook method for the report footer.
        
        Returns:
            The report footer as a string.
        """
        return f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

class HTMLReportGenerator(ReportGenerator):
    """
    Concrete implementation of ReportGenerator for HTML reports.
    """
    def _get_header(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
        """
    
    def _get_title(self) -> str:
        return "<h1>Monthly Sales Report</h1>"
    
    def _get_body(self) -> str:
        # In a real implementation, this would fetch data from a data source
        sales_data = [
            {"month": "January", "sales": 15000},
            {"month": "February", "sales": 18000},
            {"month": "March", "sales": 22000},
        ]
        
        rows = []
        for item in sales_data:
            rows.append(f"<tr><td>{item['month']}</td><td>${item['sales']:,.2f}</td></tr>")
        
        return """
        <table>
            <thead>
                <tr><th>Month</th><th>Sales</th></tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
        """.format("\n".join(rows))
    
    def _get_footer(self) -> str:
        return f"""
        <footer style="margin-top: 20px; font-size: 0.8em; color: #666;">
            {super()._get_footer()}
        </footer>
        </body>
        </html>
        """

class TextReportGenerator(ReportGenerator):
    """
    Concrete implementation of ReportGenerator for plain text reports.
    """
    def _get_title(self) -> str:
        return "MONTHLY SALES REPORT\n" + "=" * 40
    
    def _get_body(self) -> str:
        # In a real implementation, this would fetch data from a data source
        sales_data = [
            {"month": "January", "sales": 15000},
            {"month": "February", "sales": 18000},
            {"month": "March", "sales": 22000},
        ]
        
        lines = ["Month         | Sales", "-" * 25]
        for item in sales_data:
            lines.append(f"{item['month']:13} | ${item['sales']:,.2f}")
        
        return "\n".join(lines)
