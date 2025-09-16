import pandas as pd
import re
import io

def parse_basic_stats(report_content):
    """解析基本統計數據"""
    print("正在解析: 基本統計數據...")
    stats = {}
    patterns = {
        '總影像數': r"總影像數: (\d+)",
        '總病患數': r"總病患數: (\d+)",
        '病患平均年齡': r"病患平均年齡: ([\d\.]+) 歲",
        '男性數量': r"男女數量: 男性 (\d+),",
        '女性數量': r"男女數量: .*女性 (\d+)",
        '男女比率 (男:女)': r"男女比率 \(男:女\): ([\d\.:\sNA/]+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, report_content)
        if match:
            stats[key] = match.group(1).strip()
    
    df = pd.DataFrame(list(stats.items()), columns=['項目', '數值'])
    df.to_csv('report_basic_stats.csv', index=False, encoding='utf-8-sig')
    print("  -> 已儲存 report_basic_stats.csv")

def parse_prevalence(report_content):
    """解析疾病盛行率"""
    print("正在解析: 疾病盛行率...")
    try:
        counts_str = report_content.split('各疾病數量統計:')[1].split('各疾病盛行率 (%):')[0]
        counts_io = io.StringIO(counts_str)
        counts_df = pd.read_csv(counts_io, sep=r'\s{2,}', engine='python', header=None, names=['疾病', '數量']).dropna()
        counts_df = counts_df[~counts_df['疾病'].str.contains('Name:')]

        prevalence_str = report_content.split('各疾病盛行率 (%):')[1].split('--- (3)')[0]
        prevalence_io = io.StringIO(prevalence_str)
        prevalence_df = pd.read_csv(prevalence_io, sep=r'\s{2,}', engine='python', header=None, names=['疾病', '盛行率(%)']).dropna()
        prevalence_df = prevalence_df[~prevalence_df['疾病'].str.contains('Name:')]

        merged_df = pd.merge(counts_df, prevalence_df, on='疾病')
        merged_df.to_csv('report_disease_prevalence.csv', index=False, encoding='utf-8-sig')
        print("  -> 已儲存 report_disease_prevalence.csv")
    except Exception as e:
        print(f"  -> 解析疾病盛行率失敗: {e}")

def parse_gender_table_manually(report_content):
    """手動解析疾病與性別關聯表格"""
    print("正在解析: 疾病與性別關聯 (手動模式)...")
    try:
        table_str = report_content.split('各疾病中的性別分佈 (按案例數排序):')[1].split('--- (4)')[0].strip()
        lines = table_str.split('\n')[1:] # Skip header
        columns = ['疾病', '男性比例 (%)', '女性比例 (%)', '總案例數']
        parsed_data = []
        pattern = re.compile(r'^(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+(\d+)$')
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                parsed_data.append([match.group(1).strip(), float(match.group(2)), float(match.group(3)), int(match.group(4))])
        df = pd.DataFrame(parsed_data, columns=columns)
        df.to_csv('report_disease_gender.csv', index=False, encoding='utf-8-sig')
        print("  -> 已儲存 report_disease_gender.csv")
    except Exception as e:
        print(f"  -> 手動解析 疾病與性別關聯 失敗: {e}")

def parse_age_table_manually(report_content):
    """手動解析疾病與年齡關聯表格"""
    print("正在解析: 疾病與年齡關聯 (手動模式)...")
    try:
        table_str = report_content.split('各疾病的年齡分佈統計 (按案例數排序):')[1].split('--- (5)')[0].strip()
        lines = table_str.split('\n')[1:] # Skip header
        columns = ['疾病', '平均年齡', '年齡標準差', '中位數年齡', '總案例數']
        parsed_data = []
        pattern = re.compile(r'^(.+?)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+(\d+)$')
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                parsed_data.append([match.group(1).strip(), float(match.group(2)), float(match.group(3)), float(match.group(4)), int(match.group(5))])
        df = pd.DataFrame(parsed_data, columns=columns)
        df.to_csv('report_disease_age.csv', index=False, encoding='utf-8-sig')
        print("  -> 已儲存 report_disease_age.csv")
    except Exception as e:
        print(f"  -> 手動解析 疾病與年齡關聯 失敗: {e}")

def parse_evolution(report_content):
    """解析疾病演變分析"""
    print("正在解析: 初始疾病演變分析...")
    try:
        evolution_section = report_content.split('--- (5) 初始疾病演變分析 ---')[1]
        blocks = re.split(r'--- 初始診斷為 \'(.+?)\' 的後續疾病分析 ---', evolution_section)
        all_evolution_data = []
        for i in range(1, len(blocks), 2):
            initial_disease = blocks[i]
            table_str = blocks[i+1].split('==================================================')[0].strip()
            if "沒有找到" in table_str or "未發現" in table_str:
                continue
            table_io = io.StringIO(table_str)
            df = pd.read_csv(table_io, sep=r'\s{2,}', engine='python')
            df['初始疾病'] = initial_disease
            all_evolution_data.append(df)
        if all_evolution_data:
            combined_df = pd.concat(all_evolution_data, ignore_index=True)
            cols = ['初始疾病'] + [col for col in combined_df.columns if col != '初始疾病']
            combined_df = combined_df[cols]
            combined_df.to_csv('report_disease_evolution.csv', index=False, encoding='utf-8-sig')
            print("  -> 已儲存 report_disease_evolution.csv")
        else:
            print("  -> 未找到可解析的疾病演變數據。")
    except Exception as e:
        print(f"  -> 解析初始疾病演變分析失敗: {e}")

def main():
    """主函數，讀取報告並執行所有解析"""
    try:
        with open('analysis_report.txt', 'r', encoding='utf-8') as f:
            report_content = f.read()
    except FileNotFoundError:
        print("錯誤：找不到 'analysis_report.txt'。請先執行 'data_analyze.py' 來產生報告。")
        return

    print("開始解析 'analysis_report.txt'...")
    
    parse_basic_stats(report_content)
    parse_prevalence(report_content)
    parse_gender_table_manually(report_content)
    parse_age_table_manually(report_content)
    parse_evolution(report_content)
    
    print("\n所有可解析的區塊都已轉換為 CSV 檔案。")

if __name__ == '__main__':
    main()
