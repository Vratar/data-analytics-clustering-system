import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

class Visualizer:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.color_palette = sns.color_palette("husl", 10)
    
    def plot_clusters_2d(self, data, labels, algorithm='kmeans', save_path=None):
        """Визуализация кластеров в 2D"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        unique_labels = np.unique(labels)
        
        for i, label in enumerate(unique_labels):
            if label == -1:  # Шум для DBSCAN
                color = 'gray'
                label_name = 'Шум'
            else:
                color = self.color_palette[i % len(self.color_palette)]
                label_name = f'Кластер {label}'
            
            cluster_points = data[labels == label]
            ax.scatter(cluster_points[:, 0], cluster_points[:, 1],
                      c=[color], label=label_name, alpha=0.7, s=50)
        
        ax.set_xlabel('Признак 1', fontsize=12)
        ax.set_ylabel('Признак 2', fontsize=12)
        ax.set_title(f'Результаты кластеризации: {algorithm}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return fig
    
    def plot_clusters_3d(self, data, labels, algorithm='kmeans', save_path=None):
        """Визуализация кластеров в 3D"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        unique_labels = np.unique(labels)
        
        for i, label in enumerate(unique_labels):
            if label == -1:
                color = 'gray'
                label_name = 'Шум'
            else:
                color = self.color_palette[i % len(self.color_palette)]
                label_name = f'Кластер {label}'
            
            cluster_points = data[labels == label]
            ax.scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2],
                      c=[color], label=label_name, alpha=0.7, s=50)
        
        ax.set_xlabel('Признак 1', fontsize=11)
        ax.set_ylabel('Признак 2', fontsize=11)
        ax.set_zlabel('Признак 3', fontsize=11)
        ax.set_title(f'3D визуализация: {algorithm}', fontsize=14, fontweight='bold')
        ax.legend()
        
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return fig
    
    def plot_interactive_clusters(self, data, labels, feature_names=None):
        """Интерактивная визуализация кластеров с использованием Plotly"""
        if feature_names is None:
            feature_names = [f'Признак {i+1}' for i in range(data.shape[1])]
        
        if data.shape[1] >= 3:
            # 3D plot
            df = pd.DataFrame(data[:, :3], columns=feature_names[:3])
            df['Кластер'] = labels.astype(str)
            
            fig = px.scatter_3d(df, 
                               x=feature_names[0], 
                               y=feature_names[1], 
                               z=feature_names[2],
                               color='Кластер',
                               title='3D визуализация кластеров',
                               opacity=0.7)
        else:
            # 2D plot
            df = pd.DataFrame(data, columns=feature_names[:2])
            df['Кластер'] = labels.astype(str)
            
            fig = px.scatter(df, 
                            x=feature_names[0], 
                            y=feature_names[1],
                            color='Кластер',
                            title='2D визуализация кластеров',
                            opacity=0.7)
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        return fig
    
    def plot_elbow_method(self, inertias, save_path=None):
        """Метод локтя для определения оптимального количества кластеров"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(range(1, len(inertias) + 1), inertias, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Количество кластеров', fontsize=12)
        ax.set_ylabel('Сумма квадратов расстояний', fontsize=12)
        ax.set_title('Метод локтя для определения оптимального k', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return fig
    
    def plot_cluster_statistics(self, data, labels, feature_names=None):
        """Статистика по кластерам"""
        if feature_names is None:
            feature_names = [f'Признак {i+1}' for i in range(data.shape[1])]
        
        df = pd.DataFrame(data, columns=feature_names)
        df['Кластер'] = labels
        
        cluster_stats = df.groupby('Кластер').agg(['mean', 'std', 'count']).round(3)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Размеры кластеров
        cluster_sizes = df['Кластер'].value_counts().sort_index()
        axes[0, 0].bar(cluster_sizes.index.astype(str), cluster_sizes.values, color=self.color_palette[:len(cluster_sizes)])
        axes[0, 0].set_title('Размеры кластеров', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Кластер')
        axes[0, 0].set_ylabel('Количество объектов')
        
        # Средние значения признаков по кластерам
        if len(feature_names) > 0:
            feature_means = df.groupby('Кластер')[feature_names[0]].mean()
            axes[0, 1].bar(feature_means.index.astype(str), feature_means.values, color=self.color_palette[:len(feature_means)])
            axes[0, 1].set_title(f'Средние значения {feature_names[0]}', fontsize=12, fontweight='bold')
            axes[0, 1].set_xlabel('Кластер')
            axes[0, 1].set_ylabel('Среднее значение')
        
        # Box plot для первого признака
        if len(feature_names) > 0:
            df.boxplot(column=feature_names[0], by='Кластер', ax=axes[1, 0])
            axes[1, 0].set_title(f'Распределение {feature_names[0]} по кластерам', fontsize=12, fontweight='bold')
        
        # Heatmap средних значений
        if len(feature_names) > 1:
            mean_matrix = df.groupby('Кластер')[feature_names].mean()
            sns.heatmap(mean_matrix, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[1, 1])
            axes[1, 1].set_title('Средние значения признаков по кластерам', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return fig, cluster_stats