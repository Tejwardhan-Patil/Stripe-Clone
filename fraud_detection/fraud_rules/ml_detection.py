import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

class MLFraudDetection:
    def __init__(self, data_path: str):
        # Load data and initialize model variables
        self.data_path = data_path
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None

    def load_data(self):
        """Loads transaction data from CSV and splits into features and labels"""
        data = pd.read_csv(self.data_path)
        X = data.drop(columns=['is_fraud'])
        y = data['is_fraud']
        return X, y

    def preprocess_data(self, X):
        """Applies scaling to the feature set"""
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled

    def split_data(self, X, y):
        """Splits the dataset into training and testing sets"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    def train_model(self):
        """Trains the RandomForest model"""
        self.model.fit(self.X_train, self.y_train)
        print("Model training completed.")

    def evaluate_model(self):
        """Evaluates the model's performance on test data"""
        predictions = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, predictions)
        conf_matrix = confusion_matrix(self.y_test, predictions)
        report = classification_report(self.y_test, predictions)
        print(f"Accuracy: {accuracy:.4f}")
        print("Confusion Matrix:")
        print(conf_matrix)
        print("Classification Report:")
        print(report)

    def save_model(self, model_path: str):
        """Saves the trained model and scaler to disk"""
        joblib.dump(self.model, model_path + "_model.pkl")
        joblib.dump(self.scaler, model_path + "_scaler.pkl")
        print("Model and scaler saved successfully.")

    def load_model(self, model_path: str):
        """Loads a pre-trained model and scaler from disk"""
        self.model = joblib.load(model_path + "_model.pkl")
        self.scaler = joblib.load(model_path + "_scaler.pkl")
        print("Model and scaler loaded successfully.")

    def predict(self, new_data: pd.DataFrame):
        """Predicts fraud probability on new transaction data"""
        new_data_scaled = self.scaler.transform(new_data)
        predictions = self.model.predict(new_data_scaled)
        probabilities = self.model.predict_proba(new_data_scaled)
        return predictions, probabilities

if __name__ == "__main__":
    # Initialize fraud detection system
    detection = MLFraudDetection(data_path="transactions.csv")

    # Load and preprocess data
    X, y = detection.load_data()
    X_scaled = detection.preprocess_data(X)

    # Split the data
    detection.split_data(X_scaled, y)

    # Train the model
    detection.train_model()

    # Evaluate the model
    detection.evaluate_model()

    # Save the model
    detection.save_model(model_path="fraud_detection_model")

    # To make predictions with new data
    
    # Load the model for future predictions
    detection.load_model(model_path="fraud_detection_model")

    # New transaction data to predict
    new_transactions = pd.DataFrame({
        'transaction_amount': [100, 5000, 20000],
        'transaction_type': [1, 0, 1],  # Encoded values
        'merchant_id': [3, 12, 8],
        'user_id': [23, 45, 67],
        'country': [1, 0, 1]  # Encoded country codes
    })

    # Predict fraud on new data
    predictions, probabilities = detection.predict(new_transactions)
    print("Predictions:", predictions)
    print("Probabilities:", probabilities)