import pandas as pd

def combine_data_sources(source1_path, source2_path, output_path):
    """
    Combines two data sources into a single standardized CSV file.
    """

    # --- Read Source1 ---
    df1 = pd.read_csv(source1_path, sep=',')
    
    # Rename columns in Source1 to our standardized names (where needed).
    # If the columns in Source1 are already named exactly as we want
    # (e.g., 'title', 'description', 'location', etc.), we simply keep them.
    # Otherwise, rename them accordingly.
    df1.rename(columns={
        # 'date': 'some_other_name',            # Not needed in final, so not renamed
        'title': 'title',
        'description': 'description',
        'long_description': 'long_description',
        'branchen': 'branchen',
        'location': 'location'
    }, inplace=True)
    
    # Select only the standardized columns from Source1
    # Some columns (like date, url, standort, etc.) are not needed in the final dataset
    df1 = df1[['title', 'long_description', 'description', 'branchen', 'location']]
    
    # --- Read Source2 ---
    df2 = pd.read_csv(source2_path, sep=',')
    
    # Rename columns in Source2 to our standardized names
    df2.rename(columns={
        'Title': 'title',
        'Beschreibung des Verkaufsangebots': 'long_description',
        'Anforderungen an den Käufer': 'description',
        'Branchen': 'branchen',
        'Region': 'location'
    }, inplace=True)

    # Select only the standardized columns from Source2
    df2 = df2[['title', 'long_description', 'description', 'branchen', 'location']]
    
    # --- Concatenate both DataFrames ---
    df_combined = pd.concat([df1, df2], ignore_index=True)
    
    # --- Save to CSV ---
    df_combined.to_csv(output_path, index=False)
    print(f"Combined data has been saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    combine_data_sources(
        source1_path="./data/nexxt_change_sales_listings.csv",
        source2_path="./data/dub_listings.csv",
        output_path="./data/combined.csv"
    )
