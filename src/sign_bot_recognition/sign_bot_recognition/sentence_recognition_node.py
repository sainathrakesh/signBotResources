import os
import pickle
import cv2
import numpy as np
import mediapipe as mp
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SentenceRecognitionNode(Node):
    def __init__(self):
        super().__init__('sentence_recognition_node')
        self.get_logger().info("Sentence Recognition Node started!")

        self.publisher_ = self.create_publisher(String, '/finalized_sentence', 10)

        self.model_path = "/home/pepper/sign_bot_neura_challenge/model/trained_model.pkl"
        self.confidence_threshold = 0.5

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at {self.model_path}")
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)

        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils

        self.sentence = []
        self.last_prediction = ""
        self.frames_since_last_change = 0
        self.word_hold_threshold = 15
        self.last_landmark_time = time.time()
        self.no_hand_timeout = 3

        self.capture_and_recognize()

    def capture_and_recognize(self):
        self.get_logger().info("Starting webcam. Press 'q' to quit.")
        cap = cv2.VideoCapture(0)

        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    self.get_logger().error("Failed to read from webcam.")
                    break

                frame = cv2.flip(frame, 1)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = holistic.process(image)
                image.flags.writeable = True

                landmarks = self.extract_landmarks(results)
                current_time = time.time()

                if landmarks:
                    self.last_landmark_time = current_time
                    prediction, confidence = self.recognize_sign(landmarks)

                    if confidence >= self.confidence_threshold:
                        if prediction == self.last_prediction:
                            self.frames_since_last_change += 1
                        else:
                            self.frames_since_last_change = 0
                            self.last_prediction = prediction

                        if self.frames_since_last_change == self.word_hold_threshold:
                            if not self.sentence or self.sentence[-1] != prediction:
                                self.sentence.append(prediction)
                            self.frames_since_last_change = 0

                        cv2.putText(frame, f"Sign: {prediction}", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Unrecognized Sign", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                else:
                    time_diff = current_time - self.last_landmark_time
                    if time_diff > self.no_hand_timeout and self.sentence:
                        finalized = " ".join(self.sentence).strip().lower()
                        self.get_logger().info(f"Finalized Sentence: {finalized}")
                        msg = String()
                        msg.data = finalized
                        self.publisher_.publish(msg)
                        with open("final_sentences.txt", "a") as f:
                            f.write(finalized + "\n")
                        self.sentence = []
                        self.last_prediction = ""
                        self.frames_since_last_change = 0
                        self.last_landmark_time = current_time
                    else:
                        cv2.putText(frame, "Hands not fully visible!", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                self.mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)
                self.mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)

                cv2.putText(frame, "Sentence: " + " ".join(self.sentence[-10:]), (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                cv2.imshow("Sentence Recognition", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.get_logger().info("Quitting webcam.")
                    break

        cap.release()
        cv2.destroyAllWindows()

    def recognize_sign(self, landmarks):
        if not landmarks:
            return "Unrecognized Sign", 0
        landmarks = np.array(landmarks).reshape(1, -1)
        try:
            probs = self.model.predict_proba(landmarks)[0]
            confidence = np.max(probs)
            label = self.model.classes_[np.argmax(probs)]
            if confidence >= self.confidence_threshold:
                return label, confidence
            else:
                return "Unrecognized Sign", confidence
        except Exception as e:
            self.get_logger().error(f"Prediction error: {e}")
            return "Unrecognized Sign", 0

    @staticmethod
    def extract_landmarks(results):
        def flatten_hand(lm):
            if lm:
                return [v for point in lm.landmark for v in (point.x, point.y, point.z)]
            return [0.0] * 63

        left = flatten_hand(results.left_hand_landmarks)
        right = flatten_hand(results.right_hand_landmarks)
        full = left + right
        return full if sum(full) > 0 else None


def main(args=None):
    rclpy.init(args=args)
    node = SentenceRecognitionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
