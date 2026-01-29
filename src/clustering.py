import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA

class ClusteringAlgorithms:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def apply_clustering(self, data, algorithm='kmeans', n_clusters=3, **kwargs):
        """Применение алгоритма кластеризации"""
        
        # Масштабирование данных
        data_scaled = self.scaler.fit_transform(data)
        
        results = {}
        
        if algorithm == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42, **kwargs)
            labels = model.fit_predict(data_scaled)
            results['model'] = model
            results['centroids'] = model.cluster_centers_
        
        elif algorithm == 'dbscan':
            eps = kwargs.get('eps', 0.5)
            min_samples = kwargs.get('min_samples', 5)
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(data_scaled)
            results['model'] = model
        
        elif algorithm == 'hierarchical':
            linkage = kwargs.get('linkage', 'ward')
            model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
            labels = model.fit_predict(data_scaled)
            results['model'] = model
        
        elif algorithm == 'gmm':
            model = GaussianMixture(n_components=n_clusters, random_state=42, **kwargs)
            labels = model.fit_predict(data_scaled)
            results['model'] = model
            results['probabilities'] = model.predict_proba(data_scaled)
        
        elif algorithm == 'spectral':
            model = SpectralClustering(n_clusters=n_clusters, random_state=42, **kwargs)
            labels = model.fit_predict(data_scaled)
            results['model'] = model
        
        else:
            raise ValueError(f"Алгоритм {algorithm} не поддерживается")
        
        results['labels'] = labels
        results['n_clusters'] = len(np.unique(labels[labels != -1]))  # исключаем шум для DBSCAN
        
        # Вычисление метрик качества кластеризации
        if len(np.unique(labels)) > 1:
            try:
                results['metrics'] = self.calculate_metrics(data_scaled, labels)
            except:
                results['metrics'] = {}
        
        return results
    
    def calculate_metrics(self, data, labels):
        """Вычисление метрик качества кластеризации"""
        metrics = {}
        
        if len(np.unique(labels)) > 1:
            try:
                metrics['silhouette_score'] = round(silhouette_score(data, labels), 4)
            except:
                metrics['silhouette_score'] = None
            
            try:
                metrics['calinski_harabasz_score'] = round(calinski_harabasz_score(data, labels), 4)
            except:
                metrics['calinski_harabasz_score'] = None
            
            try:
                metrics['davies_bouldin_score'] = round(davies_bouldin_score(data, labels), 4)
            except:
                metrics['davies_bouldin_score'] = None
        
        return metrics
    
    def find_optimal_clusters(self, data, algorithm='kmeans', max_clusters=10):
        """Поиск оптимального количества кластеров"""
        data_scaled = self.scaler.fit_transform(data)
        scores = []
        
        for n in range(2, max_clusters + 1):
            try:
                results = self.apply_clustering(data, algorithm, n_clusters=n)
                if 'metrics' in results and results['metrics'].get('silhouette_score'):
                    scores.append({
                        'n_clusters': n,
                        'silhouette': results['metrics']['silhouette_score'],
                        'calinski_harabasz': results['metrics'].get('calinski_harabasz_score'),
                        'davies_bouldin': results['metrics'].get('davies_bouldin_score')
                    })
            except:
                continue
        
        return scores
    
    def reduce_dimensionality(self, data, n_components=2):
        """Уменьшение размерности данных"""
        pca = PCA(n_components=n_components)
        return pca.fit_transform(data)