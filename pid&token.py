import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
url = 'https://wzxxbg.mofcom.gov.cn/gspt/infoPub/entp/search/wzEntpDetail'
r = requests.post(
    url = url,
    headers = headers ,
    data = {"entpId":"TME-FI-1100600097344-0010","token":"12508E0FEB7BB96CB11BAEEAC39CCD53"}
).json()
dictMerged = dict(r['data']["wzResult"] , **r['data']["investorResult"][0])
df = pd.DataFrame(dictMerged,
                  index=[0],
                  columns =["ENTP_NAME","USC_CODE","RECORDDATEFMT","INDUSTRYNAME","BUSINESS_SCOPE","INVEST_TOTAL","REGISTER_CAPITAL",
                           "RIGHT_MAN","INVESTOR_NAME","COUNTRYNAME","CAPITAL_AMOUNT"])
df.columns = ['企业名称','统一社会信用代码/组织机构代码','成立日期','投资行业','经营范围','投资总额（万元人民币）','注册资本（万元人民币）','法定代表人','投资者名称','国别（地区）','出资金额（万元人民币）']
df.to_csv('test.csv',encoding="utf_8_sig")
print(df)
