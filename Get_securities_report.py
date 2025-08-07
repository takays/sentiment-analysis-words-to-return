# [General Comment at the top of the file]
# This script downloads Japanese securities reports (Yukashoken Hokokusho) from the EDINET API.
# It then extracts specific text sections from the downloaded XBRL data and compiles them into a single CSV file.
# EDINET is the official electronic disclosure system for Japanese companies.
# %%
import requests
import datetime
import pandas as pd
import time
import os

# %%
# set up years
Syear = 2024
Eyear = 2024
start_date = datetime.date(Syear, 3, 1)
end_date = datetime.date(Eyear, 3,31)
ipath = f'./{Syear}'
os.makedirs(ipath,exist_ok=True)

# API parameter
params = {
  "type" : 5
}
YOUR_SUBSCRIPTION_KEY = 'YOUR_SUBSCRIPTION_KEY'
Form_code = "030000"

# %%
# get date
def create_day_list(start_date=start_date, end_date = end_date):
    period = end_date - start_date
    period = int(period.days)
    day_list = []
    for d in range(period):
        day = start_date + datetime.timedelta(days=d)
        day_list.append(day)

    day_list.append(end_date)

    return day_list

day_list = create_day_list()

# %%
# get docID
def create_report_list(day_list):

    report_list =[]
    for day in day_list:
        url = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
        
        params = {"date": day, "type": 2, "Subscription-Key":YOUR_SUBSCRIPTION_KEY}
        res = requests.get(url, params=params)
        json_data = res.json()
        time.sleep(3)

        for num in range(len(json_data["results"])):
            ordinance_code= json_data["results"][num]["ordinanceCode"]
            form_code= json_data["results"][num]["formCode"]

            if ordinance_code == "010" and  form_code ==f'{Form_code}' :
                company_name=json_data["results"][num]["filerName"]
                edi={'会社名':company_name,    # Key:'Company Name'
                            '書類名':json_data["results"][num]["docDescription"],    # Key:'Document Name'
                            'docID':json_data["results"][num]["docID"],
                            '証券コード':json_data["results"][num]["secCode"],       # Key:'Security Code'
                            'ＥＤＩＮＥＴコード':json_data["results"][num]["edinetCode"],    # Key:'EDINET Code'
                            '決算期':json_data["results"][num]["periodEnd"],         # Key:'Fiscal Period End'
                            '提出日': day}     # Key:'Submission Date'
                report_list.append(edi)

    return report_list

report_list = create_report_list(day_list)
list_df = pd.DataFrame(report_list)
df = list_df.copy()
df = df[df['証券コード'].notnull()]    # 'Security Code'

# make Securities report directory
securities_report_dir = ipath
if not os.path.exists(securities_report_dir):
    os.makedirs(securities_report_dir)

for index, row in df.iterrows():
    edinet_code = row['docID']
    security_code = row['証券コード']  # 'Security Code'
    directory = os.path.join(securities_report_dir, str(security_code))

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = os.path.join(directory, f"{security_code}.zip")
    url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{edinet_code}?Subscription-Key={YOUR_SUBSCRIPTION_KEY}&type=5"

extracted_data = []

search_dir = './'

output_file = search_dir + 'extracted_data.csv'

csv_files = glob.glob(f"{search_dir}/**/XBRL_TO_CSV/jpcrp*", recursive=True)
def extract_text_block(df, column_name):
    row = df[df['項目名'] == column_name]    # 'column_name'
    return row.iloc[0]['値'] if not row.empty else None    # 'value'

def extract_text_block_element(df, column_name):
    row = df[df['要素ID'] == column_name]    # 'column_name'
    return row.iloc[0]['値'] if not row.empty else None    # 'value'

for csv_file in csv_files:
    try:
        df = pd.read_table(csv_file, encoding="utf-16", on_bad_lines='skip')
        ticker = os.path.basename(os.path.dirname(os.path.dirname(csv_file)))
        reporting_date = extract_text_block(df, "提出日、表紙")    # Item Name:'Submission Date, Cover Page'
        firm_name = extract_text_block(df, "会社名、表紙")         # Item Name:'Company Name, Cover Page'
        
        closing_date = extract_text_block(df, "当会計期間終了日、DEI")     # Item Name:'Current Fiscal Period End Date, DEI'
        Business_content = extract_text_block(df, "事業の内容 [テキストブロック]")    # Item Name:'Description of Business [Text Block]'
        management_policy = extract_text_block(df, "経営方針、経営環境及び対処すべき課題等 [テキストブロック]") or extract_text_block(df, "対処すべき課題 [テキストブロック]")    # Item Names:'Business Policy, Business Environment, and Issues to be Addressed [Text Block]' or 'Issues to be Addressed [Text Block]'
        business_risks = extract_text_block(df, "事業等のリスク [テキストブロック]")    # Item Name:'Business Risks [Text Block]'
        financial_condition = extract_text_block(df, "経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析 [テキストブロック]") or extract_text_block(df, "財政状態、経営成績及びキャッシュ・フローの状況の分析 [テキストブロック]") or extract_text_block_element(df, "jpcrp030000-asr_E00012-000:ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")    # Item Names:'Management’s Discussion and Analysis of Financial Position, Operating Results, and Cash Flows [Text Block]' or 'Analysis of Financial Position, Operating Results, and Cash Flows [Text Block]'
        performance_summary = extract_text_block(df, "業績等の概要 [テキストブロック]")    # Item Name:'Overview of Business Results [Text Block]'
        important_contracts = extract_text_block(df, "経営上の重要な契約等 [テキストブロック]") or extract_text_block(df, "経営上の重要な契約等（該当なし） [テキストブロック]")    # Item Names:'Material Contracts for Operation [Text Block]' or 'Material Contracts for Operation (Not Applicable) [Text Block]'
        Production_and_sales = extract_text_block(df, "生産、受注及び販売の状況 [テキストブロック]")    # Item Name:'Production, Orders, and Sales Status [Text Block]'
        research_development = extract_text_block(df, "研究開発活動 [テキストブロック]")    # Item Name:'Research and Development Activities [Text Block]'
        extracted_data.append([firm_name, ticker, reporting_date, closing_date, Business_content, management_policy, business_risks, financial_condition, performance_summary, important_contracts, Production_and_sales, research_development])
    except Exception as e:
        print(f"ファイル {csv_file} の処理中にエラーが発生しました: {e}")    # Print statement:'An error occurred while processing the file: {e}'

# Column names for the output CSV file.
columns = ['name', 'ticker', 'reporting_date', 'acc', '事業の内容', '経営方針、経営環境及び対処すべき課題', '事業等のリスク', '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析', '業績等の概要', '経営上の重要な契約', '生産、受注及び販売の状況', '研究開発活動']
# Japanese Columns Translation:
# '事業の内容':'Description of Business'
# '経営方針、経営環境及び対処すべき課題':'Business Policy, Business Environment, and Issues to be Addressed'
# '事業等のリスク':'Business Risks'
# '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析':'Management’s Discussion and Analysis of Financial Position, Operating Results, and Cash Flows'
# '業績等の概要':'Overview of Business Results'
# '経営上の重要な契約':'Material Contracts for Operation'
# '生産、受注及び販売の状況':'Production, Orders, and Sales Status'
# '研究開発活動':'Research and Development Activities'
output_df = pd.DataFrame(extracted_data, columns=columns)
output_df = output_df.sort_values(['ticker', 'reporting_date'])
output_df.to_csv(output_file, index=False, encoding='utf-8')
#output_df.to_csv('xx1301.csv', index=False, encoding='utf-8')

years = range(2010, 2025) 

csv_files = []
for year in years:
    csv_files.extend(glob.glob(f"{search_dir}{year}/**/XBRL_TO_CSV/jpcrp030000-asr-001_*.csv", recursive=True))

print(f"Number of CSV files found: {len(csv_files)}")
for file in csv_files:
    print(file)

def parse_and_clean_text(text):
    if isinstance(text, str):
        text = re.sub('\s', '', text)
        text = re.sub('<.*?>', '', text)
    return text

def erement_text(df, column_name):
    row = df[df['要素ID'].str.contains(column_name, na=False)]
    return row.iloc[0]['値'] if not row.empty else None

extracted_data = []

for csv_file in csv_files:
#for csv_file in xxcsv_files:
    try:
        df = pd.read_table(csv_file, encoding="utf-16", on_bad_lines='skip')
        
        company_name = erement_text(df, "CompanyNameCoverPage")
        company_name = parse_and_clean_text(company_name) if company_name else np.nan

        ticker = erement_text(df, 'jpdei_cor:SecurityCodeDEI')
        ticker = parse_and_clean_text(ticker) if ticker else np.nan

        reporting_date = erement_text(df, "FilingDateCoverPage")
        reporting_date = parse_and_clean_text(reporting_date) if reporting_date else np.nan

        closing_date = erement_text(df, "jpdei_cor:CurrentPeriodEndDateDEI")
        closing_date = parse_and_clean_text(closing_date) if closing_date else np.nan

        management_policy = erement_text(df, "BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock")
        if not management_policy:
            management_policy = erement_text(df, "IssuesToAddressTextBlock")
        management_policy = parse_and_clean_text(management_policy) if management_policy else np.nan

        business_risks = erement_text(df, "BusinessRisksTextBlock")
        business_risks = parse_and_clean_text(business_risks) if business_risks else np.nan

        financial_condition = erement_text(df, "ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")
        if not financial_condition:
            financial_condition = erement_text(df, "AnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")
        if not financial_condition:
            financial_condition = erement_text(df, "AnalysisAndResponsesToSignificantEventsRelatedToGoingConcernRisksEtcTextBlock")
        financial_condition = parse_and_clean_text(financial_condition) if financial_condition else np.nan

        Production_order_and_sales_status = erement_text(df, "OverviewOfProductionOrdersReceivedAndSalesTextBlock")
        Production_order_and_sales_status = parse_and_clean_text(Production_order_and_sales_status) if Production_order_and_sales_status else np.nan

        performance_summary = erement_text(df, "OverviewOfBusinessResultsTextBlock")
        performance_summary = parse_and_clean_text(performance_summary) if performance_summary else np.nan

        important_contracts = erement_text(df, "CriticalContractsForOperationNATextBlock")
        if not important_contracts:
            important_contracts = erement_text(df, "CriticalContractsForOperationTextBlock")
        important_contracts = parse_and_clean_text(important_contracts) if important_contracts else np.nan

        research_development = erement_text(df, "ResearchAndDevelopmentActivitiesTextBlock")
        if not research_development:
            research_development = erement_text(df, "ResearchAndDevelopmentActivitiesNATextBlock")
        research_development = parse_and_clean_text(research_development) if research_development else np.nan

        PolicyOnHuman = erement_text(df, 'DisclosureOfSustainabilityRelatedFinancialInformationTextBlock')
        PolicyOnHuman = parse_and_clean_text(PolicyOnHuman) if PolicyOnHuman else np.nan

        PolicyOnHuman_target = erement_text(df, 'DescriptionOfMetricsRelatedToPolicyOnHumanResourceDevelopmentAndImprovementOfInternalEnvironmentAndTargetsAndResultsUsingSuchMetricsMetricsAndTargetsTextBlock')
        if not PolicyOnHuman_target:
            PolicyOnHuman_target = erement_text(df, "PolicyOnDevelopmentOfHumanResourcesAndInternalEnvironmentStrategyTextBlock")
        PolicyOnHuman_target = parse_and_clean_text(PolicyOnHuman_target) if PolicyOnHuman_target else np.nan

        CorporateGovernance = erement_text(df, "ExplanationAboutCorporateGovernanceTextBlock")
        if not CorporateGovernance:
            CorporateGovernance = erement_text(df, "OverviewOfCorporateGovernanceTextBlock")
        CorporateGovernance = parse_and_clean_text(CorporateGovernance) if CorporateGovernance else np.nan

        extracted_data.append([company_name, ticker, reporting_date, closing_date, management_policy, business_risks, financial_condition, Production_order_and_sales_status, performance_summary, important_contracts, research_development, PolicyOnHuman, PolicyOnHuman_target, CorporateGovernance])

# Column names for the final output CSV file.
columns = ['name', 'ticker', '報告日', '決算日', '経営方針、経営環境及び対処すべき課題', '事業等のリスク', '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析', '生産、受注及び販売の状況', '業績等の概要', '経営上の重要な契約', '研究開発活動', 'サステナビリティに関する考え方及び取組', '人的資本目標', 'コーポレート・ガバナンス']
# Japanese Columns Translation:
# '報告日':'Reporting Date'
# '決算日': 'Closing Date'
# '経営方針、経営環境及び対処すべき課題':'Business Policy, Business Environment, and Issues to be Addressed'
# '事業等のリスク':'Business Risks'
# '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析':'Management’s Discussion and Analysis of Financial Position, Operating Results, and Cash Flows'
# '生産、受注及び販売の状況':'Production, Orders, and Sales Status'
# '業績等の概要':'Overview of Business Results'
# '経営上の重要な契約':'Material Contracts for Operation'
# '研究開発活動':'Research and Development Activities'
# 'サステナビリティに関する考え方及び取組':'Approach and Initiatives Regarding Sustainability'
# '人的資本目標':'Human Capital Targets'
# 'コーポレート・ガバナンス':'Corporate Governance'
output_df = pd.DataFrame(extracted_data, columns=columns)
output_file = 'extracted_data.csv'
output_df = output_df.sort_values(['ticker', '決算日'])
output_df.to_csv(output_file, index=False, encoding='utf-8')
