import pandas as pd
from reference_data import PROJECT_TYPE_REGISTRY_MAP

def vintage_mismatch(df:pd.DataFrame) -> pd.DataFrame:
    """Flag rows where claim_year predates vintage_year."""
    mask = df['claim_year'] < df['vintage_year']
    flagged = df.loc[mask].copy()
    flagged['discrepancy_type'] = 'vintage_mismatch'
    flagged['note'] = flagged.apply(lambda row:
                                    f"Claim year {row['claim_year']} predates vintage year {row['vintage_year']}.", axis = 1 )
    return flagged

def unit_mismatch(df : pd.DataFrame) -> pd.DataFrame:
    """Flag rows where unit is mismatched with gas type."""
    mask = (df['gas_type'] != 'CO2') & (df['unit'] != 'tCO2e')
    flagged = df.loc[mask].copy()
    flagged['discrepancy_type'] = 'unit_mismatch'
    flagged['note'] = flagged.apply(lambda row:
                                    f"Unit {row['unit']} is mismatched with gas type {row['gas_type']}.", axis = 1)
    return flagged

def project_type_mismatch(df : pd.DataFrame) -> pd.DataFrame:
    """Flag rows where project type and registry are mismatched. """
    mask = df.apply(lambda row: row['registry'] not in PROJECT_TYPE_REGISTRY_MAP.get(row['project_type']), axis = 1)
    flagged = df.loc[mask].copy()
    flagged['discrepancy_type'] = 'project_type_registry_mismatch'
    flagged['note'] = flagged.apply(
        lambda row: f"Registry {row['registry']} is invalid for project type {row['project_type']}.", axis = 1)
    return flagged


def double_count(df: pd.DataFrame) -> pd.DataFrame:
    """Flag  rows where serial number of a credit has been claimed more than once."""
    count = df.groupby('serial_number')['claimed_by'].nunique()
    count = count.loc[count > 1]
    mask = df['serial_number'].isin(count.index.to_list())
    flagged = df.loc[mask].copy()
    flagged['discrepancy_type'] = 'double_counted'
    flagged['note'] = flagged.apply(lambda row:
                                    f"Serial number {row['serial_number']} was claimed more than once.", axis = 1)
    return flagged

def double_retired(df : pd.DataFrame) -> pd.DataFrame:
    """Flag rows where serial_number is duplicated and thus credit is double retired."""
    duplicates = df.duplicated(subset = ['serial_number'], keep = False)
    flagged = df.loc[duplicates].copy()
    flagged['discrepancy_type'] = 'double_retired'
    flagged['note'] = flagged.apply(lambda row:
                                    f"Credit {row['serial_number']} is double_retired.", axis = 1
                                    )
    return flagged

def aggregator(df : pd.DataFrame) -> pd.DataFrame:
    """Aggregates all flagged rows into a single flagged data frame."""
    df1 = vintage_mismatch(df)
    df2 = unit_mismatch(df)
    df3 = project_type_mismatch(df)
    df4 = double_count(df)
    df5 = double_retired(df)
    return pd.concat([df1, df2, df3, df4, df5], join = 'outer')




    