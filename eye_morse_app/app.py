from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import time

app = Flask(__name__)

# Morse code dictionary
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D',
    '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
    '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
    '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9'
}

# Global variables
morse_sequence = ""
decoded_text = ""

# Mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_draw = mp.solutions.drawing_utils

# Blink detection thresholds
BLINK_THRESHOLD = 0.22
LETTER_PAUSE = 1.5  # end-of-letter pause

# Blink state
blink_start = None
eye_closed = False
last_blink_time = time.time()


def eye_aspect_ratio(landmarks, eye_indices, img_w, img_h):
    points = [(int(landmarks[i].x * img_w), int(landmarks[i].y * img_h)) for i in eye_indices]
    v1 = abs(points[1][1] - points[5][1])
    v2 = abs(points[2][1] - points[4][1])
    vertical = (v1 + v2) / 2.0
    horizontal = abs(points[0][0] - points[3][0])
    return vertical / horizontal if horizontal != 0 else 0


def gen_frames():
    global morse_sequence, decoded_text, blink_start, eye_closed, last_blink_time
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        current_time = time.time()

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Right eye indices
                right_eye_idx = [33, 160, 158, 133, 153, 144]
                ear = eye_aspect_ratio(face_landmarks.landmark, right_eye_idx, w, h)

                if ear < BLINK_THRESHOLD and not eye_closed:
                    eye_closed = True
                    blink_start = current_time

                elif ear >= BLINK_THRESHOLD and eye_closed:
                    blink_duration = current_time - blink_start
                    eye_closed = False
                    last_blink_time = current_time

                    # Original Tkinter timings
                    if blink_duration < 0.3:
                        morse_sequence += "."
                    elif blink_duration < 1.0:
                        morse_sequence += "-"
                    # Long blink → new word
                    elif blink_duration >= 1.5:
                        if morse_sequence:
                            decoded_text += MORSE_CODE_DICT.get(morse_sequence, "")
                            morse_sequence = ""
                        decoded_text += " "

                    blink_start = None

        # Auto decode letter if pause since last blink
        if morse_sequence and (current_time - last_blink_time) > LETTER_PAUSE:
            decoded_text += MORSE_CODE_DICT.get(morse_sequence, "")
            morse_sequence = ""

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_text')
def get_text():
    return jsonify({"morse": morse_sequence, "decoded": decoded_text})


@app.route('/clear', methods=['POST'])
def clear():
    global morse_sequence, decoded_text
    morse_sequence = ""
    decoded_text = ""
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
