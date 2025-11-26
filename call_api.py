import comtradeapicall
import pandas as pd

pd.set_option('display.max_columns', None)

# reportercode_list =  ['36','699','156','842','276']
reportercode_list =  ['484']
cmdcode_list = ['1211']


country_map = {
    '36': 'Australia',
    '699': 'India',
    '156': 'China',
    '842': 'USA',
    '276': 'Germany',
    '826': 'UK',
    '484': 'Mexico'
}

months = ['202501', '202502', '202503']

for reporterCode1 in reportercode_list:
    county_data = []
    country_name = country_map[reporterCode1]
    print(f"Fetching data for {country_name}...")

    for month in months:
        print(f"\n Running for the month {month}\n")

        for cmdCode1 in cmdcode_list:

            try:

                mydf = comtradeapicall.previewFinalData(typeCode='C', freqCode='M', clCode='HS', period=month,
                                                        reporterCode=reporterCode1, cmdCode=cmdCode1, flowCode='M', partnerCode=None,
                                                        partner2Code=None,
                                                        customsCode=None, motCode=None, maxRecords=500, format_output='JSON',
                                                        aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)


                if not mydf.empty:
                    county_data.append((mydf))
                    print(mydf)
                    print(f"Fetched {len(mydf)} for commodity {cmdCode1} ")
                else:
                    print(f"No data available for commodity {cmdCode1}")
            except Exception as e:
                print(f"Error fetching data for comodity {cmdCode1}.. ")

    # if county_data:
    #     #combined_df = pd.concat(county_data,ignore_index=True)
    #     #filename = f"{country_name}.csv"
    #     #combined_df.to_csv(filename,index=False)
    #     #print(f"Saved {len(combined_df)} records to {filename}\n")
    # else:
    #     print(f"Error fetching the data for Country {country_name}")


# import comtradeapicall
# import pandas as pd
# from datetime import datetime
#
# # Set display options
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', 1000)
#
# # Known parameters with available data (Jan 2023)
# params = {
#     'typeCode': 'C',  # Commodities
#     'freqCode': 'M',  # Monthly data
#     'clCode': 'HS',  # Harmonized System classification
#     'period': '202501',  # January 2023 (known available)
#     'reporterCode': '699',  # India (UN M49 code)
#     'cmdCode': '090121',  # Coffee beans (specific commodity with data)
#     'flowCode': 'M',  # Imports
#     'partnerCode': None,  # Brazil
#     'partner2Code': None,
#     'customsCode': None,
#     'motCode': None,
#     'maxRecords': 100,
#     'format_output': 'JSON',
#     'aggregateBy': None,
#     'breakdownMode': 'classic',
#     'countOnly': None,
#     'includeDesc': True  # Include descriptions
# }
#
# try:
#     # Fetch data from API
#     mydf = comtradeapicall.previewFinalData(**params)
#
#     if mydf.empty:
#         print("No data found. Check parameters or try another period.")
#     else:
#         # Convert USD to INR Crores
#         USD_TO_INR = 83.0  # Update with current exchange rate
#         mydf['value_INR_crores'] = mydf['tradeValue'] * USD_TO_INR / 10_000_000
#
#         # Display key columns
#         print("\nTrade Data Found:")
#         print(mydf[['period', 'reporterDesc', 'partnerDesc',
#                     'flowDesc', 'cmdDesc', 'tradeValue',
#                     'value_INR_crores', 'netWeight', 'unit']])
#
#         # Print latest exchange rate note
#         print(f"\nNote: Values converted to INR crores using exchange rate 1 USD = {USD_TO_INR} INR")
#
# except Exception as e:
#     print(f"API Error: {str(e)}")
#     print("Ensure you have valid API credentials installed for comtradeapicall")


# import requests
#
# url = "https://comtrade.un.org/api/get"
# params = {
#     "max": 500,
#     "type": "C",
#     "freq": "A",
#     "px": "HS",
#     "ps": 2022,
#     "r": 840,   # USA   # China
#     "rg": 1,    # Import
#     "cc": "TOTAL",
#     "fmt": "json"
# }
#
# response = requests.get(url, params=params)
# data = response.json()
#
# print(data)
