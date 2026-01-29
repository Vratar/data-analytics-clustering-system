import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from scipy import stats
import json

class DataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if self.filepath.endswith('.csv'):
            self.data = pd.read_csv(self.filepath, encoding='utf-8')
        elif self.filepath.endswith('.xlsx'):
            self.data = pd.read_excel(self.filepath)
        else:
            raise ValueError("Неподдерживаемый формат файла")
    
    def get_basic_statistics(self):
        """Получение базовой статистики по данным"""
        stats = {
            'total_records': len(self.data),
            'total_columns': len(self.data.columns),
            'column_types': self.data.dtypes.astype(str).to_dict(),
            'numeric_columns': self.data.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.data.select_dtypes(include=['object']).columns.tolist(),
            'memory_usage': self.data.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
        }
        
        # Basic descriptive statistics for numeric columns
        if len(stats['numeric_columns']) > 0:
            stats['descriptive_stats'] = self.data[stats['numeric_columns']].describe().to_dict()
        
        return stats
    
    def get_missing_values_statistics(self):
        """Статистика пропущенных значений"""
        missing_count = self.data.isnull().sum()
        missing_percent = (missing_count / len(self.data)) * 100
        
        missing_stats = {
            'columns': missing_count.index.tolist(),
            'missing_count': missing_count.tolist(),
            'missing_percent': missing_percent.round(2).tolist(),
            'total_missing': int(missing_count.sum()),
            'total_missing_percent': round((missing_count.sum() / (len(self.data) * len(self.data.columns))) * 100, 2)
        }
        
        return missing_stats
    
    def fill_missing_values(self, method='mean', columns=None):
        """Заполнение пропущенных значений"""
        if columns is None:
            columns = self.data.columns.tolist()
        
        for column in columns:
            if column not in self.data.columns:
                continue
                
            if self.data[column].isnull().sum() == 0:
                continue
            
            if method == 'mean' and pd.api.types.is_numeric_dtype(self.data[column]):
                self.data[column].fillna(self.data[column].mean(), inplace=True)
            
            elif method == 'median' and pd.api.types.is_numeric_dtype(self.data[column]):
                self.data[column].fillna(self.data[column].median(), inplace=True)
            
            elif method == 'mode':
                mode_value = self.data[column].mode()
                if not mode_value.empty:
                    self.data[column].fillna(mode_value[0], inplace=True)
            
            elif method == 'ffill':
                self.data[column].fillna(method='ffill', inplace=True)
            
            elif method == 'bfill':
                self.data[column].fillna(method='bfill', inplace=True)
            
            elif method == 'knn':
                # Используем KNN для заполнения
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 1:
                    knn_imputer = KNNImputer(n_neighbors=5)
                    self.data[numeric_cols] = knn_imputer.fit_transform(self.data[numeric_cols])
    
    def detect_outliers(self, method='iqr'):
        """Обнаружение выбросов"""
        outliers_info = {}
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            
            if method == 'iqr':
                # Метод межквартильного размаха
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = self.data[(self.data[col] < lower_bound) | (self.data[col] > upper_bound)]
                outlier_count = len(outliers)
                
            elif method == 'zscore':
                # Метод Z-score
                z_scores = np.abs(stats.zscore(col_data))
                outlier_count = np.sum(z_scores > 3)
            
            outliers_info[col] = {
                'outlier_count': int(outlier_count),
                'outlier_percent': round((outlier_count / len(col_data)) * 100, 2)
            }
        
        return outliers_info
    
    def remove_outliers(self, method='iqr'):
        """Удаление выбросов"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            
            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Keep data within bounds
                self.data = self.data[(self.data[col] >= lower_bound) & (self.data[col] <= upper_bound) | self.data[col].isna()]
            
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(col_data.fillna(col_data.mean())))
                self.data = self.data[z_scores <= 3]
    
    def save_data(self, filepath):
        """Сохранение обработанных данных"""
        if filepath.endswith('.csv'):
            self.data.to_csv(filepath, index=False)
        elif filepath.endswith('.xlsx'):
            self.data.to_excel(filepath, index=False)
        else:
            raise ValueError("Неподдерживаемый формат файла")