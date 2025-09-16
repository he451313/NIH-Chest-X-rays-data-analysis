# NIH 胸部 X 光數據分析專案

## 專案簡介

本專案旨在對美國國家衛生院 (NIH) 發布的 Chest X-ray 數據集（包含超過 10 萬張匿名的胸部 X 光影像）的元數據進行深入分析。透過數據清理、轉換和多維度分析，我們旨在揭示數據集中的基本統計特徵、疾病盛行率、以及疾病與患者年齡、性別之間的潛在關聯。

最終的分析結果不僅以結構化的 CSV 檔案呈現，還透過 Looker Studio 進行了視覺化展示，以便更直觀地理解數據洞察。

## 數據圖表

您可以在下方的連結中查看使用本專案設計的數據圖表：

[**點擊這裡查看 Looker Studio**](https://lookerstudio.google.com/reporting/9b1755f8-4702-4705-9a89-56fc25623d18)



## 主要分析內容

*   **基本統計分析：** 計算數據集中的總影像數、獨立病患數、平均年齡及性別分佈。
*   **疾病盛行率分析：** 統計並排名各種疾病標籤的出現頻率與盛行率。
*   **疾病與性別關聯分析：** 探討不同疾病在男性與女性患者中的分佈比例。
*   **疾病與年齡關聯分析：** 分析不同疾病患者的平均年齡、中位數年齡等統計數據。
*   **初始疾病演變分析：** 追蹤初次診斷為特定疾病的患者，在後續追蹤檢查中出現了哪些新的疾病。

## 使用流程

請依照以下步驟執行本專案的完整分析流程。

### 1. 環境準備

確保您的環境中已安裝 Python 以及 `pandas` 函式庫。

```bash
pip install pandas
```

### 2. 執行數據清理與初步分析

首先，執行 `data_analyze.py` 腳本。此腳本會：
1.  讀取原始數據 `Data_Entry_2017.csv`。
2.  進行數據清理（欄位重塑、格式轉換等）。
3.  將清理後的數據儲存為 `Data_Entry_2017_cleaned.csv`。
4.  生成一份包含所有分析結果的文字報告 `analysis_report.txt`。

```bash
python data_analyze.py
```

### 3. 將分析報告轉換為 CSV 檔案

接著，執行 `report_to_csv.py` 腳本。此腳本會讀取 `analysis_report.txt`，並將其中各個分析模組的結果解析並儲存為獨立的 CSV 檔案。

```bash
python report_to_csv.py
```

執行完畢後，您將在根目錄下看到所有 `report_*.csv` 相關的分析報告檔案。

## 檔案結構說明

```
.
├── data_analyze.py             # 主腳本：數據清理與生成文字分析報告
├── report_to_csv.py            # 次腳本：將文字報告轉換為多個 CSV 檔案
├── Data_Entry_2017.csv         # 原始數據集
├── Data_Entry_2017_cleaned.csv # 清理後的數據集
├── analysis_report.txt         # 包含所有分析結果的綜合文字報告
├── report_basic_stats.csv      # 基本統計數據報告
├── report_disease_age.csv      # 疾病與年齡關聯報告
├── report_disease_evolution.csv# 疾病演變分析報告
├── report_disease_gender.csv   # 疾病與性別關聯報告
├── report_disease_prevalence.csv # 疾病盛行率報告
└── README.md                   # 專案說明文件
```
