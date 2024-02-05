import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd

link = st.text_input('URL')
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

if st.button('Process') and link:
    payload = {}
    headers = {}

    response = requests.request("GET", link, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

        
    list_of_privated_fund_table = [x for x in soup.find_all(attrs={
        'class':'PaperFormTableData'
    }) if "A. PRIVATE FUND" in x.text]
    #CRD Number
    df_dict = {
        'Legal Name':[],
        'CRD Number':[],
        'Fund Name':[],
        'Fund ID':[],	
        'State':[],
        'Country':[],	
        'GP Names':[],
        'Type of Fund':[],
        'Current Gross Asset Value':[],
        'Minimum investment commitment required':[]
    }
    for privated_fund_table in list_of_privated_fund_table:
        Legal_Name = soup.find(attrs={'id':'ctl00_ctl00_cphMainContent_ucADVHeader_lblPrimaryBusinessName'}).text
        CRD_Number = soup.find(attrs={'id':'ctl00_ctl00_cphMainContent_ucADVHeader_lblCrdNumber'}).text
        info = privated_fund_table.find_all('table')[0].find_all('span',attrs={'class':'PrintHistRed'})
        FundName = info[0].text
        Fund_ID = info[1].text
        State_ = [x for x in privated_fund_table.find_all('td') if 'State' in x.text][1].find('span',attrs={'class':'PrintHistRed'})
        State = State_.text if State_ else None
        Country = [x for x in privated_fund_table.find_all('td') if 'Country' in x.text][1].find('span',attrs={'class':'PrintHistRed'}).text
        GPNames = '|'.join([i.text for i in [x for x in privated_fund_table.find_all('table') if 'Name of General Partner, Manager,' in x.text][1].find_all('tr',attrs={'class':'PrintHistRed'})])
        TypeofFund_ = [x for x in privated_fund_table.find_all('td') if 'img' in [y.name for y in x.contents] and 'fund' in x.text][0].contents
        TypeofFund = TypeofFund_[TypeofFund_.index([x for x in TypeofFund_ if "Radio button selected, changed" in str(x)][0])+1].replace('\xa0','')
        CurrentGrossAssetValue = [x for x in privated_fund_table.find_all('td') if 'Current gross asset value of the' in x.text][1].parent.next_sibling.find('span',attrs={'class':'PrintHistRed'}).text[2:]
        MinimumInvestmentCommitment = [x for x in privated_fund_table.find_all('td') if 'Minimum investment commitment required' in x.text][1].parent.next_sibling.find('span',attrs={'class':'PrintHistRed'}).text[2:]

        df_dict['Legal Name'].append(Legal_Name)
        df_dict['CRD Number'].append(CRD_Number)
        df_dict['Fund Name'].append(FundName)
        df_dict['Fund ID'].append(Fund_ID)
        df_dict['State'].append(State)
        df_dict['Country'].append(Country)
        df_dict['GP Names'].append(GPNames)
        df_dict['Type of Fund'].append(TypeofFund)
        df_dict['Current Gross Asset Value'].append(int(CurrentGrossAssetValue.replace(',','')))
        df_dict['Minimum investment commitment required'].append(int(MinimumInvestmentCommitment.replace(',','')))
    
    csv = convert_df(pd.DataFrame(df_dict))

    st.download_button(
    "Press to Download",
    csv,
    "result.csv",
    "text/csv",
    key='download-csv'
    )
