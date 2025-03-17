import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from cryptography.fernet import Fernet

# Color Palette
COLOR_BACKGROUND = "#FFF2F2"  # Light pink background
COLOR_BUTTON = "#A9B5DF"      # Soft blue for buttons
COLOR_TREEVIEW = "#7886C7"    # Medium blue for Treeview
COLOR_TEXT = "#2D336B"        # Dark blue for text

# Generate or load the encryption key
def load_key():
    key_file = "secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key

key = load_key()
cipher = Fernet(key)

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# Store credentials
def save_password():
    # Create a custom dialog box for entering all details
    dialog = tk.Toplevel(root)
    dialog.title("Save Password")  # Title of the dialog box
    dialog.geometry("300x200")
    dialog.configure(bg=COLOR_BACKGROUND)

    # Labels and Entry fields
    tk.Label(dialog, text="Service Name:", bg=COLOR_BACKGROUND, fg=COLOR_TEXT).grid(row=0, column=0, padx=10, pady=5)
    service_entry = tk.Entry(dialog)
    service_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(dialog, text="Username:", bg=COLOR_BACKGROUND, fg=COLOR_TEXT).grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(dialog)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(dialog, text="Password:", bg=COLOR_BACKGROUND, fg=COLOR_TEXT).grid(row=2, column=0, padx=10, pady=5)
    password_entry = tk.Entry(dialog, show="*")  # Show asterisks for password input
    password_entry.grid(row=2, column=1, padx=10, pady=5)

    # Save button
    def save():
        service = service_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if not service or not username or not password:
            messagebox.showerror("Error", "All fields are required!", parent=dialog)
            return

        encrypted_password = encrypt_password(password)
        data = {}
        if os.path.exists("passwords.json"):
            with open("passwords.json", "r") as file:
                data = json.load(file)
        data[service] = {"username": username, "password": encrypted_password}
        with open("passwords.json", "w") as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", "Password saved successfully!", parent=dialog)
        refresh_list()
        dialog.destroy()

    tk.Button(dialog, text="Save", command=save, bg=COLOR_BUTTON, fg=COLOR_TEXT).grid(row=3, column=1, pady=10)

# Retrieve credentials
def get_password():
    master_password = simpledialog.askstring(
        "Master Password Required",  # Title of the dialog box
        "Enter master password:",   # Prompt message
        show='*',                  # Show asterisks for password input
        parent=root                # Ensure the dialog is centered relative to the main window
    )
    
    # Replace "master123" with a more secure way to store/check the master password
    if master_password != "master123":
        messagebox.showerror("Error", "Incorrect master password!", parent=root)
        return

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No service selected!", parent=root)
        return

    service = tree.item(selected_item)['values'][0]
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            data = json.load(file)
        if service in data:
            username = data[service]["username"]
            decrypted_password = decrypt_password(data[service]["password"])
            messagebox.showinfo("Retrieved Password", f"Service: {service}\nUsername: {username}\nPassword: {decrypted_password}", parent=root)
            return
    messagebox.showerror("Error", "No password found for this service.", parent=root)

# Remove credentials
def remove_password():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No service selected!", parent=root)
        return

    service = tree.item(selected_item)['values'][0]
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            data = json.load(file)
        if service in data:
            del data[service]
            with open("passwords.json", "w") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Success", "Password removed successfully!", parent=root)
            refresh_list()

# Refresh the list of services
def refresh_list():
    for item in tree.get_children():
        tree.delete(item)
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            data = json.load(file)
        for service in data:
            # Display password as asterisks
            tree.insert("", "end", values=(service, data[service]["username"], "********"))

# GUI Setup
root = tk.Tk()
root.title("Password Manager")
root.geometry("600x400")
root.configure(bg=COLOR_BACKGROUND)

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=COLOR_BACKGROUND, fieldbackground=COLOR_BACKGROUND, foreground=COLOR_TEXT, font=("Arial", 10))
style.configure("Treeview.Heading", background=COLOR_TREEVIEW, foreground=COLOR_TEXT, font=("Arial", 12, "bold"))
style.map("Treeview", background=[("selected", COLOR_TREEVIEW)])

# Treeview for listing services
tree = ttk.Treeview(root, columns=("Service", "Username", "Password"), show="headings")
tree.heading("Service", text="Service")
tree.heading("Username", text="Username")
tree.heading("Password", text="Password")
tree.column("Service", width=150)
tree.column("Username", width=150)
tree.column("Password", width=150)
tree.pack(pady=20, padx=20, fill="both", expand=True)

# Buttons
button_frame = tk.Frame(root, bg=COLOR_BACKGROUND)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Save Password", command=save_password, bg=COLOR_BUTTON, fg=COLOR_TEXT, width=20).pack(side="left", padx=5)
tk.Button(button_frame, text="Retrieve Password", command=get_password, bg=COLOR_BUTTON, fg=COLOR_TEXT, width=20).pack(side="left", padx=5)
tk.Button(button_frame, text="Remove Password", command=remove_password, bg=COLOR_BUTTON, fg=COLOR_TEXT, width=20).pack(side="left", padx=5)
tk.Button(button_frame, text="Exit", command=root.quit, bg=COLOR_BUTTON, fg=COLOR_TEXT, width=20).pack(side="left", padx=5)

# Initial list refresh
refresh_list()

root.mainloop()