import pandas as pd
import os
import re
from datetime import datetime

RAW_DIR = "data/raw"
CLEANED_DIR = "data/cleaned"


def process_price(text):
    """Parse a price string like 'PKR 2,500,000' into an integer."""
    if not isinstance(text, str):
        raise ValueError(f"Invalid price input: {text!r}")
    cleaned = text.upper().replace("PKR", "").replace(",", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse price: {text!r}")


def process_mileage(text):
    """Parse a mileage string like '45,000 km' into an integer."""
    if not isinstance(text, str):
        raise ValueError(f"Invalid mileage input: {text!r}")
    cleaned = text.lower().replace("km", "").replace(",", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse mileage: {text!r}")


def process_engine_capacity(text):
    """Parse an engine capacity string like '1300 cc' into an integer."""
    if not isinstance(text, str):
        raise ValueError(f"Invalid engine capacity input: {text!r}")
    cleaned = text.lower().replace("cc", "").replace(",", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse engine capacity: {text!r}")


# Find the latest raw CSV file
def get_latest_raw_csv():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No raw CSV files found.")
    files.sort(reverse=True)
    return os.path.join(RAW_DIR, files[0])

def clean_data(data, output_path=None):
    """Clean and preprocess raw data.

    Accepts either a file path string or a pandas DataFrame.
    When given a DataFrame, applies column-level cleaning (price, mileage,
    engine_capacity string parsing) and returns the cleaned DataFrame.
    When given a file path, runs the full enhanced feature-extraction pipeline.
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        if "price" in df.columns and df["price"].dtype == object:
            df["price"] = df["price"].apply(process_price)
        if "mileage" in df.columns and df["mileage"].dtype == object:
            df["mileage"] = df["mileage"].apply(process_mileage)
        if "engine_capacity" in df.columns and df["engine_capacity"].dtype == object:
            df["engine_capacity"] = df["engine_capacity"].apply(process_engine_capacity)
        return df

    # Legacy file-path interface
    input_path = data
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Original data shape: {df.shape}")
    
    # Basic cleaning: drop empty columns, drop duplicates, fill NAs
    print("Performing basic cleaning...")
    df = df.dropna(axis=1, how='all')
    df = df.drop_duplicates()
    df = df.fillna("")
    print(f"Data shape after basic cleaning: {df.shape}")
    
    # Apply enhanced feature extraction
    df = apply_enhanced_feature_extraction(df)
    
    # Print extraction summary
    print_extraction_summary(df)
    
    # Save cleaned data
    if output_path:
        print(f"Saving cleaned data to: {output_path}")
        df.to_csv(output_path, index=False)

    # Save a summary report
    summary_path = output_path.replace('.csv', '_summary.txt') if output_path else None
    if not summary_path:
        return df
    with open(summary_path, 'w') as f:
        f.write("Enhanced Feature Extraction Summary\n")
        f.write("="*50 + "\n\n")
        f.write(f"Original data shape: {df.shape}\n")
        f.write(f"Total rows processed: {len(df)}\n\n")
        
        # Write feature extraction results
        if 'extracted_variant' in df.columns:
            f.write("Top 10 Variants:\n")
            f.write(str(df['extracted_variant'].value_counts().head(10)) + "\n\n")
        
        if 'extracted_engine_capacity_cc' in df.columns:
            f.write("Top 10 Engine Capacities:\n")
            f.write(str(df['extracted_engine_capacity_cc'].value_counts().head(10)) + "\n\n")
        
        if 'extracted_transmission_type' in df.columns:
            f.write("Transmission Types:\n")
            f.write(str(df['extracted_transmission_type'].value_counts()) + "\n\n")
        
        if 'extracted_location' in df.columns:
            f.write("Top 10 Locations:\n")
            f.write(str(df['extracted_location'].value_counts().head(10)) + "\n\n")
        
        if 'extracted_body_type' in df.columns:
            f.write("Body Type Distribution:\n")
            f.write(str(df['extracted_body_type'].value_counts()) + "\n\n")
    
    print(f"Summary report saved to: {summary_path}")
    return df

# Enhanced Feature Extraction Functions

def extract_variant(text):
    """Extract variant from text description or name."""
    if isinstance(text, str):
        text = text.lower()
        
        # First, try to extract variant with year pattern (like "z 2020", "vxr 2007")
        variant_year_match = re.search(r'\b([a-z]{1,5})\s+(19[8-9]\d|20[0-2]\d)\b', text)
        if variant_year_match:
            variant = variant_year_match.group(1).strip()
            # Common variants in Pakistan
            if variant in ['z', 'vxr', 'gli', 'xli', 'vti', 'vtis', 'oriel', 'grande', 'vx', 'lx', 'ex', 'sx', 'dx']:
                return variant
        
        # Extract variant after make/model pattern
        match_after_model = re.search(r'(?:toyota|honda|suzuki|nissan|kia|hyundai|changan|mg|dfsk|proton|audi|bmw|mercedes-benz|prince)\s+\w+\s+(.*?)\s+(?:for sale in|in|used for sale)', text)
        if match_after_model:
            potential_variant = match_after_model.group(1).strip()
            # Remove year if present and get the variant
            potential_variant = re.sub(r'\b(19[8-9]\d|20[0-2]\d)\b', '', potential_variant).strip()
            # Basic filtering to remove common words
            if potential_variant and len(potential_variant) > 1 and potential_variant not in ['used', 'for', 'sale', 'in', 'the', 'car', 'hybrid']:
                return potential_variant

        # Look for common Pakistani car variants
        variant_patterns = [
            r'\b(gli|xli|vti|vtis|vxr|oriel|grande|altis|vx|lx|ex|sx|dx|z|s|rs|si|type\s*r)\b',
            r'\b(euro\s*ii|euro\s*iii|euro\s*iv|euro\s*v)\b',
            r'\b(cvt|i-vtec|vtec|turbo|hybrid)\b'
        ]
        
        for pattern in variant_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        # Fallback to the previous simple logic
        match_basic = re.search(r'(\b\w+\b)\s+(for sale in)', text)
        if match_basic:
            potential_variant_basic = match_basic.group(1).strip()
            if potential_variant_basic and len(potential_variant_basic) > 1 and potential_variant_basic not in ['used', 'for', 'sale', 'in', 'the', 'car', 'hybrid']:
                return potential_variant_basic

    return 'unknown'

def extract_engine_capacity_cc(text):
    """Extract engine capacity (CC) from text."""
    if isinstance(text, str):
        text = text.lower().replace(',', '').replace(' ', '')
        
        # Look for L (liter) format and convert to CC
        liter_match = re.search(r'(\d+(?:\.\d+)?)\s*l\b', text)
        if liter_match:
            try:
                liters = float(liter_match.group(1))
                return int(liters * 1000)  # Convert liters to CC
            except ValueError:
                pass
        
        # Look for numbers followed by 'cc'
        cc_match = re.search(r'(\d+)\s*cc', text)
        if cc_match:
            try:
                return int(cc_match.group(1))
            except ValueError:
                pass
        
        # Look for common engine sizes in Pakistan (fallback)
        common_engines = {
            'alto': 660, 'mehran': 796, 'cultus': 1000, 'wagon r': 1000,
            'corolla': 1300, 'civic': 1800, 'city': 1300, 'vitz': 1000,
            'aqua': 1500, 'prius': 1800, 'camry': 2400
        }
        
        for model, cc in common_engines.items():
            if model in text:
                return cc
                
    return None

def extract_transmission_type(text):
    """Extract transmission type from text."""
    if isinstance(text, str):
        text = text.lower()
        
        # Handle AT = Automatic Transmission
        if re.search(r'\bat\b', text):
            return 'automatic'
        
        # Handle MT = Manual Transmission
        if re.search(r'\bmt\b', text):
            return 'manual'
        
        # Standard patterns
        if re.search(r'\bauto\b|\bautomatic\b|\bcvt\b', text):
            return 'automatic'
        elif re.search(r'\bmanual\b', text):
            return 'manual'
            
    return 'unknown'

def extract_make_model(text):
    """Extract make and model from text."""
    if isinstance(text, str):
        text = text.lower().strip()
        # Common car makes in Pakistan
        makes = ['toyota', 'honda', 'suzuki', 'nissan', 'kia', 'hyundai', 'changan', 'mg', 'dfsk', 'proton', 'audi', 'bmw', 'mercedes-benz', 'prince', 'daihatsu', 'mitsubishi', 'peugeot', 'chevrolet', 'ford', 'volkswagen']
        
        for make in makes:
            if make in text:
                # Extract model after make
                pattern = rf'{make}\s+(\w+)'
                match = re.search(pattern, text)
                if match:
                    model = match.group(1)
                    return make.title(), model.title()
        
        # If no make found, try to extract first two words
        words = text.split()
        if len(words) >= 2:
            return words[0].title(), words[1].title()
    
    return 'Unknown', 'Unknown'

def extract_year(text):
    """Extract year from text."""
    if isinstance(text, str):
        # Look for 4-digit years between 1980-2025
        match = re.search(r'\b(19[8-9]\d|20[0-2]\d)\b', text)
        if match:
            try:
                year = int(match.group(1))
                if 1980 <= year <= 2025:
                    return year
            except ValueError:
                pass
    return None

def extract_price(text):
    """Extract price from text."""
    if isinstance(text, str):
        text = text.lower().replace(',', '').replace('rs', '').replace('pkr', '')
        # Look for numbers followed by lakh or crore
        match_lakh = re.search(r'(\d+(?:\.\d+)?)\s*lakh', text)
        if match_lakh:
            try:
                return float(match_lakh.group(1)) * 100000
            except ValueError:
                pass
        
        match_crore = re.search(r'(\d+(?:\.\d+)?)\s*crore', text)
        if match_crore:
            try:
                return float(match_crore.group(1)) * 10000000
            except ValueError:
                pass
        
        # Look for plain numbers (assuming they're already in correct format)
        match_plain = re.search(r'(\d+(?:\.\d+)?)', text)
        if match_plain:
            try:
                price = float(match_plain.group(1))
                # If price is too small, assume it's in lakhs
                if price < 1000:
                    return price * 100000
                return price
            except ValueError:
                pass
    return None

def extract_location(text):
    """Extract location/city from text."""
    if isinstance(text, str):
        text = text.lower()
        
        # Look for "for sale in [location]" pattern
        location_match = re.search(r'for sale in\s+([a-zA-Z\s]+)', text)
        if location_match:
            location = location_match.group(1).strip()
            # Clean up common suffixes
            location = re.sub(r'\s+(pakistan|pk|city)$', '', location)
            return location.title()
        
        # Look for "in [location]" pattern
        in_match = re.search(r'\sin\s+([a-zA-Z\s]+?)(?:\s|$)', text)
        if in_match:
            location = in_match.group(1).strip()
            # Common Pakistani cities
            pak_cities = ['karachi', 'lahore', 'islamabad', 'rawalpindi', 'faisalabad', 
                         'multan', 'peshawar', 'quetta', 'sialkot', 'gujranwala', 
                         'hyderabad', 'attock', 'bahawalpur', 'sargodha', 'sukkur']
            
            if location.lower() in pak_cities:
                return location.title()
    
    return 'unknown'

def extract_body_type(text):
    """Extract body type from text."""
    if isinstance(text, str):
        text = text.lower()
        
        # Define body type patterns
        body_types = {
            'sedan': r'\b(sedan|saloon)\b',
            'suv': r'\b(suv|sport utility|crossover)\b',
            'hatchback': r'\b(hatchback|hatch)\b',
            'coupe': r'\b(coupe|coup)\b',
            'convertible': r'\b(convertible|cabriolet)\b',
            'wagon': r'\b(wagon|estate|touring)\b',
            'pickup': r'\b(pickup|truck)\b',
            'van': r'\b(van|minivan)\b',
            'jeep': r'\b(jeep|4x4|4wd)\b'
        }
        
        for body_type, pattern in body_types.items():
            if re.search(pattern, text):
                return body_type
        
        # Common model-based body type identification
        model_body_types = {
            'corolla': 'sedan', 'civic': 'sedan', 'city': 'sedan', 'camry': 'sedan',
            'vitz': 'hatchback', 'aqua': 'hatchback', 'cultus': 'hatchback', 'alto': 'hatchback',
            'prado': 'suv', 'fortuner': 'suv', 'tucson': 'suv', 'sportage': 'suv',
            'van': 'van', 'hiace': 'van', 'bolan': 'van'
        }
        
        for model, body_type in model_body_types.items():
            if model in text:
                return body_type
    
    return 'unknown'

def apply_enhanced_feature_extraction(df):
    """Apply enhanced feature extraction to the dataframe."""
    print("Applying enhanced feature extraction...")
    
    # Create copies of original columns if they don't exist
    if 'description' not in df.columns:
        df['description'] = df.get('name', '')
    if 'name' not in df.columns:
        df['name'] = df.get('description', '')
    
    # Extract variant
    print("Extracting variants...")
    df['extracted_variant'] = df['description'].apply(extract_variant)
    # If variant is unknown from description, try name
    unknown_variant_mask = df['extracted_variant'] == 'unknown'
    if unknown_variant_mask.any():
        df.loc[unknown_variant_mask, 'extracted_variant'] = df.loc[unknown_variant_mask, 'name'].apply(extract_variant)
    
    # Extract engine capacity
    print("Extracting engine capacity...")
    df['extracted_engine_capacity_cc'] = df['description'].apply(extract_engine_capacity_cc)
    # If engine capacity is None from description, try name
    none_engine_mask = df['extracted_engine_capacity_cc'].isnull()
    if none_engine_mask.any():
        df.loc[none_engine_mask, 'extracted_engine_capacity_cc'] = df.loc[none_engine_mask, 'name'].apply(extract_engine_capacity_cc)
    
    # Extract transmission type
    print("Extracting transmission type...")
    df['extracted_transmission_type'] = df['description'].apply(extract_transmission_type)
    # If transmission is unknown from description, try name
    unknown_transmission_mask = df['extracted_transmission_type'] == 'unknown'
    if unknown_transmission_mask.any():
        df.loc[unknown_transmission_mask, 'extracted_transmission_type'] = df.loc[unknown_transmission_mask, 'name'].apply(extract_transmission_type)
    
    # Extract make and model if not already present
    print("Extracting make and model...")
    if 'make' not in df.columns or 'model' not in df.columns:
        extracted_make_model = df['name'].apply(extract_make_model)
        df['extracted_make'] = extracted_make_model.apply(lambda x: x[0])
        df['extracted_model'] = extracted_make_model.apply(lambda x: x[1])
    
    # Extract year if not already present
    print("Extracting year...")
    if 'year' not in df.columns:
        df['extracted_year'] = df['description'].apply(extract_year)
        # If year is None from description, try name
        none_year_mask = df['extracted_year'].isnull()
        if none_year_mask.any():
            df.loc[none_year_mask, 'extracted_year'] = df.loc[none_year_mask, 'name'].apply(extract_year)
    
    # Extract price if not already present
    print("Extracting price...")
    if 'price' not in df.columns:
        df['extracted_price'] = df['description'].apply(extract_price)
        # If price is None from description, try name
        none_price_mask = df['extracted_price'].isnull()
        if none_price_mask.any():
            df.loc[none_price_mask, 'extracted_price'] = df.loc[none_price_mask, 'name'].apply(extract_price)
    
    # Extract location if not already present
    print("Extracting location...")
    if 'location' not in df.columns:
        df['extracted_location'] = df['description'].apply(extract_location)
        # If location is unknown from description, try name
        unknown_location_mask = df['extracted_location'] == 'unknown'
        if unknown_location_mask.any():
            df.loc[unknown_location_mask, 'extracted_location'] = df.loc[unknown_location_mask, 'name'].apply(extract_location)
    
    # Extract body type if not already present
    print("Extracting body type...")
    if 'body_type' not in df.columns:
        df['extracted_body_type'] = df['description'].apply(extract_body_type)
        # If body type is unknown from description, try name
        unknown_body_type_mask = df['extracted_body_type'] == 'unknown'
        if unknown_body_type_mask.any():
            df.loc[unknown_body_type_mask, 'extracted_body_type'] = df.loc[unknown_body_type_mask, 'name'].apply(extract_body_type)
    
    return df

def print_extraction_summary(df):
    """Print summary of extracted features."""
    print("\n" + "="*60)
    print("ENHANCED FEATURE EXTRACTION SUMMARY")
    print("="*60)
    
    if 'extracted_variant' in df.columns:
        print(f"\nTop 10 Extracted Variants:")
        print(df['extracted_variant'].value_counts().head(10))
    
    if 'extracted_engine_capacity_cc' in df.columns:
        print(f"\nTop 10 Engine Capacities (CC):")
        print(df['extracted_engine_capacity_cc'].value_counts().head(10))
    
    if 'extracted_transmission_type' in df.columns:
        print(f"\nTransmission Types:")
        print(df['extracted_transmission_type'].value_counts())
    
    if 'extracted_make' in df.columns:
        print(f"\nTop 10 Makes:")
        print(df['extracted_make'].value_counts().head(10))
    
    if 'extracted_model' in df.columns:
        print(f"\nTop 10 Models:")
        print(df['extracted_model'].value_counts().head(10))
    
    if 'extracted_year' in df.columns:
        print(f"\nYear Distribution:")
        print(df['extracted_year'].value_counts().sort_index().tail(10))
    
    if 'extracted_location' in df.columns:
        print(f"\nTop 10 Locations:")
        print(df['extracted_location'].value_counts().head(10))
    
    if 'extracted_body_type' in df.columns:
        print(f"\nBody Type Distribution:")
        print(df['extracted_body_type'].value_counts())
    
    # Data quality metrics
    print(f"\n" + "="*60)
    print("DATA QUALITY METRICS")
    print("="*60)
    
    total_rows = len(df)
    
    if 'extracted_variant' in df.columns:
        unknown_variants = (df['extracted_variant'] == 'unknown').sum()
        print(f"Unknown variants: {unknown_variants}/{total_rows} ({unknown_variants/total_rows*100:.1f}%)")
    
    if 'extracted_engine_capacity_cc' in df.columns:
        missing_engine = df['extracted_engine_capacity_cc'].isnull().sum()
        print(f"Missing engine capacity: {missing_engine}/{total_rows} ({missing_engine/total_rows*100:.1f}%)")
    
    if 'extracted_transmission_type' in df.columns:
        unknown_transmission = (df['extracted_transmission_type'] == 'unknown').sum()
        print(f"Unknown transmission: {unknown_transmission}/{total_rows} ({unknown_transmission/total_rows*100:.1f}%)")
    
    if 'extracted_location' in df.columns:
        unknown_location = (df['extracted_location'] == 'unknown').sum()
        print(f"Unknown location: {unknown_location}/{total_rows} ({unknown_location/total_rows*100:.1f}%)")
    
    if 'extracted_body_type' in df.columns:
        unknown_body_type = (df['extracted_body_type'] == 'unknown').sum()
        print(f"Unknown body type: {unknown_body_type}/{total_rows} ({unknown_body_type/total_rows*100:.1f}%)")
    
    print("="*60)

RAW_DIR = "data/raw"
CLEANED_DIR = "data/cleaned"

if __name__ == "__main__":
    print("Starting Enhanced Data Cleaning and Preprocessing...")
    print("="*60)
    
    # Create output directory
    os.makedirs(CLEANED_DIR, exist_ok=True)
    
    # Get latest raw data
    try:
        latest_raw = get_latest_raw_csv()
        print(f"Processing file: {latest_raw}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure you have raw CSV files in the 'data/raw' directory.")
        exit(1)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    cleaned_filename = f"cleaned_enhanced_{timestamp}.csv"
    cleaned_path = os.path.join(CLEANED_DIR, cleaned_filename)
    
    # Process the data
    try:
        df_cleaned = clean_data(latest_raw, cleaned_path)
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"✅ Cleaned data saved to: {cleaned_path}")
        print(f"✅ Total rows processed: {len(df_cleaned)}")
        print(f"✅ Enhanced features extracted successfully!")
        print(f"{'='*60}")
        
        # Show column summary
        print("\nFinal DataFrame Columns:")
        for i, col in enumerate(df_cleaned.columns, 1):
            print(f"{i:2d}. {col}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        print("Please check your data and try again.")
        exit(1)
