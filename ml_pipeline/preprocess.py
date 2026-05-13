from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Import the AdvancedFeatureEngineer from its dedicated module
from feature_engineering import AdvancedFeatureEngineer

CATEGORICAL_COLS = ["protocol_type", "service", "flag"]


def preprocess_data(df_train, df_test):
    print("Preprocessing data and building Feature Engineering Pipeline...")

    columns = df_train.columns.tolist()
    numeric_cols = [c for c in columns if c not in CATEGORICAL_COLS + ["label", "difficulty_level"]]
    # Add our new engineered column so the StandardScaler scales it too!
    if "byte_ratio" not in numeric_cols:
        numeric_cols.append("byte_ratio")

    # Map 'normal' -> 0, all attacks -> 1 (Anomaly)
    y_train = (df_train["label"] != "normal").astype(int)
    y_test = (df_test["label"] != "normal").astype(int)

    X_train = df_train.drop(columns=["label", "difficulty_level"])
    X_test = df_test.drop(columns=["label", "difficulty_level"])

    # ColumnTransformer: scale numerics, one-hot encode categoricals
    col_transformer = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_COLS)
        ])

    # Unified MLOps Pipeline: Feature Engineering → Scaling/Encoding
    preprocessor = Pipeline([
        ('feature_engineer', AdvancedFeatureEngineer()),
        ('transformer', col_transformer)
    ])

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    return X_train_processed, X_test_processed, y_train, y_test, preprocessor
