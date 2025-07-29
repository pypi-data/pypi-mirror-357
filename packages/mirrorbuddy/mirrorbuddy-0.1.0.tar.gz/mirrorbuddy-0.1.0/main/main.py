import cv2
import mediapipe as mp
import pyttsx3

def clone():
    engine = pyttsx3.init()

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    pose = mp_pose.Pose()

    already_spoken = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            for connection in mp_pose.POSE_CONNECTIONS:
                start_idx = connection[0]
                end_idx = connection[1]

                start = result.pose_landmarks.landmark[start_idx]
                end = result.pose_landmarks.landmark[end_idx]

                x1 = w - int(start.x * w)
                y1 = int(start.y * h)
                x2 = w - int(end.x * w)
                y2 = int(end.y * h)

                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 10)

            for landmark in result.pose_landmarks.landmark:
                x = w - int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

            rh_real = result.pose_landmarks.landmark[16]  
            lh_clone = result.pose_landmarks.landmark[15] 

            real_hand_x = int(rh_real.x * w)
            real_hand_y = int(rh_real.y * h)
            clone_hand_x = w - int(lh_clone.x * w)
            clone_hand_y = int(lh_clone.y * h)

            dist = ((real_hand_x - clone_hand_x) ** 2 + (real_hand_y - clone_hand_y) ** 2) ** 0.5 
            if dist < 50:
                cv2.putText(frame, "🤝 Handshake!", (w//2 - 100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
                if not already_spoken:
                    engine.say("what's up bruh")
                    engine.runAndWait()
                    already_spoken = True
                else: 
                    already_spoken = False

        cv2.imshow("You and Your Clone", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()



