import cv2
import face_recognition
import numpy as np
import csv
from datetime import datetime


def load_known_faces():
    ankit_image = face_recognition.load_image_file("C://Users//DELL//Downloads//face//face//ankit.jpg")
    ankit_encoding = face_recognition.face_encodings(ankit_image)[0]
    raushan_image = face_recognition.load_image_file("C://Users//DELL//Downloads//face//face//raushan.jpg")
    raushan_encoding = face_recognition.face_encodings(raushan_image)[0]
    satyam_image = face_recognition.load_image_file("C://Users//DELL//Downloads//face//face//satyam.jpg")
    satyam_encoding = face_recognition.face_encodings(satyam_image)[0]
    pragya_image = face_recognition.load_image_file("C://Users//DELL//Downloads//face//face//pragya.jpg")
    pragya_encoding = face_recognition.face_encodings(pragya_image)[0]

    known_face_encodings = [ankit_encoding, raushan_encoding,satyam_encoding,pragya_encoding]
    known_face_names = ["Ankit", "Raushan","Satyam","Pragya"]
    return known_face_encodings, known_face_names


def initialize_attendance_file(course_name, teacher_name):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    filename = f"attendance_{course_name}_{teacher_name}_{current_date}.csv"
    f = open(filename, "w+", newline="")
    lnwritter = csv.writer(f)
    lnwritter.writerow(["Name", "Time", "Course", "Teacher"])
    return f, lnwritter, filename


def recognize_faces(frame, known_face_encodings, known_face_names, recorded_students, lnwritter, course_name,
                    teacher_name):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distance)

        name = "Unknown"
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        if name not in recorded_students and name != "Unknown":
            recorded_students.add(name)
            current_time = datetime.now().strftime("%H:%M:%S")
            lnwritter.writerow([name, current_time, course_name, teacher_name])

        return name
    return "Unknown"
