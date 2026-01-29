import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def validate_dataframe(df):
    """Проверка корректности DataFrame"""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Входные данные должны быть pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame пустой")
    
    return True

def normalize_column_names(df):
    """Нормализация названий столбцов"""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
    return df

def detect_data_types(df):
    """Определение типов данных в столбцах"""
    data_types = {}
    
    for col in df.columns:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            data_types[col] = 'unknown'
            continue
        
        # Проверка на числовой тип
        try:
            pd.to_numeric(col_data)
            if col_data.astype(float).apply(lambda x: x.is_integer()).all():
                data_types[col] = 'integer'
            else:
                data_types[col] = 'float'
        except:
            # Проверка на категориальный тип
            unique_ratio = len(col_data.unique()) / len(col_data)
            if unique_ratio < 0.1:  # Меньше 10% уникальных значений
                data_types[col] = 'categorical'
            else:
                data_types[col] = 'text'
    
    return data_types

def create_summary_report(df, output_path):
    """Создание отчета по данным"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'shape': {
            'rows': len(df),
            'columns': len(df.columns)
        },
        'data_types': detect_data_types(df),
        'missing_values': {
            'total': int(df.isnull().sum().sum()),
            'by_column': df.isnull().sum().to_dict()
        },
        'descriptive_stats': {}
    }
    
    # Добавление описательной статистики для числовых столбцов
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        report['descriptive_stats'] = df[numeric_cols].describe().to_dict()
    
    # Сохранение отчета
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def save_clustering_results(data, labels, feature_names, output_dir, algorithm):
    """Сохранение результатов кластеризации"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Создание DataFrame с результатами
    results_df = pd.DataFrame(data, columns=feature_names)
    results_df['cluster_label'] = labels
    
    # Сохранение в CSV
    csv_path = os.path.join(output_dir, f'clustering_{algorithm}_{timestamp}.csv')
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    
    # Сохранение метаданных
    metadata = {
        'algorithm': algorithm,
        'timestamp': timestamp,
        'n_clusters': len(np.unique(labels)),
        'n_samples': len(data),
        'features': feature_names
    }
    
    metadata_path = os.path.join(output_dir, f'metadata_{algorithm}_{timestamp}.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return csv_path, metadata_path