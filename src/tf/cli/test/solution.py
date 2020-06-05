import pandas as pd

def build_dataframe(resource):
    sales = pd.read_csv(resource)
    #s = pd.DataFrame({})
    #s = pd.DataFrame({})
    sales.rename(columns=lambda x: x.replace(' ', ''), inplace=True)
    return sales

def total_sales(df):
  # add up total spending
  ans = df['Total'].sum()
  return ans 

def pam_sales(df):
    is_pam = df['SalesPerson'] == 'Pam'
    return df[is_pam]['Total'].sum()


def andy_bond_sales(df): 
    is_andy = df['SalesPerson'] == 'Andy'
    is_paper = df['Product'].isin(['Bond-20', 'Bond-50'])
    mask = is_andy & is_paper
    #print(df[mask])
    return df[mask]['Total'].sum()/12.

def worst_zip(df):
    # reset_index turns the Series into DataFrame
    return df.groupby(['Zip'])['Total'].sum().nsmallest(1).reset_index()


URL = 'https://raw.githubusercontent.com/NSF-EC/INFO490Assets/master/src/datasets/dunder/dm101s.csv'
df = build_dataframe(URL)
#worst_zip(df)
