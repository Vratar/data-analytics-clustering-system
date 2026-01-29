import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import json
from datetime import datetime

from src.data_processor import DataProcessor
from src.clustering import ClusteringAlgorithms
from src.visualization import Visualizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['RESULTS_FOLDER'] = 'results/'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='Файл не выбран')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('upload.html', error='Файл не выбран')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store file info in session
            session['filepath'] = filepath
            session['filename'] = filename
            
            return redirect(url_for('show_statistics'))
    
    return render_template('upload.html')

@app.route('/statistics')
def show_statistics():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return redirect(url_for('upload_file'))
    
    try:
        processor = DataProcessor(filepath)
        stats = processor.get_basic_statistics()
        missing_stats = processor.get_missing_values_statistics()
        
        return render_template('statistics.html', 
                             stats=stats, 
                             missing_stats=missing_stats,
                             filename=session.get('filename'))
    except Exception as e:
        return render_template('statistics.html', error=str(e))

@app.route('/api/statistics')
def api_statistics():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'Файл не найден'}), 404
    
    try:
        processor = DataProcessor(filepath)
        stats = processor.get_basic_statistics()
        missing_stats = processor.get_missing_values_statistics()
        outliers = processor.detect_outliers()
        
        return jsonify({
            'basic_statistics': stats,
            'missing_values': missing_stats,
            'outliers': outliers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preprocessing', methods=['GET', 'POST'])
def preprocessing():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return redirect(url_for('upload_file'))
    
    processor = DataProcessor(filepath)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'fill_missing':
            method = request.form.get('method')
            columns = request.form.getlist('columns')
            
            if not columns:
                columns = None
            
            processor.fill_missing_values(method=method, columns=columns)
            
            # Save processed data
            processed_filename = f"processed_{session.get('filename')}"
            processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            processor.save_data(processed_path)
            session['processed_filepath'] = processed_path
            
        elif action == 'remove_outliers':
            method = request.form.get('outlier_method')
            processor.remove_outliers(method=method)
            
            processed_filename = f"processed_{session.get('filename')}"
            processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            processor.save_data(processed_path)
            session['processed_filepath'] = processed_path
        
        return redirect(url_for('preprocessing'))
    
    # Get data for display
    missing_stats = processor.get_missing_values_statistics()
    outliers_info = processor.detect_outliers()
    columns = processor.data.columns.tolist()
    
    return render_template('preprocessing.html',
                         missing_stats=missing_stats,
                         outliers_info=outliers_info,
                         columns=columns,
                         filename=session.get('filename'))

@app.route('/clustering', methods=['GET', 'POST'])
def clustering():
    filepath = session.get('processed_filepath', session.get('filepath'))
    if not filepath or not os.path.exists(filepath):
        return redirect(url_for('upload_file'))
    
    processor = DataProcessor(filepath)
    columns = processor.data.columns.tolist()
    
    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        algorithm = request.form.get('algorithm')
        n_clusters = request.form.get('n_clusters', type=int)
        
        if not selected_columns:
            return render_template('clustering.html', 
                                 columns=columns,
                                 error='Выберите хотя бы один столбец для кластеризации')
        
        # Perform clustering
        clusterer = ClusteringAlgorithms()
        data_for_clustering = processor.data[selected_columns]
        
        # Handle missing values if any
        if data_for_clustering.isnull().any().any():
            data_for_clustering = data_for_clustering.fillna(data_for_clustering.mean())
        
        # Apply clustering
        results = clusterer.apply_clustering(
            data=data_for_clustering,
            algorithm=algorithm,
            n_clusters=n_clusters
        )
        
        # Store results in session
        session['clustering_results'] = {
            'algorithm': algorithm,
            'n_clusters': n_clusters,
            'columns': selected_columns,
            'labels': results['labels'].tolist(),
            'metrics': results.get('metrics', {}),
            'data': data_for_clustering.values.tolist()
        }
        
        # Generate visualization
        visualizer = Visualizer()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_filename = f"clustering_{algorithm}_{timestamp}.png"
        viz_path = os.path.join(app.config['RESULTS_FOLDER'], viz_filename)
        
        # Select only numeric columns for visualization
        numeric_cols = data_for_clustering.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) >= 2:
            # Use first two numeric columns for 2D visualization
            visualizer.plot_clusters_2d(
                data=data_for_clustering[numeric_cols[:2]].values,
                labels=results['labels'],
                algorithm=algorithm,
                save_path=viz_path
            )
            session['visualization_path'] = viz_path
        
        return redirect(url_for('clustering_results'))
    
    return render_template('clustering.html', columns=columns)

@app.route('/results')
def clustering_results():
    results = session.get('clustering_results')
    viz_path = session.get('visualization_path')
    
    if not results:
        return redirect(url_for('clustering'))
    
    return render_template('results.html', 
                         results=results,
                         visualization_path=viz_path)

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

@app.route('/save_results', methods=['POST'])
def save_results():
    results = session.get('clustering_results')
    if not results:
        return jsonify({'error': 'Нет результатов для сохранения'}), 400
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save clustering results as CSV
        results_filename = f"clustering_results_{timestamp}.csv"
        results_path = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        
        # Create DataFrame with original data and cluster labels
        filepath = session.get('processed_filepath', session.get('filepath'))
        processor = DataProcessor(filepath)
        
        # Add cluster labels to data
        data_with_clusters = processor.data.copy()
        data_with_clusters['cluster'] = results['labels']
        
        # Save to CSV
        data_with_clusters.to_csv(results_path, index=False)
        
        # Save metrics as JSON
        metrics_filename = f"clustering_metrics_{timestamp}.json"
        metrics_path = os.path.join(app.config['RESULTS_FOLDER'], metrics_filename)
        
        with open(metrics_path, 'w') as f:
            json.dump(results['metrics'], f, indent=2)
        
        return jsonify({
            'success': True,
            'results_file': results_filename,
            'metrics_file': metrics_filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)