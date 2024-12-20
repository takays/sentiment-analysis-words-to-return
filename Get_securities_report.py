# %%
import requests
import datetime
import pandas as pd
import time
import os

# %%
# 取りたい期間を指定
Syear = 2024
Eyear = 2024
start_date = datetime.date(Syear, 3, 1)
end_date = datetime.date(Eyear, 3,31)
ipath = f'./{Syear}'
os.makedirs(ipath,exist_ok=True)

# 書類取得APIのリクエストパラメータ：5はcsv
params = {
  "type" : 5
}
YOUR_SUBSCRIPTION_KEY = 'YOUR_SUBSCRIPTION_KEY'
#form_code=030000：有報　050000:半報 043000:四半期報告書, 024000：新規上場時の有報
Form_code = "030000"

# %%
# 日付取得
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
# docIDが必要になるので、取得
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

            #form_code=030000：有報　050000:半報 043000:四半期報告書,
            #f ordinance_code == "010" and (form_code =="043000" or form_code =="050000") :
            if ordinance_code == "010" and  form_code ==f'{Form_code}' :
                company_name=json_data["results"][num]["filerName"]
                edi={'会社名':company_name,
                            '書類名':json_data["results"][num]["docDescription"],
                            'docID':json_data["results"][num]["docID"],
                            '証券コード':json_data["results"][num]["secCode"],
                            'ＥＤＩＮＥＴコード':json_data["results"][num]["edinetCode"],
                            '決算期':json_data["results"][num]["periodEnd"],
                            '提出日': day}
                report_list.append(edi)

    return report_list

report_list = create_report_list(day_list)
list_df = pd.DataFrame(report_list)
list_df.to_csv(f'{ipath}/code_list.csv', index=False)

# %%
# 全docIDのデータを取得する
import pandas as pd
import requests
import os
from zipfile import ZipFile
from urllib.request import urlretrieve

# CSVファイルを読み込む
df = pd.read_csv(f'code_list.csv', dtype={'証券コード':'object'})
# null行=非上場銘柄
df = df[df['証券コード'].notnull()]

# Securities reportディレクトリを作成
securities_report_dir = ipath
if not os.path.exists(securities_report_dir):
    os.makedirs(securities_report_dir)

# 各行に対してループ
for index, row in df.iterrows():
    edinet_code = row['docID']
    security_code = row['証券コード']
    # Securities reportディレクトリ下に証券コードディレクトリを作成
    directory = os.path.join(securities_report_dir, str(security_code))

    # ディレクトリが存在しない場合は作成
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # ファイル名とダウンロードURLを設定
    filename = os.path.join(directory, f"{security_code}.zip")
    url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{edinet_code}?Subscription-Key={YOUR_SUBSCRIPTION_KEY}&type=5"
    
    # ファイルをダウンロード
    try:
        urlretrieve(url, filename)
        
        # ダウンロードしたzipファイルを解凍
        with ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(directory)
        print(f"{security_code} のデータをダウンロードして解凍しました。")
    except Exception as e:
        print(f"{security_code} のダウンロードまたは解凍中にエラーが発生しました：{e}")


# %%
# 取得したファイルを必要項目のみ抽出してまとめる
import pandas as pd
import os
import glob

# 初期化
extracted_data = []

# 検索するディレクトリのパス
search_dir = './'

# 出力ファイルのパス
output_file = search_dir + 'extracted_data.csv'

# 対象のCSVファイルを検索
csv_files = glob.glob(f"{search_dir}/**/XBRL_TO_CSV/jpcrp*", recursive=True)
def extract_text_block(df, column_name):
    # 特定のテキストブロック項目を抽出する関数
    row = df[df['項目名'] == column_name]
    return row.iloc[0]['値'] if not row.empty else None

def extract_text_block_element(df, column_name):
    # 特定のテキストブロック項目を抽出する関数
    row = df[df['要素ID'] == column_name]
    return row.iloc[0]['値'] if not row.empty else None

for csv_file in csv_files:
    try:
        # CSVファイルを読み込む
        df = pd.read_table(csv_file, encoding="utf-16", on_bad_lines='skip')
        # 証券コードをファイルパスから抽出
        ticker = os.path.basename(os.path.dirname(os.path.dirname(csv_file)))
        # 提出日、表紙 (仮定: 「提出日、表紙」という項目名が存在する)
        reporting_date = extract_text_block(df, "提出日、表紙")
        firm_name = extract_text_block(df, "会社名、表紙")
        
        # 当会計期間終了日、DEI
        closing_date = extract_text_block(df, "当会計期間終了日、DEI")
        # 各テキストブロックの抽出
        Business_content = extract_text_block(df, "事業の内容 [テキストブロック]")
        management_policy = extract_text_block(df, "経営方針、経営環境及び対処すべき課題等 [テキストブロック]") or extract_text_block(df, "対処すべき課題 [テキストブロック]")
        business_risks = extract_text_block(df, "事業等のリスク [テキストブロック]")
        financial_condition = extract_text_block(df, "経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析 [テキストブロック]") or extract_text_block(df, "財政状態、経営成績及びキャッシュ・フローの状況の分析 [テキストブロック]") or extract_text_block_element(df, "jpcrp030000-asr_E00012-000:ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")
        performance_summary = extract_text_block(df, "業績等の概要 [テキストブロック]")
        important_contracts = extract_text_block(df, "経営上の重要な契約等 [テキストブロック]") or extract_text_block(df, "経営上の重要な契約等（該当なし） [テキストブロック]")
        Production_and_sales = extract_text_block(df, "生産、受注及び販売の状況 [テキストブロック]")
        research_development = extract_text_block(df, "研究開発活動 [テキストブロック]")

        # 抽出した情報をリストに追加
        extracted_data.append([firm_name, ticker, reporting_date, closing_date, Business_content, management_policy, business_risks, financial_condition, performance_summary, important_contracts, Production_and_sales, research_development])
    except Exception as e:
        print(f"ファイル {csv_file} の処理中にエラーが発生しました: {e}")

# DataFrameを作成し、CSVに保存
columns = ['name', 'ticker', 'reporting_date', 'acc', '事業の内容', '経営方針、経営環境及び対処すべき課題', '事業等のリスク', '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析', '業績等の概要', '経営上の重要な契約', '生産、受注及び販売の状況', '研究開発活動']
output_df = pd.DataFrame(extracted_data, columns=columns)
output_df = output_df.sort_values(['ticker', 'reporting_date'])
output_df.to_csv(output_file, index=False, encoding='utf-8')
#output_df.to_csv('xx1301.csv', index=False, encoding='utf-8')

print("データの抽出と保存が完了しました。")

# %%

# 年代の範囲を設定
years = range(2010, 2025)  # 2010年から2020年まで

# 対象のCSVファイルを検索
csv_files = []
for year in years:
    csv_files.extend(glob.glob(f"{search_dir}{year}/**/XBRL_TO_CSV/jpcrp030000-asr-001_*.csv", recursive=True))

# ファイルリストを出力して確認
print(f"Number of CSV files found: {len(csv_files)}")
for file in csv_files:
    print(file)


# %%
import re
import os
import pandas as pd
import numpy as np

# 空白除去
def parse_and_clean_text(text):
    if isinstance(text, str):
        text = re.sub('\s', '', text)
        text = re.sub('<.*?>', '', text)
    return text

def erement_text(df, column_name):
    # 特定のテキストブロック項目を抽出する関数
    row = df[df['要素ID'].str.contains(column_name, na=False)]
    return row.iloc[0]['値'] if not row.empty else None

# test用
#xxcsv_files = ["/Users/moe/Bloated_Disclosure/DATA/Securities_report/2018/87080/XBRL_TO_CSV/jpcrp030000-asr-001_E03763-000_2018-03-31_01_2018-06-28.csv"]  # サンプルファイルのリストを設定
extracted_data = []

for csv_file in csv_files:
#for csv_file in xxcsv_files:
    try:
        # CSVファイルを読み込む
        df = pd.read_table(csv_file, encoding="utf-16", on_bad_lines='skip')
        
        # 各項目のテキストを抽出し、空白やHTMLタグを除去
        # name
        company_name = erement_text(df, "CompanyNameCoverPage")
        company_name = parse_and_clean_text(company_name) if company_name else np.nan
        # ticker
        ticker = erement_text(df, 'jpdei_cor:SecurityCodeDEI')
        ticker = parse_and_clean_text(ticker) if ticker else np.nan
        # 報告日
        reporting_date = erement_text(df, "FilingDateCoverPage")
        reporting_date = parse_and_clean_text(reporting_date) if reporting_date else np.nan
        # 決算日
        closing_date = erement_text(df, "jpdei_cor:CurrentPeriodEndDateDEI")
        closing_date = parse_and_clean_text(closing_date) if closing_date else np.nan
        # 経営方針、経営環境及び対処すべき課題
        management_policy = erement_text(df, "BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock")
        if not management_policy:
            management_policy = erement_text(df, "IssuesToAddressTextBlock")
        management_policy = parse_and_clean_text(management_policy) if management_policy else np.nan
        # 事業等のリスク
        business_risks = erement_text(df, "BusinessRisksTextBlock")
        business_risks = parse_and_clean_text(business_risks) if business_risks else np.nan
        # 経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析
        financial_condition = erement_text(df, "ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")
        if not financial_condition:
            financial_condition = erement_text(df, "AnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock")
        if not financial_condition:
            financial_condition = erement_text(df, "AnalysisAndResponsesToSignificantEventsRelatedToGoingConcernRisksEtcTextBlock")
        financial_condition = parse_and_clean_text(financial_condition) if financial_condition else np.nan
        # 生産、受注及び販売の状況
        Production_order_and_sales_status = erement_text(df, "OverviewOfProductionOrdersReceivedAndSalesTextBlock")
        Production_order_and_sales_status = parse_and_clean_text(Production_order_and_sales_status) if Production_order_and_sales_status else np.nan
        # 業績等の概要
        performance_summary = erement_text(df, "OverviewOfBusinessResultsTextBlock")
        performance_summary = parse_and_clean_text(performance_summary) if performance_summary else np.nan
        # 経営上の重要な契約
        important_contracts = erement_text(df, "CriticalContractsForOperationNATextBlock")
        if not important_contracts:
            important_contracts = erement_text(df, "CriticalContractsForOperationTextBlock")
        important_contracts = parse_and_clean_text(important_contracts) if important_contracts else np.nan
        # 研究開発活動
        research_development = erement_text(df, "ResearchAndDevelopmentActivitiesTextBlock")
        if not research_development:
            research_development = erement_text(df, "ResearchAndDevelopmentActivitiesNATextBlock")
        research_development = parse_and_clean_text(research_development) if research_development else np.nan
        # サステナビリティに関する考え方及び取組
        PolicyOnHuman = erement_text(df, 'DisclosureOfSustainabilityRelatedFinancialInformationTextBlock')
        PolicyOnHuman = parse_and_clean_text(PolicyOnHuman) if PolicyOnHuman else np.nan
        # 人的資本目標
        PolicyOnHuman_target = erement_text(df, 'DescriptionOfMetricsRelatedToPolicyOnHumanResourceDevelopmentAndImprovementOfInternalEnvironmentAndTargetsAndResultsUsingSuchMetricsMetricsAndTargetsTextBlock')
        if not PolicyOnHuman_target:
            PolicyOnHuman_target = erement_text(df, "PolicyOnDevelopmentOfHumanResourcesAndInternalEnvironmentStrategyTextBlock")
        PolicyOnHuman_target = parse_and_clean_text(PolicyOnHuman_target) if PolicyOnHuman_target else np.nan
        # コーポレート・ガバナンス
        CorporateGovernance = erement_text(df, "ExplanationAboutCorporateGovernanceTextBlock")
        if not CorporateGovernance:
            CorporateGovernance = erement_text(df, "OverviewOfCorporateGovernanceTextBlock")
        CorporateGovernance = parse_and_clean_text(CorporateGovernance) if CorporateGovernance else np.nan

        # 抽出した情報をリストに追加
        extracted_data.append([company_name, ticker, reporting_date, closing_date, management_policy, business_risks, financial_condition, Production_order_and_sales_status, performance_summary, important_contracts, research_development, PolicyOnHuman, PolicyOnHuman_target, CorporateGovernance])
    
    except Exception as e:
        print(f"ファイル {csv_file} の処理中にエラーが発生しました: {e}")

# DataFrameを作成し、CSVに保存
columns = ['name', 'ticker', '報告日', '決算日', '経営方針、経営環境及び対処すべき課題', '事業等のリスク', '経営者による財政状態、経営成績及びキャッシュ・フローの状況の分析', '生産、受注及び販売の状況', '業績等の概要', '経営上の重要な契約', '研究開発活動', 'サステナビリティに関する考え方及び取組', '人的資本目標', 'コーポレート・ガバナンス']
output_df = pd.DataFrame(extracted_data, columns=columns)
output_file = 'extracted_data.csv'
output_df = output_df.sort_values(['ticker', '決算日'])
output_df.to_csv(output_file, index=False, encoding='utf-8')

# データフレームを表示
print(output_df.sort_values('決算日'))
print("データの抽出と保存が完了しました。")



