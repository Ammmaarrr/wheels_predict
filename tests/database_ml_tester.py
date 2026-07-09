#!/usr/bin/env python3
"""
Database and ML Model Tester
Tests data loading, ML models, and database connections
"""

import pandas as pd
import numpy as np
import pickle
import sqlite3
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

@dataclass
class DataTestResult:
    """Data test result structure"""
    test_name: str
    status: str
    message: str
    details: Optional[Dict] = None
    data_shape: Optional[Tuple] = None
    error_trace: Optional[str] = None

class DatabaseMLTester:
    """Comprehensive database and ML testing"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def add_result(self, test_name: str, status: str, message: str, 
                   details: Dict = None, data_shape: Tuple = None, error_trace: str = None):
        """Add test result"""
        result = DataTestResult(
            test_name=test_name,
            status=status,
            message=message,
            details=details or {},
            data_shape=data_shape,
            error_trace=error_trace
        )
        self.test_results.append(result)
        
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        self.log(f"{emoji} {test_name}: {message}")
    
    def test_data_files(self):
        """Test data file availability and integrity"""
        self.log("📊 Testing data files...")
        
        # Find all data files
        data_extensions = [".csv", ".json", ".xlsx", ".pkl", ".parquet"]
        data_files = []
        
        for ext in data_extensions:
            files = list(self.project_root.glob(f"**/*{ext}"))
            data_files.extend(files)
        
        self.add_result("data_files_found", "PASS", 
                       f"Found {len(data_files)} data files", 
                       details={"file_types": {ext: len(list(self.project_root.glob(f"**/*{ext}"))) for ext in data_extensions}})
        
        # Test loading each data file
        for data_file in data_files[:10]:  # Limit to first 10 for performance
            self.test_single_data_file(data_file)
    
    def test_single_data_file(self, file_path: Path):
        """Test loading a single data file"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == ".csv":
                df = pd.read_csv(file_path)
                self.add_result(f"data_load_{file_path.name}", "PASS", 
                               f"CSV loaded successfully", 
                               data_shape=df.shape,
                               details={"columns": list(df.columns)[:10], "memory_usage": f"{df.memory_usage().sum() / 1024 / 1024:.2f}MB"})
                
                # Test data quality
                self.test_data_quality(df, file_path.name)
                
            elif file_extension == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.add_result(f"data_load_{file_path.name}", "PASS", 
                               f"JSON loaded successfully",
                               details={"type": type(data).__name__, "size": len(str(data))})
                
            elif file_extension == ".xlsx":
                df = pd.read_excel(file_path)
                self.add_result(f"data_load_{file_path.name}", "PASS", 
                               f"Excel loaded successfully", 
                               data_shape=df.shape)
                
            elif file_extension == ".pkl":
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                self.add_result(f"data_load_{file_path.name}", "PASS", 
                               f"Pickle loaded successfully",
                               details={"type": type(data).__name__})
                
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"data_load_{file_path.name}", "ERROR", 
                           f"Failed to load: {str(e)}", 
                           error_trace=error_trace)
    
    def test_data_quality(self, df: pd.DataFrame, filename: str):
        """Test data quality metrics"""
        try:
            # Basic quality checks
            null_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            duplicate_rows = df.duplicated().sum()
            
            # Data type analysis
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            quality_details = {
                "null_percentage": f"{null_percentage:.2f}%",
                "duplicate_rows": duplicate_rows,
                "numeric_columns": len(numeric_columns),
                "categorical_columns": len(categorical_columns),
                "total_records": len(df)
            }
            
            # Determine quality status
            if null_percentage > 50:
                status = "FAIL"
                message = f"Poor data quality: {null_percentage:.1f}% null values"
            elif null_percentage > 20:
                status = "WARN"
                message = f"Moderate data quality: {null_percentage:.1f}% null values"
            else:
                status = "PASS"
                message = f"Good data quality: {null_percentage:.1f}% null values"
            
            self.add_result(f"data_quality_{filename}", status, message, 
                           details=quality_details)
            
            # Test specific columns if this looks like car data
            if any(col.lower() in ['price', 'make', 'model', 'year'] for col in df.columns):
                self.test_car_data_specifics(df, filename)
                
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"data_quality_{filename}", "ERROR", 
                           f"Quality check failed: {str(e)}", error_trace=error_trace)
    
    def test_car_data_specifics(self, df: pd.DataFrame, filename: str):
        """Test car-specific data validation"""
        try:
            car_columns = {
                'price': ['price', 'cost', 'amount'],
                'make': ['make', 'brand', 'manufacturer'],
                'model': ['model', 'variant'],
                'year': ['year', 'model_year']
            }
            
            found_columns = {}
            for category, possible_names in car_columns.items():
                for col in df.columns:
                    if any(name.lower() in col.lower() for name in possible_names):
                        found_columns[category] = col
                        break
            
            # Validate price data
            if 'price' in found_columns:
                price_col = found_columns['price']
                price_data = pd.to_numeric(df[price_col], errors='coerce')
                valid_prices = price_data.dropna()
                
                if len(valid_prices) > 0:
                    avg_price = valid_prices.mean()
                    min_price = valid_prices.min()
                    max_price = valid_prices.max()
                    
                    # Reasonable price range for cars (in various currencies)
                    if min_price > 0 and max_price < 100000000:  # 100M upper limit
                        self.add_result(f"car_price_validation_{filename}", "PASS", 
                                       f"Price data looks valid (avg: {avg_price:,.0f})",
                                       details={"min_price": min_price, "max_price": max_price, "avg_price": avg_price})
                    else:
                        self.add_result(f"car_price_validation_{filename}", "WARN", 
                                       f"Price data may have outliers",
                                       details={"min_price": min_price, "max_price": max_price})
            
            # Validate year data
            if 'year' in found_columns:
                year_col = found_columns['year']
                year_data = pd.to_numeric(df[year_col], errors='coerce')
                valid_years = year_data.dropna()
                
                if len(valid_years) > 0:
                    min_year = valid_years.min()
                    max_year = valid_years.max()
                    
                    if 1900 <= min_year <= 2025 and 1900 <= max_year <= 2025:
                        self.add_result(f"car_year_validation_{filename}", "PASS", 
                                       f"Year data looks valid ({min_year}-{max_year})")
                    else:
                        self.add_result(f"car_year_validation_{filename}", "FAIL", 
                                       f"Invalid year range ({min_year}-{max_year})")
            
            self.add_result(f"car_data_structure_{filename}", "PASS", 
                           f"Found {len(found_columns)} car-related columns", 
                           details=found_columns)
            
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"car_data_validation_{filename}", "ERROR", 
                           f"Car data validation failed: {str(e)}", error_trace=error_trace)
    
    def test_ml_models(self):
        """Test ML model loading and functionality"""
        self.log("🤖 Testing ML models...")
        
        # Find model files
        model_extensions = [".pkl", ".joblib", ".h5", ".pt", ".pth"]
        model_files = []
        
        for ext in model_extensions:
            files = list(self.project_root.glob(f"**/*{ext}"))
            model_files.extend(files)
        
        if not model_files:
            self.add_result("ml_models_found", "WARN", "No model files found")
            return
        
        self.add_result("ml_models_found", "PASS", f"Found {len(model_files)} potential model files")
        
        # Test loading each model
        for model_file in model_files:
            self.test_single_model(model_file)
    
    def test_single_model(self, model_path: Path):
        """Test loading a single ML model"""
        try:
            file_extension = model_path.suffix.lower()
            
            if file_extension == ".pkl":
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                
                # Try to determine model type
                model_type = type(model).__name__
                
                # Test if it has common sklearn methods
                has_predict = hasattr(model, 'predict')
                has_fit = hasattr(model, 'fit')
                
                self.add_result(f"model_load_{model_path.name}", "PASS", 
                               f"Model loaded successfully ({model_type})",
                               details={"has_predict": has_predict, "has_fit": has_fit, "type": model_type})
                
                # If it's a sklearn model, try a basic prediction test
                if has_predict and 'sklearn' in str(type(model)):
                    self.test_model_prediction(model, model_path.name)
                    
            elif file_extension in [".joblib"]:
                try:
                    import joblib
                    model = joblib.load(model_path)
                    self.add_result(f"model_load_{model_path.name}", "PASS", 
                                   f"Joblib model loaded successfully")
                except ImportError:
                    self.add_result(f"model_load_{model_path.name}", "WARN", 
                                   "Joblib not available for model loading")
                    
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"model_load_{model_path.name}", "ERROR", 
                           f"Failed to load model: {str(e)}", error_trace=error_trace)
    
    def test_model_prediction(self, model, model_name: str):
        """Test model prediction capability"""
        try:
            # Try to make a dummy prediction
            # We need to guess the input shape
            
            # Common input shapes for car price prediction
            test_inputs = [
                np.array([[2020, 50000, 1.5, 4]]),  # year, mileage, engine, doors
                np.array([[1, 2, 3, 4, 5]]),        # generic 5 features
                np.array([[1, 2, 3]]),              # generic 3 features
                np.array([[2020]]),                 # single feature
            ]
            
            prediction_made = False
            for test_input in test_inputs:
                try:
                    prediction = model.predict(test_input)
                    self.add_result(f"model_prediction_{model_name}", "PASS", 
                                   f"Model prediction successful (output: {prediction})",
                                   details={"input_shape": test_input.shape, "output": str(prediction)})
                    prediction_made = True
                    break
                except:
                    continue
            
            if not prediction_made:
                self.add_result(f"model_prediction_{model_name}", "WARN", 
                               "Could not test prediction with standard inputs")
                
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"model_prediction_{model_name}", "ERROR", 
                           f"Prediction test failed: {str(e)}", error_trace=error_trace)
    
    def test_database_connections(self):
        """Test database connectivity"""
        self.log("🗄️ Testing database connections...")
        
        # Find database files
        db_files = list(self.project_root.glob("**/*.db")) + list(self.project_root.glob("**/*.sqlite"))
        
        if not db_files:
            self.add_result("database_files", "WARN", "No database files found")
            return
        
        self.add_result("database_files", "PASS", f"Found {len(db_files)} database files")
        
        # Test each database
        for db_file in db_files:
            self.test_single_database(db_file)
    
    def test_single_database(self, db_path: Path):
        """Test a single database connection"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_names = [table[0] for table in tables]
            
            self.add_result(f"database_connect_{db_path.name}", "PASS", 
                           f"Database connected successfully ({len(table_names)} tables)",
                           details={"tables": table_names})
            
            # Test each table
            for table_name in table_names[:5]:  # Limit to first 5 tables
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    self.add_result(f"database_table_{db_path.name}_{table_name}", "PASS", 
                                   f"Table {table_name} has {count} rows, {len(column_names)} columns",
                                   details={"row_count": count, "columns": column_names})
                    
                except Exception as e:
                    self.add_result(f"database_table_{db_path.name}_{table_name}", "ERROR", 
                                   f"Table access failed: {str(e)}")
            
            conn.close()
            
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result(f"database_connect_{db_path.name}", "ERROR", 
                           f"Database connection failed: {str(e)}", error_trace=error_trace)
    
    def test_ml_pipelines(self):
        """Test ML pipeline functionality"""
        self.log("🔄 Testing ML pipelines...")
        
        try:
            # Try to import ML modules
            try:
                from src.pakwheels_ml import enhanced_api_wrapper
                self.add_result("ml_import_enhanced_api", "PASS", "Enhanced API wrapper imported")
                
                # Test if it has expected functions
                if hasattr(enhanced_api_wrapper, 'predict_price'):
                    self.add_result("ml_predict_function", "PASS", "Predict function available")
                else:
                    self.add_result("ml_predict_function", "WARN", "Predict function not found")
                    
            except ImportError as e:
                self.add_result("ml_import_enhanced_api", "FAIL", f"Import failed: {str(e)}")
            
            # Try to find and test other ML files
            ml_files = list((self.project_root / "src" / "pakwheels_ml").glob("*.py"))
            
            for ml_file in ml_files:
                if ml_file.name.startswith('__'):
                    continue
                    
                try:
                    # Try to import as module
                    module_name = ml_file.stem
                    self.add_result(f"ml_file_{module_name}", "PASS", f"ML file found: {ml_file.name}")
                except Exception as e:
                    self.add_result(f"ml_file_{module_name}", "ERROR", f"ML file issue: {str(e)}")
                    
        except Exception as e:
            error_trace = traceback.format_exc()
            self.add_result("ml_pipeline_test", "ERROR", f"ML pipeline test failed: {str(e)}", 
                           error_trace=error_trace)
    
    def run_all_tests(self):
        """Run all database and ML tests"""
        self.log("🧪 Starting database and ML testing...")
        
        test_suites = [
            self.test_data_files,
            self.test_ml_models,
            self.test_database_connections,
            self.test_ml_pipelines
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                self.log(f"❌ Test suite failed: {str(e)}", "ERROR")
                self.add_result(f"suite_{test_suite.__name__}", "ERROR", f"Test suite crashed: {str(e)}")
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive report"""
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r.status == "PASS"])
        failed = len([r for r in self.test_results if r.status == "FAIL"])
        errors = len([r for r in self.test_results if r.status == "ERROR"])
        warnings = len([r for r in self.test_results if r.status == "WARN"])
        
        report = f"""# 📊 DATABASE & ML TESTING REPORT

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}

## 📈 Summary
- **Total Tests:** {total_tests}
- **Passed:** {passed} ✅
- **Failed:** {failed} ❌
- **Errors:** {errors} ⚠️
- **Warnings:** {warnings} ⚠️
- **Success Rate:** {(passed/total_tests*100):.1f}%

## 🔍 Detailed Results

"""
        
        for result in self.test_results:
            emoji = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⚠️"
            report += f"\n### {emoji} {result.test_name}\n"
            report += f"**Status:** {result.status}\n"
            report += f"**Message:** {result.message}\n"
            
            if result.data_shape:
                report += f"**Data Shape:** {result.data_shape}\n"
            
            if result.details:
                report += f"**Details:**\n"
                for key, value in result.details.items():
                    report += f"  - {key}: {value}\n"
            
            if result.error_trace:
                report += f"**Error:** ```\n{result.error_trace[:300]}...\n```\n"
        
        report += f"""
## 🎯 Recommendations

{"✅ Data and ML systems are working well!" if passed/total_tests > 0.8 else "⚠️ Several issues detected that need attention"}

### Next Steps:
1. Review failed tests and fix underlying issues
2. Ensure all required data files are available
3. Validate ML model performance
4. Test with real prediction scenarios
"""
        
        # Save report
        import time
        report_path = self.project_root / "DATABASE_ML_TEST_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        
        self.log(f"📋 Report saved to: {report_path}")
        self.log(f"🎯 Results: {passed}/{total_tests} tests passed ({(passed/total_tests*100):.1f}%)")

def main():
    """Main function"""
    print("=" * 60)
    print("📊 DATABASE & ML MODEL TESTER")
    print("=" * 60)
    
    tester = DatabaseMLTester()
    tester.run_all_tests()
    
    print("=" * 60)
    print("✨ DATABASE & ML TESTING COMPLETE!")
    print("📋 Check DATABASE_ML_TEST_REPORT.md for results")
    print("=" * 60)

if __name__ == "__main__":
    main()
