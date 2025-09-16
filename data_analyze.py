import pandas as pd
import sys

def clean_nih_data(file_path):
    """
    Cleans the NIH Chest X-ray dataset entry file.
    - Reads the CSV file.
    - Corrects improperly parsed column names.
    - Drops empty columns.
    - Converts 'Patient Age' to a numeric type.
    - Standardizes column names.
    """
    # Load the dataset
    df = pd.read_csv(file_path)

    # 1. Drop the empty 'Unnamed: 11' column
    # It's created due to a trailing comma in the CSV header
    if 'Unnamed: 11' in df.columns:
        df = df.drop(columns=['Unnamed: 11'])

    # 2. Define a mapping for renaming columns for clarity and fixing parsing issues
    column_rename_map = {
        'Image Index': 'Image_Index',
        'Finding Labels': 'Finding_Labels',
        'Follow-up #': 'Follow_Up_Num',
        'Patient ID': 'Patient_ID',
        'Patient Age': 'Patient_Age',
        'Patient Gender': 'Patient_Gender',
        'View Position': 'View_Position',
        'OriginalImage[Width': 'Original_Image_Width',
        'Height]': 'Original_Image_Height',
        'OriginalImagePixelSpacing[x': 'Pixel_Spacing_X',
        'y]': 'Pixel_Spacing_Y'
    }
    df = df.rename(columns=column_rename_map)

    # 3. Clean and convert 'Patient_Age' to a numeric type
    # It's stored as a string like '58Y', so we remove non-numeric characters and convert to int
    df['Patient_Age'] = df['Patient_Age'].astype(str).str.extract('(\d+)', expand=False).astype(int)

    return df

if __name__ == '__main__':
    # --- 1. 數據載入與清理 ---
    print("--- 正在載入與清理數據... ---")
    data_file_path = 'Data_Entry_2017.csv'
    df = clean_nih_data(data_file_path)
    print("數據清理完成。")

    # --- 2. 數據分析 (寫入檔案) ---
    print("--- 正在產生分析報告... ---")
    original_stdout = sys.stdout  # 保存原始標準輸出
    try:
        with open('analysis_report.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f  # 將標準輸出重定向到檔案

            print("--- NIH Chest X-ray 數據分析報告 ---")
            # 基本統計數據
            print("\n--- (1) 基本統計數據 ---")
            total_images = len(df)
            total_patients = df['Patient_ID'].nunique()
            average_age = df['Patient_Age'].mean()
            gender_counts = df['Patient_Gender'].value_counts()
            male_count = gender_counts.get('M', 0)
            female_count = gender_counts.get('F', 0)
            gender_ratio = f"{male_count / female_count:.2f} : 1" if female_count > 0 else "N/A"

            print(f"總影像數: {total_images}")
            print(f"總病患數: {total_patients}")
            print(f"病患平均年齡: {average_age:.2f} 歲")
            print(f"男女數量: 男性 {male_count}, 女性 {female_count}")
            print(f"男女比率 (男:女): {gender_ratio}")

            # 疾病盛行率分析
            print("\n--- (2) 疾病盛行率排名 ---")
            all_labels = df['Finding_Labels'].str.split('|').explode()
            all_diseases = all_labels[all_labels != 'No Finding']
            disease_counts = all_diseases.value_counts()
            disease_prevalence = (disease_counts / total_images) * 100
            print(f"發現總數 (不含 'No Finding'): {all_diseases.count()}")
            print("\n各疾病數量統計:")
            print(disease_counts)
            print("\n各疾病盛行率 (%):")
            print(disease_prevalence.round(4))
            
            # 疾病與性別關聯
            print("\n--- (3) 疾病與性別關聯 ---")
            unique_diseases = all_diseases.unique().tolist()
            gender_association_data = []
            for disease in unique_diseases:
                disease_df = df[df['Finding_Labels'].str.contains(disease, na=False)]
                gender_dist = disease_df['Patient_Gender'].value_counts()
                male_d_count = gender_dist.get('M', 0)
                female_d_count = gender_dist.get('F', 0)
                total_d_count = male_d_count + female_d_count
                if total_d_count > 0:
                    male_percent = (male_d_count / total_d_count) * 100
                    female_percent = (female_d_count / total_d_count) * 100
                    gender_association_data.append({
                        '疾病': disease,
                        '男性比例 (%)': f"{male_percent:.2f}",
                        '女性比例 (%)': f"{female_percent:.2f}",
                        '總案例數': total_d_count
                    })
            gender_df = pd.DataFrame(gender_association_data).sort_values(by='總案例數', ascending=False)
            print("各疾病中的性別分佈 (按案例數排序):")
            print(gender_df.to_string(index=False))

            # 疾病與年齡關聯
            print("\n--- (4) 疾病與年齡關聯 ---")
            age_association_data = []
            for disease in unique_diseases:
                disease_df = df[df['Finding_Labels'].str.contains(disease, na=False)]
                age_stats = disease_df['Patient_Age'].describe()
                age_association_data.append({
                    '疾病': disease,
                    '平均年齡': age_stats['mean'],
                    '年齡標準差': age_stats['std'],
                    '中位數年齡': age_stats['50%'],
                    '總案例數': int(age_stats['count'])
                })
            age_df = pd.DataFrame(age_association_data).sort_values(by='總案例數', ascending=False)
            pd.options.display.float_format = '{:.2f}'.format
            print("各疾病的年齡分佈統計 (按案例數排序):")
            print(age_df.to_string(index=False))
            pd.reset_option('display.float_format')

            # Follow-up 分析 (新版 v3 - 指定順序)
            print("\n--- (5) 初始疾病演變分析 ---")
            print("分析說明：針對每種單一的初始疾病，統計其後續追蹤中新出現的其他疾病種類與佔比。\n")

            # 依照使用者指定的順序
            analysis_order = [
                'No Finding', 'Infiltration', 'Effusion', 'Atelectasis', 'Nodule', 'Mass', 
                'Pneumothorax', 'Consolidation', 'Pleural_Thickening', 'Cardiomegaly', 
                'Emphysema', 'Edema', 'Fibrosis', 'Pneumonia', 'Hernia'
            ]
            
            # 獲取數據中實際存在的所有標籤以進行檢查
            all_single_labels_in_data = df['Finding_Labels'].str.split('|').explode().unique()

            for initial_disease in analysis_order:
                if initial_disease not in all_single_labels_in_data:
                    continue # 如果指定的疾病不存在於數據中，則跳過

                # --- 針對每種初始疾病進行分析 ---
                print(f"--- 初始診斷為 '{initial_disease}' 的後續疾病分析 ---")

                # 找出初次診斷為指定單一疾病的病患 ID
                # 我們只考慮初診只有一個標籤的案例，以簡化分析
                patient_cohort = df[(df['Follow_Up_Num'] == 0) & (df['Finding_Labels'] == initial_disease)]['Patient_ID'].unique()

                if len(patient_cohort) == 0:
                    print("資料庫中沒有找到初次診斷僅為此項的案例。\n")
                    continue

                # 從這些病患中，找出他們後續追蹤的紀錄
                follow_ups = df[(df['Patient_ID'].isin(patient_cohort)) & (df['Follow_Up_Num'] > 0)]

                if follow_ups.empty:
                    print("此組病患沒有後續追蹤紀錄可供分析。\n")
                    continue

                # 統計後續出現的所有疾病 (排除初始疾病本身)
                all_follow_up_diseases = follow_ups['Finding_Labels'].str.split('|').explode()
                new_diseases = all_follow_up_diseases[all_follow_up_diseases != initial_disease]
                
                # 移除 'No Finding' 標籤，因為它不是一種疾病
                new_diseases = new_diseases[new_diseases != 'No Finding']

                if new_diseases.empty:
                    print("後續追蹤中未發現新的不同疾病。\n")
                    continue

                # 計算次數與百分比
                new_disease_counts = new_diseases.value_counts()
                total_new_findings = len(new_diseases)
                new_disease_percentages = (new_disease_counts / total_new_findings) * 100

                # 合併成一個 DataFrame 來顯示
                result_df = pd.DataFrame({
                    '新發現的疾病': new_disease_counts.index,
                    '發現次數': new_disease_counts.values,
                    '佔比 (%)': new_disease_percentages.values
                })
                
                # 設置顯示格式
                pd.options.display.float_format = '{:.2f}'.format
                print(result_df.to_string(index=False))
                pd.reset_option('display.float_format')
                print("\n" + "="*50 + "\n")

    finally:
        sys.stdout = original_stdout  # 還原標準輸出

    print("分析報告已成功儲存至 'analysis_report.txt'")

    # --- 3. 儲存清理後的數據 ---
    print("\n--- 正在儲存清理後的數據... ---")
    df.to_csv('Data_Entry_2017_cleaned.csv', index=False)
    print("清理後的數據已儲存至 'Data_Entry_2017_cleaned.csv'")
