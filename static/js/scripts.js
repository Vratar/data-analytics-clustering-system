// Основные функции для взаимодействия с пользователем

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initializeFileUpload();
    initializeDataTables();
    initializeClusteringControls();
    initializeCharts();
});

// Функции для загрузки файлов
function initializeFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    
    if (dropZone) {
        // Drag and drop functionality
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                document.getElementById('uploadForm').submit();
            }
        });
        
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Live file name display
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Файл не выбран';
            const fileNameDisplay = document.getElementById('fileName');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    }
}

// Инициализация таблиц данных
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Простая сортировка таблиц
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.addEventListener('click', function() {
                const columnIndex = Array.from(this.parentElement.children).indexOf(this);
                const isAscending = !this.classList.contains('asc');
                
                // Сброс всех сортировок
                headers.forEach(h => {
                    h.classList.remove('asc', 'desc');
                });
                
                // Установка направления сортировки
                this.classList.add(isAscending ? 'asc' : 'desc');
                
                // Сортировка таблицы
                sortTable(table, columnIndex, isAscending);
            });
        });
    });
}

// Функция сортировки таблицы
function sortTable(table, column, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.children[column].textContent.trim();
        const bVal = b.children[column].textContent.trim();
        
        // Попытка численного сравнения
        const aNum = parseFloat(aVal.replace(',', '.'));
        const bNum = parseFloat(bVal.replace(',', '.'));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }
        
        // Строковое сравнение
        return ascending 
            ? aVal.localeCompare(bVal, undefined, {numeric: true})
            : bVal.localeCompare(aVal, undefined, {numeric: true});
    });
    
    // Очистка и перезапись таблицы
    rows.forEach(row => tbody.appendChild(row));
}

// Функции для кластеризации
function initializeClusteringControls() {
    // Динамическое изменение параметров алгоритма
    const algorithmSelect = document.getElementById('algorithmSelect');
    const paramsContainer = document.getElementById('algorithmParams');
    
    if (algorithmSelect && paramsContainer) {
        algorithmSelect.addEventListener('change', function() {
            updateAlgorithmParams(this.value);
        });
        
        // Инициализация параметров
        updateAlgorithmParams(algorithmSelect.value);
    }
    
    // Кнопка для определения оптимального количества кластеров
    const optimizeBtn = document.getElementById('optimizeClustersBtn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizeClusters);
    }
    
    // Валидация формы кластеризации
    const clusteringForm = document.getElementById('clusteringForm');
    if (clusteringForm) {
        clusteringForm.addEventListener('submit', function(e) {
            const selectedColumns = document.querySelectorAll('input[name="columns"]:checked');
            if (selectedColumns.length === 0) {
                e.preventDefault();
                alert('Пожалуйста, выберите хотя бы один столбец для кластеризации');
                return false;
            }
            
            const algorithm = document.getElementById('algorithmSelect').value;
            const nClusters = document.getElementById('nClusters').value;
            
            if (algorithm !== 'dbscan' && (nClusters < 2 || nClusters > 20)) {
                e.preventDefault();
                alert('Количество кластеров должно быть от 2 до 20');
                return false;
            }
        });
    }
}

// Обновление параметров алгоритма
function updateAlgorithmParams(algorithm) {
    const paramsContainer = document.getElementById('algorithmParams');
    if (!paramsContainer) return;
    
    let paramsHTML = '';
    
    switch(algorithm) {
        case 'kmeans':
            paramsHTML = `
                <div class="form-group">
                    <label for="nClusters">Количество кластеров:</label>
                    <input type="number" id="nClusters" name="nClusters" 
                           min="2" max="20" value="3" class="form-control">
                </div>
                <div class="form-group">
                    <label for="maxIter">Максимальное число итераций:</label>
                    <input type="number" id="maxIter" name="maxIter" 
                           min="100" max="1000" value="300" class="form-control">
                </div>
            `;
            break;
            
        case 'dbscan':
            paramsHTML = `
                <div class="form-group">
                    <label for="eps">Радиус окрестности (eps):</label>
                    <input type="number" id="eps" name="eps" 
                           min="0.1" max="10" step="0.1" value="0.5" class="form-control">
                </div>
                <div class="form-group">
                    <label for="minSamples">Минимальное число точек:</label>
                    <input type="number" id="minSamples" name="minSamples" 
                           min="2" max="20" value="5" class="form-control">
                </div>
            `;
            break;
            
        case 'hierarchical':
            paramsHTML = `
                <div class="form-group">
                    <label for="nClusters">Количество кластеров:</label>
                    <input type="number" id="nClusters" name="nClusters" 
                           min="2" max="20" value="3" class="form-control">
                </div>
                <div class="form-group">
                    <label for="linkage">Метод связи:</label>
                    <select id="linkage" name="linkage" class="form-control">
                        <option value="ward">Ward</option>
                        <option value="complete">Полная связь</option>
                        <option value="average">Средняя связь</option>
                        <option value="single">Одиночная связь</option>
                    </select>
                </div>
            `;
            break;
            
        case 'gmm':
            paramsHTML = `
                <div class="form-group">
                    <label for="nClusters">Количество компонент:</label>
                    <input type="number" id="nClusters" name="nClusters" 
                           min="2" max="20" value="3" class="form-control">
                </div>
                <div class="form-group">
                    <label for="covarianceType">Тип ковариации:</label>
                    <select id="covarianceType" name="covarianceType" class="form-control">
                        <option value="full">Полная</option>
                        <option value="tied">Связанная</option>
                        <option value="diag">Диагональная</option>
                        <option value="spherical">Сферическая</option>
                    </select>
                </div>
            `;
            break;
            
        case 'spectral':
            paramsHTML = `
                <div class="form-group">
                    <label for="nClusters">Количество кластеров:</label>
                    <input type="number" id="nClusters" name="nClusters" 
                           min="2" max="20" value="3" class="form-control">
                </div>
                <div class="form-group">
                    <label for="affinity">Метод сходства:</label>
                    <select id="affinity" name="affinity" class="form-control">
                        <option value="rbf">RBF</option>
                        <option value="nearest_neighbors">Ближайшие соседи</option>
                    </select>
                </div>
            `;
            break;
    }
    
    paramsContainer.innerHTML = paramsHTML;
}

// Оптимизация количества кластеров
function optimizeClusters() {
    const algorithm = document.getElementById('algorithmSelect').value;
    const selectedColumns = Array.from(document.querySelectorAll('input[name="columns"]:checked'))
        .map(cb => cb.value);
    
    if (selectedColumns.length === 0) {
        alert('Выберите столбцы для анализа');
        return;
    }
    
    // Показать индикатор загрузки
    const btn = document.getElementById('optimizeClustersBtn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Анализ...';
    
    // Отправка запроса на сервер
    fetch('/api/optimize_clusters', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            algorithm: algorithm,
            columns: selectedColumns,
            max_clusters: 10
        })
    })
    .then(response => response.json())
    .then(data => {
        // Обновить поле количества кластеров
        if (data.optimal_clusters) {
            document.getElementById('nClusters').value = data.optimal_clusters;
            showNotification(`Рекомендуемое количество кластеров: ${data.optimal_clusters}`, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при оптимизации кластеров', 'error');
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = originalText;
    });
}

// Инициализация графиков
function initializeCharts() {
    // Инициализация всех графиков на странице
    const chartElements = document.querySelectorAll('.chart-container');
    
    chartElements.forEach(container => {
        const chartType = container.dataset.chartType;
        const dataUrl = container.dataset.dataUrl;
        
        if (dataUrl) {
            loadChartData(container, chartType, dataUrl);
        }
    });
}

// Загрузка данных для графиков
function loadChartData(container, chartType, dataUrl) {
    fetch(dataUrl)
        .then(response => response.json())
        .then(data => {
            renderChart(container, chartType, data);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            container.innerHTML = '<p class="error">Ошибка загрузки данных для графика</p>';
        });
}

// Отрисовка графиков
function renderChart(container, chartType, data) {
    const canvas = document.createElement('canvas');
    container.innerHTML = '';
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    switch(chartType) {
        case 'bar':
            renderBarChart(ctx, data);
            break;
        case 'line':
            renderLineChart(ctx, data);
            break;
        case 'pie':
            renderPieChart(ctx, data);
            break;
        case 'scatter':
            renderScatterChart(ctx, data);
            break;
    }
}

// Пример реализации bar chart
function renderBarChart(ctx, data) {
    // Простая реализация bar chart
    const labels = data.labels || [];
    const values = data.values || [];
    
    const maxValue = Math.max(...values);
    const barWidth = ctx.canvas.width / labels.length - 10;
    
    ctx.fillStyle = '#3498db';
    
    labels.forEach((label, i) => {
        const barHeight = (values[i] / maxValue) * (ctx.canvas.height - 50);
        const x = i * (barWidth + 10) + 5;
        const y = ctx.canvas.height - barHeight - 30;
        
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Подписи
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(label, x + barWidth/2, ctx.canvas.height - 10);
        ctx.fillText(values[i], x + barWidth/2, y - 10);
    });
}

// Сохранение результатов
function saveResults() {
    const saveBtn = document.getElementById('saveResultsBtn');
    const originalText = saveBtn.innerHTML;
    
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
    
    fetch('/save_results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Результаты успешно сохранены!', 'success');
            
            // Предложить скачать файлы
            if (confirm('Хотите скачать сохраненные файлы?')) {
                window.location.href = `/download/${data.results_file}`;
            }
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        showNotification(`Ошибка сохранения: ${error.message}`, 'error');
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    });
}

// Уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Экспорт функций для использования в других скриптах
window.DataAnalytics = {
    sortTable,
    updateAlgorithmParams,
    optimizeClusters,
    saveResults,
    showNotification
};