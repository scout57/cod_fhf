 
import argparse
import pandas as pd
from catboost import CatBoostRegressor, Pool, cv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os

from target import DB_2_FOLDER
from target import TARGET_COL


# Основная функция
def predict(model, serial):

    # Загрузка и подготовка данных
    file_path = f'{DB_2_FOLDER}/{model}.csv'
    print(f"Loading file from path: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return -1
    
    df = pd.read_csv(file_path)

    # Удаление ненужных колонок
    columns_to_drop = ['date', 'serial_number', 'failure', 'pod_id', 'vault_id']
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Обработка категориальных признаков
    categorical_features = ['model']
    df[categorical_features] = df[categorical_features].astype('category')

    # Определение целевой переменной и признаков
    df = df[df[TARGET_COL].notna()]  # Удаление строк с отсутствующим target
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]
#    X['date'] = (pd.to_datetime(X['date']) - pd.to_datetime('2000-01-01')).dt.days

    # Разделение выборки на обучающую и тестовую в соотношении 80:20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Настройка модели и параметров
    model = CatBoostRegressor(
        iterations=500,  # Максимальное количество итераций
        learning_rate=0.1,
        depth=8,
        loss_function='RMSE',
        early_stopping_rounds=50,  # Остановка обучения при отсутствии улучшений
        verbose=100
    )

    # Подготовка данных для CatBoost
    train_data = Pool(data=X_train, label=y_train, cat_features=categorical_features)

    # Кросс-валидация для поиска лучших параметров
    cv_data = cv(
        params=model.get_params(),
        pool=train_data,
        fold_count=3,  # Используем 3 фолда для кросс-валидации
        shuffle=True,
        partition_random_seed=42,  # Фиксируем seed для воспроизводимости
        plot=True
    )

    # Получение лучших параметров по результатам кросс-валидации
    best_iteration = np.argmin(cv_data['test-RMSE-mean'])
    best_params = model.get_params()
    best_params['iterations'] = best_iteration

    # Обучение финальной модели с оптимальными параметрами
    model_final = CatBoostRegressor(**best_params)
    model_final.fit(X_train, y_train, cat_features=categorical_features)

    # Получение и обработка важности признаков
    feature_importances = model_final.get_feature_importance(Pool(X_train, label=y_train, cat_features=categorical_features))
    feature_names = X_train.columns

    important_features = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importances
    }).sort_values(by='Importance', ascending=False)

    # Визуализация важности признаков
    plt.figure(figsize=(10, 8))
    plt.barh(important_features['Feature'], important_features['Importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.title('Feature Importance')
    plt.gca().invert_yaxis()
    plt.show()

    # Прогноз для новой записи
    df = pd.read_csv(file_path)
    filtered_df = df[df['serial_number'] == serial].copy()

    filtered_df.loc[:, 'date'] = pd.to_datetime(filtered_df['date'])
    latest_record = filtered_df.sort_values(by='date')

#    latest_record['date'] = (latest_record['date'] - pd.to_datetime('2000-01-01')).days
    latest_record = latest_record.drop(['serial_number', 'failure'], errors='ignore')

    

    X_new = pd.DataFrame(latest_record)
    X_new['model'] = X_new['model'].astype('category')
#    X_new['date'] = X_new['date'].astype(int)

    X_new = X_new.drop(columns=['date', 'serial_number', 'failure', 'pod_id', 'vault_id'], errors='ignore')

    # Прогнозирование
    prediction = model_final.predict(X_new)
    prediction = np.maximum(prediction, 0)  # Применение ограничения для неотрицательных значений

    return prediction



