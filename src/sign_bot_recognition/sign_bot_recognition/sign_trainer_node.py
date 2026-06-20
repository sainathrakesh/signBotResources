import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)
import rclpy
from rclpy.node import Node

PLOT_DIR = "/home/pepper/sign_bot_neura_challenge/training_plots"
os.makedirs(PLOT_DIR, exist_ok=True)

class SignTrainerNode(Node):
    def __init__(self):
        super().__init__('sign_trainer_node')
        self.get_logger().info("Sign Trainer Node started!")

        self.data_dir = "/home/pepper/sign_bot_neura_challenge/collected_data"
        self.model_save_path = "/home/pepper/sign_bot_neura_challenge/model/trained_model.pkl"

        self.get_logger().info("Processing data and training the model...")
        try:
            dataset, labels = self.process_data()
            X_train, X_test, y_train, y_test = self.split_data(dataset, labels)
            self.plot_split_pie(len(X_train), len(X_test))

            model = self.train_model(X_train, y_train)
            self.evaluate_model(model, X_test, y_test)
            self.save_model(model)

            self.get_logger().info("Model training and evaluation completed successfully!")
        except Exception as e:
            self.get_logger().error(f"Error during training: {str(e)}")

    def process_data(self):
        if not os.path.exists(self.data_dir):
            raise RuntimeError(f"Data path '{self.data_dir}' does not exist.")

        signs = os.listdir(self.data_dir)
        dataset, labels = [], []

        for sign in signs:
            sign_folder = os.path.join(self.data_dir, sign)
            if not os.path.isdir(sign_folder):
                continue

            for file_name in os.listdir(sign_folder):
                file_path = os.path.join(sign_folder, file_name)
                if not file_path.endswith('.json'):
                    continue
                with open(file_path, 'r') as f:
                    video_data = json.load(f)
                    for frame in video_data:
                        landmarks = self.extract_landmarks(frame)
                        dataset.append(landmarks)
                        labels.append(sign)

        self.plot_class_distribution(labels)
        self.get_logger().info(f"Processed {len(dataset)} frames from {len(signs)} signs.")
        return np.array(dataset), np.array(labels)

    def extract_landmarks(self, frame):
        def flatten(landmarks):
            if not landmarks:
                return [0] * 63
            return [coord for lm in landmarks for coord in (lm['x'], lm['y'], lm['z'])]

        left_hand = flatten(frame.get("left_hand"))
        right_hand = flatten(frame.get("right_hand"))
        return left_hand + right_hand

    def split_data(self, dataset, labels):
        X_train, X_test, y_train, y_test = train_test_split(
            dataset, labels, test_size=0.2, random_state=42, stratify=labels
        )
        self.get_logger().info(f"Dataset split: {len(X_train)} train, {len(X_test)} test.")
        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        self.get_logger().info("Training RandomForest model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_test, y_test):
        y_pred = model.predict(X_test)
        self.plot_confusion_matrix(y_test, y_pred, model.classes_)
        self.plot_metrics_bar(y_test, y_pred, model.classes_)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        self.get_logger().info(f"Accuracy:  {accuracy:.4f}\nPrecision: {precision:.4f}\nRecall:    {recall:.4f}\nF1-Score:  {f1:.4f}")

    def save_model(self, model):
        import pickle
        model_dir = os.path.dirname(self.model_save_path)
        os.makedirs(model_dir, exist_ok=True)
        with open(self.model_save_path, 'wb') as f:
            pickle.dump(model, f)

    def plot_class_distribution(self, labels):
        counts = Counter(labels)
        classes, values = zip(*sorted(counts.items()))
        plt.figure(figsize=(14, 6))
        plt.bar(classes, values, color='mediumpurple')
        plt.xticks(rotation=90)
        plt.ylabel("Frames")
        plt.title("Class Distribution")
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, "class_distribution.png"))
        plt.close()

    def plot_split_pie(self, train_size, test_size):
        plt.figure(figsize=(5, 5))
        plt.pie([train_size, test_size], labels=['Train', 'Test'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
        plt.title("Train/Test Split")
        plt.savefig(os.path.join(PLOT_DIR, "train_test_split.png"))
        plt.close()

    def plot_confusion_matrix(self, y_true, y_pred, class_names):
        cm = confusion_matrix(y_true, y_pred, labels=class_names)
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        plt.figure(figsize=(12, 9))
        sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="viridis", xticklabels=class_names, yticklabels=class_names)
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Normalized Confusion Matrix")
        plt.xticks(rotation=90)
        plt.savefig(os.path.join(PLOT_DIR, "confusion_matrix.png"))
        plt.close()

    def plot_metrics_bar(self, y_true, y_pred, class_names):
        precision = precision_score(y_true, y_pred, average=None, labels=class_names)
        recall = recall_score(y_true, y_pred, average=None, labels=class_names)
        f1 = f1_score(y_true, y_pred, average=None, labels=class_names)

        x = np.arange(len(class_names))
        width = 0.25
        plt.figure(figsize=(14, 6))
        plt.bar(x - width, precision, width, label='Precision')
        plt.bar(x, recall, width, label='Recall')
        plt.bar(x + width, f1, width, label='F1 Score')

        plt.xticks(x, class_names, rotation=90)
        plt.ylim(0, 1)
        plt.ylabel("Score")
        plt.title("Per-Class Evaluation Metrics")
        plt.legend()
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, "metrics_bar.png"))
        plt.close()


def main(args=None):
    rclpy.init(args=args)
    node = SignTrainerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

