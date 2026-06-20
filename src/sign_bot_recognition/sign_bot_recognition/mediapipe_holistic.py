import cv2
import os
import mediapipe as mp
import json

# MediaPipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Directory for storing data
DATA_PATH = "collected_data"  # Base directory where data is saved
NUM_VIDEOS_PER_SIGN = 50  # Number of videos per sign
FPS = 30  # Assumes 30 FPS recording
DURATION_SECONDS = 4  # Video duration (4 seconds)

# Total frames to record (FPS * duration)
TOTAL_FRAMES = FPS * DURATION_SECONDS

# Create the data directory if it doesn't exist
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)


def save_landmarks_to_json(landmarks_list, file_path):
    """
    Saves the list of landmarks data to a JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(landmarks_list, f, indent=4)


def capture_landmarks_for_sign(sign_name, video_count):
    """
    Captures landmarks for frames of a 4-second video (30 FPS).
    Saves the data in JSON format for each video, excluding face landmarks.
    """
    cap = cv2.VideoCapture(0)  # Open the webcam (change index if needed)

    print(f"Get ready to record video {video_count + 1} for the sign: {sign_name}")
    print("Press `Enter` to start recording...")

    # Wait for the user to press "Enter"
    input()

    # Initialize Mediapipe Holistic
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        frame_count = 0
        video_landmarks = []  # Store frame-wise landmarks

        print(f"Recording video {video_count + 1} for the sign: {sign_name}...")

        while frame_count < TOTAL_FRAMES:  # Ensure it captures exactly 120 frames
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame!")
                break

            # Flip the frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process the frame using Mediapipe Holistic
            results = holistic.process(image)
            image.flags.writeable = True

            # Draw landmarks on the frame for feedback (optional for users to see in real-time)
            mp_drawing.draw_landmarks(image=frame, landmark_list=results.pose_landmarks,
                                      connections=mp_holistic.POSE_CONNECTIONS)
            mp_drawing.draw_landmarks(image=frame, landmark_list=results.left_hand_landmarks,
                                      connections=mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image=frame, landmark_list=results.right_hand_landmarks,
                                      connections=mp_holistic.HAND_CONNECTIONS)

            # Extract landmarks for the current frame
            def extract_coordinates(landmarks):
                if landmarks:
                    return [{"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility} for lm in landmarks]
                return []

            frame_landmarks = {
                "frame": frame_count + 1,
                "pose": extract_coordinates(results.pose_landmarks.landmark if results.pose_landmarks else None),
                "left_hand": extract_coordinates(
                    results.left_hand_landmarks.landmark if results.left_hand_landmarks else None),
                "right_hand": extract_coordinates(
                    results.right_hand_landmarks.landmark if results.right_hand_landmarks else None)
            }

            # Append this frame's landmarks to the video landmarks
            video_landmarks.append(frame_landmarks)

            # Display the frame with annotations
            cv2.putText(frame, f"Recording: {sign_name} (Frame {frame_count + 1}/{TOTAL_FRAMES})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('MediaPipe Holistic Model', frame)

            # Increment frame count
            frame_count += 1

            # Press `q` to interrupt the recording early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Recording interrupted.")
                break

        # Save the captured landmarks to a JSON file
        save_path = os.path.join(DATA_PATH, sign_name)
        os.makedirs(save_path, exist_ok=True)  # Create folder for the sign if it doesn't exist

        file_path = os.path.join(save_path, f"{sign_name}_{video_count}.json")
        save_landmarks_to_json(video_landmarks, file_path)
        print(f"Landmarks for sign '{sign_name}', video {video_count + 1}, saved successfully!")

    cap.release()
    cv2.destroyAllWindows()


def main():
    """
    Main loop for recording landmarks for different signs.
    """
    print("Welcome to the Sign Language Data Collection tool!")

    while True:
        print("\nEnter the name of the sign you want to record (or type 'exit' to quit):")
        sign_name = input().strip()

        if sign_name.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        # Create folder for the given sign
        os.makedirs(os.path.join(DATA_PATH, sign_name), exist_ok=True)

        print(f"You chose to record data for the sign: {sign_name}")

        # Check if there are already recorded videos for this sign
        existing_videos = len(os.listdir(os.path.join(DATA_PATH, sign_name)))
        remaining_videos = NUM_VIDEOS_PER_SIGN - existing_videos

        if remaining_videos <= 0:
            print(f"Enough videos ({NUM_VIDEOS_PER_SIGN}) are already recorded for the sign '{sign_name}'.")
            continue

        print(f"Remaining videos to record for '{sign_name}': {remaining_videos}")

        # Record the remaining videos for this sign
        for video_idx in range(existing_videos, NUM_VIDEOS_PER_SIGN):
            capture_landmarks_for_sign(sign_name, video_idx)

    print("Data collection finished! All data is saved.")


if __name__ == "__main__":
    main()
