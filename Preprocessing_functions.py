def make_capacity_by_country(active_df, method_name):
    """
    Given an ‘operating’ DataFrame with columns Region, Country, and Capacity (MW),
    group by Region & Country, sum Capacity, and rename to <method_name>_capacity.
    """
    cap_col = f"{method_name}_capacity"
    return (
        active_df
        .groupby(['Region', 'Country'], as_index=False)['Capacity (MW)']
        .sum()
        .rename(columns={'Capacity (MW)': cap_col})
    )

def split_owner(owner_str):
    """
    Given an owner string like:
    - "Örsted [10%]; Felvig [90%]"  OR
    - "Owner1; Owner2" 
    returns a list of tuples (owner_name, fraction).
    
    If no percentages are provided for multiple owners, each is assigned an equal share.
    If some owners lack percentages while others have them, the remaining percentage is equally
    distributed among those missing percentages.
    """
    if not isinstance(owner_str, str):
        return [("Unknown", 1.0)]


    # Split the string by semicolon to handle multiple owners
    parts = [part.strip() for part in owner_str.split(';')]
    
    # Check if any part contains a percentage
    has_percentage = any('[' in part and ']' in part for part in parts)
    
    result = []
    
    if not has_percentage:
        # No percentages provided: assign equal share to each Country.
        equal_share = 1.0 / len(parts)
        for part in parts:
            # Clean the owner name in case any extraneous text exists
            name = part.split('[')[0].strip()
            result.append((name, equal_share))
    else:
        # Process each part: extract percentage if available.
        for part in parts:
            if '[' in part and ']' in part:
                name = part.split('[')[0].strip()
                percentage_str = part.split('[')[1].split(']')[0].strip().replace('%', '')
                try:
                    percentage = float(percentage_str) / 100.0
                except ValueError:
                    percentage = None
                result.append((name, percentage))
            else:
                # Part without a percentage: mark fraction as None for now.
                result.append((part, None))
        
        # For parts that are missing percentages, assign an equal share of the remaining capacity.
        total_assigned = sum(p for _, p in result if p is not None)
        missing_count = sum(1 for _, p in result if p is None)
        if missing_count > 0:
            remaining = max(0, 1.0 - total_assigned)  # Avoid negative
            missing_share = remaining / missing_count
            result = [(name, p if p is not None else missing_share) for name, p in result]
    
    return result

# Assume merged_bio is your DataFrame containing the "Owner" and "Capacity (MW)" columns.
# For example, if reading from CSV:
# merged_bio = pd.read_csv("Bioenergy_merged.csv")


