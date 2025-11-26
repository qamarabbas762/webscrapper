import comtradeapicall
import pandas as pd

# 2100 - Sea
# 2200 - Inland waterways
# 1000 - Air
# 9000 - pipelines, cables
# 9900 - others
# 9300 - self propelled
# 9200 - Potal consignment
#  0   - Total MOT
# 3200  - Road
# 3100  - Railway

pd.set_option('display.max_columns', None)

mydf = comtradeapicall.previewFinalData(typeCode='C', freqCode='M', clCode='HS', period=202501,
                                                        reporterCode=276, cmdCode=8419, flowCode='M', partnerCode=None,
                                                        partner2Code=None,
                                                        customsCode=None, motCode=None, maxRecords=500, format_output='JSON',
                                                        aggregateBy='customscode,motcode', breakdownMode='plus', countOnly=None, includeDesc=True)

print(f"Length of the data is {len(mydf)}")
print(mydf)
