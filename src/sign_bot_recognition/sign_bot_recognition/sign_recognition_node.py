import os
import pickle
import cv2
import numpy as np
import mediapipe as mp
import rclpy
from rclpy.node import Node


class SignRecognitionNode(Node):
    def __init__(self):
        super().__init__('sign_recognition_node')
        self.get_logger().info("Sign Recognition Node started!")

        # Parameters for model and Mediapipe setup
        self.model_path = "/home/pepper/sign_bot_neura_challenge/model/trained_model.pkl"  # Path to the trained model
        self.min_detection_confidence = 0.5
        self.min_tracking_confidence = 0.5
        self.confidence_threshold = 0.5  # Minimum confidence required for recognizing a sign

        # Verify and load the trained model
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at {self.model_path}. Please train a model first.")

        self.get_logger().info(f"Loading model from: {self.model_path}")

        with open(self.model_path, 'rb') as model_file:
            self.model = pickle.load(model_file)

        self.get_logger().info("Model loaded successfully!")

        # MediaPipe setup
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils

        # Start recognition
        self.capture_and_recognize()

    def capture_and_recognize(self):
        """
        Captures real-time video input from a webcam and recognizes the sign in the video stream.
        """
        self.get_logger().info("Starting webcam feed... Press 'q' to quit.")

        cap = cv2.VideoCapture(0)  # Open the webcam feed

        with self.mp_holistic.Holistic(
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
        ) as holistic:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    self.get_logger().error("Failed to capture video frame. Exiting.")
                    break

                # Flip the frame horizontally for a mirror-like effect
                frame = cv2.flip(frame, 1)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Process the video frame using MediaPipe
                results = holistic.process(image)
                image.flags.writeable = True

                # Extract hand landmarks (left + right hand only)
                landmarks = self.extract_landmarks(results)

                if landmarks:
                    # Recognize the sign based on the hand landmark data
                    prediction, confidence = self.recognize_sign(landmarks)

                    if confidence >= self.confidence_threshold:  # Only accept predictions with >= 75% confidence
                        # Display the recognized sign on the video feed
                        cv2.putText(frame, f"Sign: {prediction}", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    else:
                        # Display "unrecognized sign" for low confidence
                        cv2.putText(frame, "Unrecognized Sign", (10, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    # Case when neither hand landmarks are properly detected
                    cv2.putText(frame, "Hands not fully visible!", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                # Draw hand landmarks for visual feedback
                self.mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)
                self.mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)

                # Show the frame
                cv2.imshow('Sign Recognition', frame)

                # Press 'q' to quit the GUI
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.get_logger().info("Exiting webcam feed.")
                    break

        cap.release()
        cv2.destroyAllWindows()

    def recognize_sign(self, landmarks):
        """
        Uses the trained model to predict the sign based on the hand landmarks.

        :param landmarks: Flattened hand landmark list (left + right).
        :return: Tuple (Predicted sign label, Confidence) or ("Unrecognized Sign", 0).
        """
        # If no landmarks are detected, return None
        if len(landmarks) == 0:
            return "Unrecognized Sign", 0

        # Prepare input data for the model
        landmarks = np.array(landmarks).reshape(1, -1)  # Reshape for single sample prediction

        # Perform prediction with confidence checks
        try:
            probabilities = self.model.predict_proba(landmarks)[0]  # Get class probabilities
            max_confidence = np.max(probabilities)  # Max confidence score
            predicted_label = self.model.classes_[np.argmax(probabilities)]  # Predicted class label

            # Return the prediction only if confidence is >= 75%
            if max_confidence >= self.confidence_threshold:
                return predicted_label, max_confidence
            else:
                return "Unrecognized Sign", max_confidence
        except Exception as e:
            self.get_logger().error(f"Failed to predict sign: {str(e)}")
            return "Unrecognized Sign", 0

    @staticmethod
    def extract_landmarks(results):
        """
        Extracts and flattens only left hand and right hand landmarks.

        :param results: Mediapipe Holistic results object containing the hand landmarks.
        :return: Flattened list of 3D landmarks ([x, y, z] for all landmarks) or None if no hands are found.
        """

        def flatten_hand(landmarks):
            if landmarks:
                return [coord for lm in landmarks.landmark for coord in (lm.x, lm.y, lm.z)]
            return [0] * 63  # Return zero-filled list if hand landmarks are not detected

        # Extract left hand and right hand landmarks
        left_hand = flatten_hand(results.left_hand_landmarks)
        right_hand = flatten_hand(results.right_hand_landmarks)

        # Combine left and right hand landmarks
        full_landmark = left_hand + right_hand

        # If both hands are missing, treat as invalid data
        if sum(full_landmark) == 0:
            return None

        return full_landmark


def main(args=None):
    rclpy.init(args=args)
    node = SignRecognitionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
