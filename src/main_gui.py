import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageEnhance, ImageTk
import pygame, os, sys, time, cv2
import threading


import ai_engine
import core_backend
import auth_manager





# -------------------------------
#  App Setup
# -------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Nova AI v1.0 (Beta) | Smart Assistant - Amir Hashmi")
root.geometry("950x650")  #780, 650
root.resizable(False, False)

current_user = None




# -------------------------------
#  Video Background Setup
# -------------------------------
video_path = "../assets/background_video.mp4"
cap = cv2.VideoCapture(video_path)

video_label = ctk.CTkLabel(root, text="")
video_label.place(x=0, y=0, relwidth=1, relheight=1)

def play_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (1190, 810))
        img = Image.fromarray(frame)

        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.4)
        img_tk = ImageTk.PhotoImage(img)
        video_label.configure(image=img_tk)
        video_label.image = img_tk

threading.Thread(target=play_video, daemon=True).start()

# -------------------------------
#  Utility Functions
# -------------------------------
def clear_window():
    for widget in root.winfo_children():
        if widget != video_label:
            widget.destroy()


def show_message(title, msg, type_="info"):
    if type_ == "info":
        messagebox.showinfo(title, msg)
    elif type_ == "error":
        messagebox.showerror(title, msg)

def on_close():
    play_sound("shutdown.wav")
    root.after(1500, root.destroy)

root.protocol("WM_DELETE_WINDOW", on_close)





# -------------------------------
#  Sound Effects
# -------------------------------
pygame.init()
pygame.mixer.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")
    return os.path.join(base_path, relative_path)

def play_sound(file):
    try:
        sound_path = resource_path(os.path.join("sounds", file))
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
    except :
        pass





# -------------------------------
#  Signup Page
# -------------------------------
def signup_page():
    clear_window()
    ctk.CTkLabel(root, text="Sign Up - Nova AI",
                 font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(pady=20)

    frame = ctk.CTkFrame(root, fg_color="#111111", corner_radius=15)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="Username").grid(row=0, column=0, pady=10, padx=10, sticky="w")
    username_entry = ctk.CTkEntry(frame, width=180)
    username_entry.grid(row=0, column=1, pady=10, padx=10)

    ctk.CTkLabel(frame, text="Password").grid(row=1, column=0, pady=10, padx=10, sticky="w")
    password_entry = ctk.CTkEntry(frame, show="*", width=180)
    password_entry.grid(row=1, column=1, pady=10, padx=10)

    def do_signup():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            show_message("Error", "Please fill in all fields", "error")
            return
        if auth_manager.create_user(username, password):
            show_message("Success", "Signup successful! Please login now.")
            login_page()
        else:
            show_message("Error", "Username already exists!", "error")

    ctk.CTkButton(frame, text="Sign Up", command=do_signup).grid(row=2, columnspan=2, pady=20)
    ctk.CTkButton(root, text="Back to Login", command=login_page).pack(pady=5)





# -------------------------------
#  Login Page
# -------------------------------
def login_page():
    global current_user
    clear_window()
    current_user = None

    ctk.CTkLabel(root, text="Login - Nova AI",
                 font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(pady=20)

    frame = ctk.CTkFrame(root, fg_color="#111111", corner_radius=15)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="Username").grid(row=0, column=0, pady=10, padx=10, sticky="w")
    username_entry = ctk.CTkEntry(frame, width=180)
    username_entry.grid(row=0, column=1, pady=10, padx=10)

    ctk.CTkLabel(frame, text="Password").grid(row=1, column=0, pady=10, padx=10, sticky="w")
    password_entry = ctk.CTkEntry(frame, show="*", width=180)
    password_entry.grid(row=1, column=1, pady=10, padx=10)

    def do_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if auth_manager.authenticate_user(username, password):
            global current_user
            current_user = username
            show_dashboard()
        else:
            show_message("Login Failed", "Invalid credentials!", "error")

    ctk.CTkButton(frame, text="Login", command=do_login).grid(row=2, columnspan=2, pady=20)
    ctk.CTkLabel(root, text="Don't have an account?", text_color="white").pack(pady=5)
    ctk.CTkButton(root, text="Signup Now", command=signup_page).pack(pady=5)





# -------------------------------
#  Sidebar Colors
# -------------------------------
dark_sidebar_color = "#1E1E2E"
light_sidebar_color = "#8ea5c0"


# -------------------------------
#  Dashboard
# -------------------------------
def show_dashboard():
    clear_window()
    user_info = auth_manager.get_user_info(current_user)
    theme = user_info.get("theme", "dark")
    ctk.set_appearance_mode(theme)

    sidebar_color = dark_sidebar_color if theme == "dark" else light_sidebar_color


    sidebar = ctk.CTkFrame(root, width=180, fg_color=sidebar_color)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(0)

    ctk.CTkLabel(sidebar, text=f"🔷 Control Panel", font=ctk.CTkFont(size=20, weight="bold"), text_color="#005f7f").pack(pady=20)
    ctk.CTkButton(sidebar, text="Dashboard", command=show_dashboard).pack(pady=8)
    ctk.CTkButton(sidebar, text="Profile", command=show_profile).pack(pady=8)
    ctk.CTkButton(sidebar, text="AI Assistant", command=lambda: threading.Thread(target=core_backend.Activation_N_E, daemon=True).start()).pack(pady=8)
    ctk.CTkButton(sidebar, text="History", command=show_history).pack(pady=8)
    ctk.CTkButton(sidebar, text="Logout", command=login_page).pack(side="bottom", pady=20)

    play_sound("startup.wav")


    rightbar = ctk.CTkFrame(root, width=180, fg_color=sidebar_color)
    rightbar.pack(side="right", fill="y")
    rightbar.pack_propagate(0)

    ctk.CTkLabel(rightbar, text="Settings", font=ctk.CTkFont(size=22, weight="bold"), text_color="#005f7f").pack(pady=20)
    ctk.CTkButton(rightbar, text="Toggle Theme", command=toggle_theme).pack(pady=10)





    # -------------------------------
    #  Dashboard Main Content
    # -------------------------------
    center = ctk.CTkFrame(root, fg_color="#0B2027")
    center.pack(expand=True, fill="both")

    # Video label for center background
    video_label_center = ctk.CTkLabel(center, text="", width=800, height=650)
    video_label_center.place(x=0, y=0)

    # Video path for center background
    center_video_path = "../assets/background_video.mp4"
    center_cap = cv2.VideoCapture(center_video_path)

    def play_center_video():
        def update_frame():
            # Agar widget destroy ho gaya to return
            if not video_label_center.winfo_exists():
                return

            if not center_cap.isOpened():
                return

            ret, frame = center_cap.read()
            if not ret:
                center_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                root.after(20, update_frame)
                return

            # Convert to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize
            frame = cv2.resize(frame, (800, 650), interpolation=cv2.INTER_AREA)

            # Brightness adjust
            img = Image.fromarray(frame)
            img = ImageEnhance.Brightness(img).enhance(0.4)

            # CTkImage (warning free)
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 650))

            # Update safely
            video_label_center.configure(image=img_ctk)
            video_label_center.image = img_ctk

            # Schedule next frame
            root.after(20, update_frame)

        update_frame()

    threading.Thread(target=play_center_video, daemon=True).start()







    # -------------------------------
    #  Nova Profile Logo (Top Center)
    # -------------------------------
    try:
        profile_img = Image.open("../assets/logo.png").resize((120, 110))
        profile_ctk = ctk.CTkImage(light_image=profile_img, dark_image=profile_img, size=(120, 110))
        profile_label = ctk.CTkLabel(center, image=profile_ctk, text="")
        profile_label.pack(pady=(28, 5))
    except:
        pass


    ctk.CTkLabel(center,
                 text=f"Welcome {current_user}! 🤖 Ready to assist you...",
                 font=ctk.CTkFont(size=25, weight="bold"),
                 text_color="white").pack(pady=30)




    input_frame = ctk.CTkFrame(center , fg_color = "transparent")
    input_frame.pack(pady=50)

    command_entry = ctk.CTkEntry(input_frame, width=350, fg_color="#101010", corner_radius=8)
    command_entry.pack(side="left", padx=5)

    response_box = ctk.CTkTextbox(center, height=290, width=550, fg_color="#101010", corner_radius=10)
    response_box.pack(pady=10)
    response_box.configure(state="disabled")



    def type_response(response_text, box):
        box.configure(state="normal")
        box.insert("end", "🤖 Nova: ")
        play_sound("type.wav")
        box.update()
        for char in response_text:
            box.insert("end", char)
            box.update()
            time.sleep(0)
        box.insert("end", "\n\n")
        box.see("end")
        box.configure(state="disabled")

    def handle_command():
        user_input = command_entry.get().strip()
        if not user_input:
            return


        response_box.configure(state="normal")
        response_box.insert("end", f"\n🧠 You: {user_input}\n")
        response_box.configure(state="disabled")
        command_entry.delete(0, "end")
        response_box.update()




        try:
            response = ai_engine.Ai_answer(user_input)
            type_response(response.strip(), response_box)
            auth_manager.save_user_history(
                current_user, f"\nYou: {user_input}\nNova: {response}"
            )
        except Exception as e:
            response_box.configure(state="normal")
            response_box.insert("end", f"⚠️ Error: {str(e)}\n")
            response_box.configure(state="disabled")


    ctk.CTkButton(input_frame, text="Ask Nova", command=handle_command).pack(side="left", padx=5)






# -------------------------------
#  Profile Page
# -------------------------------
def show_profile():
    user_info = auth_manager.get_user_info(current_user)


    popup = ctk.CTkToplevel(root)
    popup.title("Profile Info")
    popup.geometry("350x400")
    popup.resizable(False, False)
    popup.grab_set()


    frame = ctk.CTkFrame(popup, fg_color="#0B2027", corner_radius=12)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # -------------------------------
    # Profile Picture (Top Center)
    # -------------------------------
    try:
        from PIL import Image
        profile_img = Image.open("../assets/ai_avatar.png").resize((120, 120))
        profile_ctk = ctk.CTkImage(light_image=profile_img, dark_image=profile_img, size=(120, 120))
        ctk.CTkLabel(frame, image=profile_ctk, text="").pack(pady=(15, 5))
    except:
       pass

    # -------------------------------
    # User Info Styled Labels
    # -------------------------------
    ctk.CTkLabel(frame, text=f"Username: {current_user}",
                 font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=5)

    ctk.CTkLabel(frame, text=f"Theme: {user_info.get('theme', 'dark')}",
                 font=ctk.CTkFont(size=14), text_color="lightgray").pack(pady=5)

    ctk.CTkLabel(frame, text=f"History Entries: {len(user_info['history'])}",
                 font=ctk.CTkFont(size=14), text_color="lightgray").pack(pady=5)


    ctk.CTkButton(frame, text="Close", command=popup.destroy, width=100).pack(pady=20)




# -------------------------------
#  History Page
# -------------------------------
def show_history():
    clear_window()
    ctk.CTkLabel(root, text=f"{current_user}'s Search History", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)
    history_box = ctk.CTkTextbox(root, width=800, height=400)
    history_box.pack(pady=10)
    history = auth_manager.get_user_info(current_user).get("history", [])
    if history:
        for entry in history:
            history_box.insert("end", entry + "\n\n\n")
    else:
        history_box.insert("end", "No history found.")
    history_box.configure(state="disabled")
    ctk.CTkButton(root, text="Back to Dashboard", command=show_dashboard).pack(pady=10)



# -------------------------------
#  Theme Toggle
# -------------------------------
def toggle_theme():
    user_info = auth_manager.get_user_info(current_user)
    new_theme = "light" if user_info.get("theme", "dark") == "dark" else "dark"
    auth_manager.change_theme(current_user, new_theme)
    show_dashboard()


# -------------------------------
#  Start App
# -------------------------------
login_page()
root.mainloop()
