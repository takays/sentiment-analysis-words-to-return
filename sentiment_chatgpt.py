import openai
import time
import pandas as pd
from scipy import stats
import os
import re
import random
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import japanize_matplotlib
from openai import OpenAI
import time
import re
import openai
import pandas as pd

df_X_df_segment = pd.read_csv('MDA_X_DataSet.csv', encoding='utf-8', dtype={'nkcode':'object', 'ticker':'object', 'ticker_上場廃止':'object', 'year':'object', 'month':'object', 'month_end':'object'}, parse_dates=['報告日', '決算日'])
print(df_X_df_segment)

openai.api_key = os.getenv('OPENAI_API_KEY')
api_model = "gpt-4o-mini-2024-07-18"
max_chars_per_chunk = 100000 - 500

def analyze_sentiment(df, api_model):
    instruction = f"""あなたは証券アナリストです。以下の企業の開示情報を読み、文脈も考慮して、positive_sentiment_scoreとnegative_sentiment_scoreを合計100になるように算出しなさい。
    ルール)
    フォーマットは以下で出力しなさい。positive_score: X(0〜100) negative_score: Y(0〜100)
    positive_scoreとnegative_scoreは、両方合わせて100になるようにスコアを算出しなさい。
    例を参考にして開示情報の内容全体を漏れなく厳密に評価しなさい。
    理由は出力しないで、positive_score: X(0〜100) negative_score: Y(0〜100)のみを出力してください。
    ・positive_scoreが100の開示情報の例
    「セグメント利益は、販売数量の増加により、同247百万円増益の178百万円となりました」
    「米国では企業業績や個人消費が堅調に推移し、景気は緩やかに回復しました」
    「営業利益は、非鉄金属相場や為替相場の変動に伴うたな卸資産の在庫影響（以下「在庫要因」）が好転し、機能材料部門において主要製品の販売量が増加したこと等により、前連結会計年度に比べて273億円（245.3%）増加の384億円となりました」
    「期間限定で東京駅一番街にオープンした当社初のアンテナショップ「パティスリーブルボン」では、特別に仕立てたクッキーの限定商品「ラングレイス」や「ルマンドアソート」などに大きな反響をいただきました」
    「セグメント利益は、のれん償却費３億33百万円を計上したものの、上記要因に伴う営業利益の増加に加え、飲食用資材分野における原材料価格の下落などにより、９億45百万円と前年同期比２億41百万円（34.3%）の増益となりました」
    ・negative_scoreが100の開示情報の例
    「建築用塗料を取扱う塗料部門におきましては、新築向け市場及びリフォーム向け市場とも、工事を伴う施工棟数が前年度に比べ伸び悩んだことなどにより、売上高は減少いたしました」
    「この結果、売上高は126億17百万円（同4.8％減）となり、営業利益は７億40百万円（同11.2％減）となりました」
    「即席麺部門は、製造ラインの移設に伴う稼働率の低下と受託が低調に推移し、また、３月に製造ラインを増設しましたが、売上の寄与は低く、売上高は7,085百万円と前年同期と比べ659百万円（8.5％）の減収となり、セグメント利益（営業利益）は204百万円と前年同期と比べ219百万円（51.8％）の減益となりました」
    「しかしながら、資材費や労務費のコストが高止まりする中で、北海道・東北地区の集中豪雨の影響により、公共工事の優先順位が入れ替わり、当初予定されていた工期が先延ばしになるなど、当社を取り巻く経営環境は厳しい状況で推移しました」
    「当事業年度におけるわが国経済は、政府による経済政策や金融政策の総動員もあり、緩やかな回復基調となったものの、個人消費や設備投資は力強さを欠き、海外経済の減速と為替、原材料価格の変動リスクを抱え、先行き不透明な状況が続いた」"""
     
    def split_text(text, max_chars=max_chars_per_chunk):
        sentences = text.split('。')
        chunks = []
        current_chunk = ""
        current_chars = 0

        for sentence in sentences:
            sentence_chars = len(sentence)
            if current_chars + sentence_chars > max_chars:
                chunks.append(current_chunk)
                current_chunk = sentence
                current_chars = sentence_chars
            else:
                current_chunk += sentence + "。"
                current_chars += sentence_chars

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    dat = df.copy()
    results_rand = []
    for index, row in dat.iterrows():
        text = row['MDA']
        ticker = row['ticker']
        name = row['name']
        closing_date = row['決算日']
        reporting_date = row['報告日']
        year = row['year']
        month = row['month']
        industry_33 = row['industry_33']
        MDA_文字数 = row['MDA_文字数']
        positive_probability = 	row['positive_probability']
        negative_probability = 	row['negative_probability']
        
        print(name, ticker)
        text_chunks = split_text(text)

        all_responses = []
        all_input_tokens = []
        all_output_tokens = []
        chunk_texts = []
        for chunk in text_chunks:
            time.sleep(20)

            retry_attempts = 0
            max_retries = 5
            while retry_attempts < max_retries:
                try:
                    response_rand = client.chat.completions.create(
                        model=api_model,
                        messages=[
                            {"role": "system", "content": instruction},
                            {"role": "user", "content": chunk}
                        ],
                        temperature=0.3,
                        max_tokens=500, 
                        top_p=0.5,
                        frequency_penalty=0.5,
                        presence_penalty=0
                    )

                    response_text_rand = response_rand.choices[0].message.content
                    #print('response_text_rand', response_text_rand)
                    all_responses.append(response_text_rand)
                    chunk_texts.append(response_text_rand)
                    all_input_tokens.append(response_rand.usage.prompt_tokens)
                    all_output_tokens.append(response_rand.usage.completion_tokens)
                    break 

                except openai.OpenAIError as e:
                    retry_attempts += 1
                    wait_time = 30 
                    print(f"Rate limit exceeded: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue  


        posi_scores = []
        nega_scores = []
        posi_pattern = re.compile(r'positive_score\s*[:：]\s*([0-9]{1,3}(\.[0-9]+)?)')
        nega_pattern = re.compile(r'negative_score\s*[:：]\s*([0-9]{1,3}(\.[0-9]+)?)')
        for response in all_responses:
            posi_match = posi_pattern.search(response)
            nega_match = nega_pattern.search(response)
            if posi_match:
                posi_scores.append(float(posi_match.group(1)))
            if nega_match:
                nega_scores.append(float(nega_match.group(1)))    

        posi_score_avg = sum(posi_scores) / len(posi_scores) if posi_scores else None
        nega_score_avg = sum(nega_scores) / len(nega_scores) if nega_scores else None

        result_rand = {
            "ticker": ticker,
            "name": name,
            "報告日": reporting_date,
            "決算日": closing_date,
            "year": year,
            "month": month,
            "positive_probability": positive_probability,
            "negative_probability": negative_probability,
            "gpt_positive": posi_score_avg,
            "gpt_negative": nega_score_avg,
            "input_tokens": all_input_tokens,
            "output_tokens": all_output_tokens,
            "industry_33": industry_33,
            "MDA_文字数": MDA_文字数
        }
        if len(text_chunks) > 1:
            result_rand["chunk_responses"] = chunk_texts

        results_rand.append(result_rand)

    results_dat = pd.DataFrame(results_rand)

    max_segments = max(results_dat['input_tokens'].apply(len))

    for i in range(max_segments):
        results_dat[f'input_tokens_{i+1}'] = results_dat['input_tokens'].apply(lambda x: x[i] if i < len(x) else None)
        results_dat[f'output_tokens_{i+1}'] = results_dat['output_tokens'].apply(lambda x: x[i] if i < len(x) else None)

    results_dat.drop(columns=['input_tokens', 'output_tokens'], inplace=True)
    return results_dat


error_tickers = []
tickers_list = df_X_df_segment['ticker'].unique().tolist()
for ticker in tickers_list:
    try:
        results_ = analyze_sentiment(df_X_df_segment[df_X_df_segment['ticker'] == ticker], api_model)
        results_dat_ = results_.copy()

        results_dat_[['gpt_positive', 'gpt_negative']] = results_dat_[['gpt_positive', 'gpt_negative']] / 100

        if results_dat_['gpt_positive'].isna().any() or results_dat_['gpt_negative'].isna().any():
            raise ValueError(f"{ticker} is NaN")

        results_dat_.to_csv(f'{ticker}.csv', index=False, encoding='utf-8-sig')


    except Exception as e:
        print(f'{ticker} error: {e}')
        error_tickers.append(ticker)
        
with open('error_tickers.txt', 'w') as f:
    for ticker in error_tickers:
        f.write(f"{ticker}\n")

directory = '/'
csv_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

df_list = [pd.read_csv(file, parse_dates=['決算日', '報告日'], dtype={'ticker':'object', 'year':'object', 'month':'object'}) for file in csv_files]
combined_df = pd.concat(df_list, axis=0)

output_file = 'combined_output.csv'
combined_df = combined_df.sort_values(['ticker', '決算日'])
combined_df[['ticker', 'year', 'month']] = combined_df[['ticker', 'year', 'month']].astype(str)
combined_df.to_csv(output_file, index=False)



