"""
Dataset Validation Framework
"""

import logging
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import pyarrow as pa
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, 
                 is_valid: bool = True, 
                 issues: Optional[List[Dict[str, Any]]] = None,
                 validation_time: Optional[str] = None):
        """
        Initialize validation result
        
        Args:
            is_valid: Whether the dataset is valid
            issues: List of validation issues found
            validation_time: When validation was performed
        """
        self.is_valid = is_valid
        self.issues = issues or []
        self.validation_time = validation_time or datetime.now().isoformat()
        
    def add_issue(self, 
                 issue_type: str, 
                 description: str, 
                 severity: str = 'warning',
                 location: Optional[Union[str, List, Dict]] = None) -> None:
        """
        Add a validation issue
        
        Args:
            issue_type: Type of issue (schema, missing, format, etc.)
            description: Human-readable description
            severity: Issue severity ('error', 'warning', 'info')
            location: Where issue was found (column, row, etc.)
        """
        self.issues.append({
            'type': issue_type,
            'description': description,
            'severity': severity,
            'location': location,
            'timestamp': datetime.now().isoformat()
        })
        
        # Set as invalid if any error-level issues
        if severity == 'error':
            self.is_valid = False
            
    def get_issues_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get issues filtered by severity"""
        return [issue for issue in self.issues if issue['severity'] == severity]
    
    def get_issues_by_type(self, issue_type: str) -> List[Dict[str, Any]]:
        """Get issues filtered by type"""
        return [issue for issue in self.issues if issue['type'] == issue_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""
        return {
            'is_valid': self.is_valid,
            'issues': self.issues,
            'validation_time': self.validation_time,
            'issue_count': len(self.issues),
            'error_count': len(self.get_issues_by_severity('error')),
            'warning_count': len(self.get_issues_by_severity('warning')),
            'info_count': len(self.get_issues_by_severity('info'))
        }
    
    def summary(self) -> str:
        """Get a human-readable summary"""
        if self.is_valid and not self.issues:
            return "✅ Dataset is valid with no issues."
            
        error_count = len(self.get_issues_by_severity('error'))
        warning_count = len(self.get_issues_by_severity('warning'))
        info_count = len(self.get_issues_by_severity('info'))
        
        result = []
        if self.is_valid:
            result.append("✅ Dataset is valid")
        else:
            result.append("❌ Dataset is invalid")
            
        if error_count:
            result.append(f"{error_count} error(s)")
        if warning_count:
            result.append(f"{warning_count} warning(s)")
        if info_count:
            result.append(f"{info_count} info message(s)")
            
        return ", ".join(result)
    

class DatasetValidator:
    """
    Professional dataset validation framework
    
    Features:
    - Schema validation
    - Data quality checks
    - Custom validation rules
    - Comprehensive reporting
    """
    
    def __init__(self):
        """Initialize validator with default checks"""
        self.validation_rules = {}
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """Set up default validation rules"""
        # Schema validation
        self.add_rule('schema_match', self._validate_schema)
        
        # Missing value checks
        self.add_rule('missing_values', self._check_missing_values)
        
        # Data type checks
        self.add_rule('data_types', self._check_data_types)
        
        # Value range checks
        self.add_rule('value_ranges', self._check_value_ranges)
    
    def add_rule(self, 
                rule_name: str, 
                validation_func: Callable,
                description: Optional[str] = None) -> None:
        """
        Add a validation rule
        
        Args:
            rule_name: Unique name for the rule
            validation_func: Function that performs validation
            description: Optional description of the rule
        """
        self.validation_rules[rule_name] = {
            'function': validation_func,
            'description': description or f"Validation rule: {rule_name}"
        }
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a validation rule
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        if rule_name in self.validation_rules:
            del self.validation_rules[rule_name]
            return True
        return False
    
    def validate(self, 
                dataset, 
                rules: Optional[List[str]] = None,
                schema: Optional[Union[Dict, pa.Schema]] = None,
                options: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a dataset
        
        Args:
            dataset: Dataset to validate
            rules: Optional list of rule names to run (runs all if None)
            schema: Optional schema to validate against
            options: Optional validation options
            
        Returns:
            ValidationResult with validation outcomes
        """
        result = ValidationResult()
        options = options or {}
        
        # Determine which rules to run
        rules_to_run = rules or list(self.validation_rules.keys())
        
        # Run each specified rule
        for rule_name in rules_to_run:
            if rule_name not in self.validation_rules:
                result.add_issue(
                    'validation_config', 
                    f"Unknown validation rule: {rule_name}",
                    'warning'
                )
                continue
                
            rule = self.validation_rules[rule_name]
            try:
                # Execute validation rule
                rule['function'](dataset, result, schema, options)
            except Exception as e:
                # Log validation failures but don't crash
                logger.error(f"Validation rule '{rule_name}' failed: {e}")
                result.add_issue(
                    'validation_error', 
                    f"Validation rule '{rule_name}' failed: {e}",
                    'error'
                )
                
        return result
    
    def _validate_schema(self, 
                        dataset, 
                        result: ValidationResult,
                        schema: Optional[Union[Dict, pa.Schema]],
                        options: Dict[str, Any]) -> None:
        """
        Validate dataset against schema
        
        Args:
            dataset: Dataset to validate
            result: ValidationResult to update
            schema: Schema to validate against
            options: Validation options
        """
        if not schema:
            # Try to get schema from dataset
            if hasattr(dataset, 'schema') and dataset.schema:
                schema = dataset.schema
            else:
                result.add_issue(
                    'schema', 
                    "No schema provided for validation",
                    'info'
                )
                return
                
        # Convert dataset to PyArrow Table or pandas DataFrame
        if hasattr(dataset, 'to_pyarrow'):
            data = dataset.to_pyarrow()
        elif hasattr(dataset, 'to_pandas'):
            data = dataset.to_pandas()
        else:
            data = dataset
            
        # Schema validation
        if isinstance(schema, pa.Schema):
            # PyArrow schema validation
            if isinstance(data, pa.Table):
                # Check if all required columns exist
                missing_cols = set(schema.names) - set(data.column_names)
                if missing_cols:
                    result.add_issue(
                        'schema', 
                        f"Missing required columns: {', '.join(missing_cols)}",
                        'error',
                        {'missing_columns': list(missing_cols)}
                    )
                
                # Check if datatypes match
                for field in schema:
                    field_name = field.name
                    if field_name in data.column_names:
                        expected_type = field.type
                        actual_type = data.schema.field(field_name).type
                        if not expected_type.equals(actual_type):
                            result.add_issue(
                                'schema', 
                                f"Column '{field_name}' has type {actual_type} but expected {expected_type}",
                                'error',
                                {'column': field_name, 'expected': str(expected_type), 'actual': str(actual_type)}
                            )
        
        elif isinstance(schema, dict):
            # Dictionary-based schema validation
            if isinstance(data, pd.DataFrame):
                # Check required columns
                if 'required' in schema:
                    missing_cols = set(schema['required']) - set(data.columns)
                    if missing_cols:
                        result.add_issue(
                            'schema', 
                            f"Missing required columns: {', '.join(missing_cols)}",
                            'error',
                            {'missing_columns': list(missing_cols)}
                        )
                
                # Check column types if specified
                if 'properties' in schema:
                    for col_name, properties in schema['properties'].items():
                        if col_name in data.columns:
                            # Type validation
                            if 'type' in properties:
                                self._validate_column_type(
                                    data, col_name, properties['type'], result
                                )
                            
                            # Pattern validation
                            if 'pattern' in properties and pd.api.types.is_string_dtype(data[col_name].dtype):
                                pattern = re.compile(properties['pattern'])
                                invalid_values = data[~data[col_name].astype(str).str.match(pattern)]
                                if len(invalid_values) > 0:
                                    result.add_issue(
                                        'schema', 
                                        f"Column '{col_name}' has {len(invalid_values)} values not matching pattern '{properties['pattern']}'",
                                        'error',
                                        {'column': col_name, 'invalid_count': len(invalid_values)}
                                    )
    
    def _validate_column_type(self, 
                            df: pd.DataFrame, 
                            column_name: str, 
                            expected_type: str,
                            result: ValidationResult) -> None:
        """Validate column data type"""
        if expected_type == 'string' and not pd.api.types.is_string_dtype(df[column_name].dtype):
            result.add_issue(
                'schema', 
                f"Column '{column_name}' should be string type",
                'error',
                {'column': column_name, 'expected': 'string', 'actual': str(df[column_name].dtype)}
            )
        elif expected_type == 'number' and not pd.api.types.is_numeric_dtype(df[column_name].dtype):
            result.add_issue(
                'schema', 
                f"Column '{column_name}' should be numeric type",
                'error',
                {'column': column_name, 'expected': 'number', 'actual': str(df[column_name].dtype)}
            )
        elif expected_type == 'integer' and not pd.api.types.is_integer_dtype(df[column_name].dtype):
            result.add_issue(
                'schema', 
                f"Column '{column_name}' should be integer type",
                'error',
                {'column': column_name, 'expected': 'integer', 'actual': str(df[column_name].dtype)}
            )
        elif expected_type == 'boolean' and not pd.api.types.is_bool_dtype(df[column_name].dtype):
            result.add_issue(
                'schema', 
                f"Column '{column_name}' should be boolean type",
                'error',
                {'column': column_name, 'expected': 'boolean', 'actual': str(df[column_name].dtype)}
            )
    
    def _check_missing_values(self, 
                             dataset, 
                             result: ValidationResult,
                             schema: Optional[Union[Dict, pa.Schema]],
                             options: Dict[str, Any]) -> None:
        """Check for missing values in the dataset"""
        # Get DataFrame
        if hasattr(dataset, 'to_pandas'):
            df = dataset.to_pandas()
        elif isinstance(dataset, pd.DataFrame):
            df = dataset
        else:
            # Can't check missing values without DataFrame
            return
            
        # Check for missing values
        missing_counts = df.isna().sum()
        missing_columns = missing_counts[missing_counts > 0]
        
        missing_pct_threshold = options.get('missing_threshold', 0.05)  # Default 5%
        
        for column, count in missing_columns.items():
            missing_pct = count / len(df)
            if missing_pct > missing_pct_threshold:
                severity = 'error' if missing_pct > 0.2 else 'warning'
                result.add_issue(
                    'missing_values', 
                    f"Column '{column}' has {count} missing values ({missing_pct:.1%})",
                    severity,
                    {'column': column, 'count': int(count), 'percentage': missing_pct}
                )
    
    def _check_data_types(self, 
                         dataset, 
                         result: ValidationResult,
                         schema: Optional[Union[Dict, pa.Schema]],
                         options: Dict[str, Any]) -> None:
        """Check for appropriate data types"""
        # Get DataFrame
        if hasattr(dataset, 'to_pandas'):
            df = dataset.to_pandas()
        elif isinstance(dataset, pd.DataFrame):
            df = dataset
        else:
            return
        
        # For each column, check for mixed datatypes
        for column in df.columns:
            # Skip columns that are already non-object type
            if not pd.api.types.is_object_dtype(df[column].dtype):
                continue
                
            # See if column contains mixed types
            try:
                type_counts = df[column].map(type).value_counts()
                if len(type_counts) > 1:
                    type_info = {str(t): c for t, c in type_counts.items()}
                    result.add_issue(
                        'data_types', 
                        f"Column '{column}' has mixed types: {type_info}",
                        'warning',
                        {'column': column, 'type_counts': type_info}
                    )
            except Exception:
                # Skip columns that can't be analyzed
                pass
                
    def _check_value_ranges(self, 
                           dataset, 
                           result: ValidationResult,
                           schema: Optional[Union[Dict, pa.Schema]],
                           options: Dict[str, Any]) -> None:
        """Check for appropriate value ranges"""
        # Get DataFrame
        if hasattr(dataset, 'to_pandas'):
            df = dataset.to_pandas()
        elif isinstance(dataset, pd.DataFrame):
            df = dataset
        else:
            return
            
        # For numeric columns, check for outliers
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for column in numeric_cols:
            # Skip columns with too many NaN values
            if df[column].isna().mean() > 0.5:
                continue
                
            try:
                # Use IQR method for outlier detection
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    outlier_pct = outlier_count / len(df)
                    if outlier_pct > 0.05:  # More than 5% outliers
                        result.add_issue(
                            'value_ranges', 
                            f"Column '{column}' has {outlier_count} outliers ({outlier_pct:.1%})",
                            'warning',
                            {
                                'column': column, 
                                'count': outlier_count,
                                'percentage': outlier_pct,
                                'bounds': [float(lower_bound), float(upper_bound)]
                            }
                        )
            except Exception:
                # Skip columns that can't be analyzed
                pass
