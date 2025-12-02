import tkinter as tk
from tkinter import Label, Button, Entry, messagebox
from PIL import Image, ImageTk
import cv2
import backend1  # make sure your backend file is named backend.py or change this import

# Globals for video / DB / state
video_capture = None
known_face_encodings = []
known_face_names = []
recorded_students = set()
course_name = ""
teacher_name = ""
conn = None
cursor = None
db_filename = None
current_date = None

def start_attendance():
    global video_capture, course_name, teacher_name, recorded_students, conn, cursor, db_filename, current_date

    course_name = course_entry.get().strip()
    teacher_name = teacher_entry.get().strip()
    if not course_name or not teacher_name:
        messagebox.showerror("Error", "Please enter course name and teacher name")
        return

    # Initialize DB (returns conn, cursor, filename, date)
    conn, cursor, db_filename, current_date = backend1.initialize_database(course_name, teacher_name)

    # load known faces if not already loaded
    global known_face_encodings, known_face_names
    if not known_face_encodings:
        known_face_encodings, known_face_names = backend1.load_known_faces()

    # init video if not already
    if video_capture is None:
        init_video_capture()

    recorded_students.clear()
    messagebox.showinfo("Attendance System", f"Attendance started for {course_name} by {teacher_name}\nDB: {db_filename}")

    # Start updating frames
    update_frame()

def init_video_capture():
    global video_capture
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        messagebox.showerror("Error", "Unable to open webcam")
        raise SystemExit

def update_frame():
    global video_capture, known_face_encodings, known_face_names, recorded_students, conn, cursor, course_name, teacher_name, current_date

    if video_capture is None or not video_capture.isOpened():
        return

    ret, frame = video_capture.read()
    if not ret:
        return

    # Call backend recognize_faces (which inserts into DB for newly seen)
    # The backend's recognize_faces returns (detected_names, face_locations)
    detected_names, face_locations = backend1.recognize_faces(
        frame,
        known_face_encodings,
        known_face_names,
        recorded_students,
        cursor,
        conn,
        course_name,
        teacher_name,
        current_date
    )

    # Draw rectangles and labels on frame (note: face_locations are for scaled down frame)
    # In the backend we used 1/4 scaling; so multiply by 4 to draw on original frame
    for (top, right, bottom, left), name in zip(face_locations, detected_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    # Show last detected name at top-left (or "No one")
    last_name = detected_names[0] if detected_names else "No one"
    cv2.putText(frame, f"{last_name} Present", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Convert for Tkinter display
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # schedule next frame
    video_label.after(10, update_frame)

def close_application():
    global video_capture, conn

    if video_capture is not None and video_capture.isOpened():
        video_capture.release()

    cv2.destroyAllWindows()

    # close DB connection
    if conn:
        conn.close()

    root.destroy()
    messagebox.showinfo("Attendance System", f"Attendance session closed.\nDB saved to: {db_filename or 'N/A'}")

# ---------- GUI layout ----------
root = tk.Tk()
root.title("Attendance System")
root.geometry("700x580")
root.configure(bg="#f0f0f0")

title = Label(root, text="Face Recognition Attendance System", font=("Arial", 18, "bold"), bg="#f0f0f0")
title.pack(pady=12)

frm = tk.Frame(root, bg="#f0f0f0")
frm.pack(pady=6)

course_label = Label(frm, text="Course Name:", font=("Arial", 12), bg="#f0f0f0")
course_label.grid(row=0, column=0, padx=6, pady=6, sticky="e")
course_entry = Entry(frm, font=("Arial", 12), width=30, justify="center")
course_entry.grid(row=0, column=1, padx=6, pady=6)

teacher_label = Label(frm, text="Teacher Name:", font=("Arial", 12), bg="#f0f0f0")
teacher_label.grid(row=1, column=0, padx=6, pady=6, sticky="e")
teacher_entry = Entry(frm, font=("Arial", 12), width=30, justify="center")
teacher_entry.grid(row=1, column=1, padx=6, pady=6)

btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=8)

start_button = Button(btn_frame, text="Start Attendance", command=start_attendance, font=("Arial", 12, "bold"), bg="green", fg="white", width=18)
start_button.grid(row=0, column=0, padx=10)

stop_button = Button(btn_frame, text="Stop Attendance", command=close_application, font=("Arial", 12, "bold"), bg="red", fg="white", width=18)
stop_button.grid(row=0, column=1, padx=10)

video_label = Label(root, bg="#000000", width=640, height=420)
video_label.pack(pady=10)

# preload known faces (optional) to avoid lag when starting
try:
    known_face_encodings, known_face_names = backend1.load_known_faces()
except Exception as e:
    # if images are missing or encodings fail, show message but allow GUI to run
    print("Warning: couldn't preload known faces:", e)
    known_face_encodings, known_face_names = [], []

root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()

# Print final DB filename (optional)
if db_filename:
    print(f"Attendance saved in {db_filename}")
