# src/ml/train.py
import os
import logging
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import lightgbm as lgb
from sklearn.metrics import classification_report, accuracy_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-ML-Train")

def run_production_model_training():
    logger.info("Initializing LightGBM multiclass model optimization pipeline sequence...")
    data_path = os.path.join("data", "raw", "financial_phrasebank.csv")
    
    if not os.path.exists(data_path):
        logger.critical(f"Halted: Training baseline files missing at destination volume: {data_path}")
        return

    df = pd.read_csv(data_path, names=["sentiment", "text"], encoding="latin-1")
    df = df.dropna().reset_index(drop=True)
    logger.info(f"Training rows successfully ingested into DataFrame container: {len(df)}")

    # 1. Feature Engineering
    tfidf = TfidfVectorizer(max_features=2000, stop_words='english', ngram_range=(1, 2))
    X = tfidf.fit_transform(df["text"]).toarray()
    
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["sentiment"])

    # 2. Imbalance Resolution via SMOTE
    logger.info("Re-balancing dataset row matrices via SMOTE over-sampling algorithms...")
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
    )

    train_data_set = lgb.Dataset(X_train, label=y_train)
    test_data_set = lgb.Dataset(X_test, label=y_test, reference=train_data_set)

    params = {
        'objective': 'multiclass',
        'num_class': len(encoder.classes_),
        'metric': 'multi_logloss',
        'boosting_type': 'gbdt',
        'learning_rate': 0.1,
        'verbosity': -1,
        'n_jobs': -1
    }

    # 3. Model Training
    logger.info("Executing gradient boosting training optimization iterations...")
    model = lgb.train(params, train_data_set, num_boost_round=150, valid_sets=[test_data_set])
    
    # 4. Serialize and Save Pipeline Weights (Populates the models folder)
    target_models_dir = os.path.join("src", "ml", "models")
    os.makedirs(target_models_dir, exist_ok=True)
    logger.info(f"Persisting trained structural assets to destination volume folder: [{target_models_dir}]")
    
    model.save_model(os.path.join(target_models_dir, "lightgbm_finrisk.model"))
    with open(os.path.join(target_models_dir, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    with open(os.path.join(target_models_dir, "label_encoder.pkl"), "wb") as f:
        pickle.dump(encoder, f)
    logger.info("Pipeline serialization complete. Models folder is successfully populated.")

    # 5. Evaluate Performance Metrics
    y_pred = np.argmax(model.predict(X_test), axis=1)
    logger.info(f"Model optimization complete. Validation Target Accuracy Score: {accuracy_score(y_test, y_pred):.4f}")
    print("\n--- Compliance Classifier Matrix Performance Report ---")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))

if __name__ == "__main__":
    run_production_model_training()
