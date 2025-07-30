import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from decouple import config

class BusinessCard:
    def __init__(self, first_name="", last_name="", email="", phone_number="", comment="",
                 photo_path=None, front_card_path=None, back_card_path=None, id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.comment = comment
        self.photo_path = photo_path
        self.front_card_path = front_card_path
        self.back_card_path = back_card_path

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BusinessCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Card Manager")
        self.details_window = None
        self.center_window(800, 900) 

        self.db_file = "business_cards.db"
        self.media_dir = "Media/buscard_photo"
        os.makedirs(self.media_dir, exist_ok=True)
        self._create_table()
        self.business_cards = []
        self.selected_item_id = None  # Store the ID of the selected card in the Treeview
        self.details_window = None  # To track if the details window is open
        self.compose_email_window = None # To track the compose email window

        self._create_widgets()  # Call _create_widgets first
        self._load_data()    # Then call _load_data

    def center_window(self, width, height):
        """Centers the Tkinter window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone_number TEXT,
                comment TEXT,
                photo_path TEXT,
                front_card_path TEXT,
                back_card_path TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _load_data(self):
        self.business_cards = []
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email, phone_number FROM business_cards")
        rows = cursor.fetchall()
        for row in rows:
            self.business_cards.append(BusinessCard(id=row[0], first_name=row[1], last_name=row[2], email=row[3], phone_number=row[4]))
        conn.close()
        self._populate_treeview()

    def _fetch_card_details(self, card_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM business_cards WHERE id=?", (card_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return BusinessCard(id=row[0], first_name=row[1], last_name=row[2], email=row[3],
                                 phone_number=row[4], comment=row[5], photo_path=row[6],
                                 front_card_path=row[7], back_card_path=row[8])
        return None

    def _save_resized_image(self, image_path, save_path, size):
        try:
            img = Image.open(image_path)
            img = img.resize(size)
            img.save(save_path)
            return save_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save/resize image: {e}")
            return None

    def _select_photo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.temp_photo_path = file_path
            self.photo_path_label.configure(text=file_path)

    def _select_front_card(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.temp_front_card_path = file_path
            self.front_card_path_label.configure(text=file_path)

    def _select_back_card(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.temp_back_card_path = file_path
            self.back_card_path_label.configure(text=file_path)

    def _add_card(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        phone_number = self.phone_entry.get()
        comment = self.comment_entry.get("1.0", ctk.END).strip()

        photo_path = None
        front_card_path = None
        back_card_path = None

        if first_name and last_name:
            base_name = f"{first_name.lower()}_{last_name.lower()}"

            if hasattr(self, 'temp_photo_path') and self.temp_photo_path:
                photo_filename = f"{base_name}.png"
                photo_save_path = os.path.join(self.media_dir, photo_filename)
                photo_path = self._save_resized_image(self.temp_photo_path, photo_save_path, (300, 300))
                del self.temp_photo_path

            if hasattr(self, 'temp_front_card_path') and self.temp_front_card_path:
                front_filename = f"{base_name}_f.png"
                front_save_path = os.path.join(self.media_dir, front_filename)
                front_card_path = self._save_resized_image(self.temp_front_card_path, front_save_path, (300, 600))
                del self.temp_front_card_path

            if hasattr(self, 'temp_back_card_path') and self.temp_back_card_path:
                back_filename = f"{base_name}_b.png"
                back_save_path = os.path.join(self.media_dir, back_filename)
                back_card_path = self._save_resized_image(self.temp_back_card_path, back_save_path, (300, 600))
                del self.temp_back_card_path

            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO business_cards (first_name, last_name, email, phone_number, comment, photo_path, front_card_path, back_card_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone_number, comment, photo_path, front_card_path, back_card_path))
            conn.commit()
            conn.close()
            self._load_data()
            self._clear_fields()
        else:
            messagebox.showerror("Error", "First and Last Name are required.")

    def _update_card(self):
        if self.selected_item_id is not None:
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            email = self.email_entry.get()
            phone_number = self.phone_entry.get()
            comment = self.comment_entry.get("1.0", ctk.END).strip()
            original_card = self._fetch_card_details(self.selected_item_id)

            photo_path = original_card.photo_path if original_card else None
            front_card_path = original_card.front_card_path if original_card else None
            back_card_path = original_card.back_card_path if original_card else None

            if first_name and last_name:
                base_name = f"{first_name.lower()}_{last_name.lower()}"

                if hasattr(self, 'temp_photo_path') and self.temp_photo_path:
                    photo_filename = f"{base_name}.png"
                    photo_save_path = os.path.join(self.media_dir, photo_filename)
                    photo_path = self._save_resized_image(self.temp_photo_path, photo_save_path, (300, 300))
                    del self.temp_photo_path
                elif self.photo_path_label.cget("text") and not hasattr(self, 'temp_photo_path'):
                    photo_path = self.photo_path_label.cget("text")

                if hasattr(self, 'temp_front_card_path') and self.temp_front_card_path:
                    front_filename = f"{base_name}_f.png"
                    front_save_path = os.path.join(self.media_dir, front_filename)
                    front_card_path = self._save_resized_image(self.temp_front_card_path, front_save_path, (300, 600))
                    del self.temp_front_card_path
                elif self.front_card_path_label.cget("text") and not hasattr(self, 'temp_front_card_path'):
                    front_card_path = self.front_card_path_label.cget("text")

                if hasattr(self, 'temp_back_card_path') and self.temp_back_card_path:
                    back_filename = f"{base_name}_b.png"
                    back_save_path = os.path.join(self.media_dir, back_filename)
                    back_card_path = self._save_resized_image(self.temp_back_card_path, back_save_path, (300, 600))
                    del self.temp_back_card_path
                elif self.back_card_path_label.cget("text") and not hasattr(self, 'temp_back_card_path'):
                    back_card_path = self.back_card_path_label.cget("text")

                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE business_cards SET first_name=?, last_name=?, email=?, phone_number=?, comment=?,
                    photo_path=?, front_card_path=?, back_card_path=? WHERE id=?
                """, (first_name, last_name, email, phone_number, comment, photo_path, front_card_path, back_card_path, self.selected_item_id))
                conn.commit()
                conn.close()
                self._load_data()
                self._clear_fields()
                self.update_button.configure(state="disabled")
                self.delete_button.configure(state="disabled")
                self.selected_item_id = None
            else:
                messagebox.showerror("Error", "First and Last Name are required.")
        else:
            messagebox.showinfo("Info", "Please select a card to update.")

    def _delete_card(self):
        if self.selected_item_id is not None:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this card?"):
                card_to_delete = self._fetch_card_details(self.selected_item_id)
                if messagebox.askyesno("Confirm", "Do you want to delete the associated image files as well?"):
                    if card_to_delete.photo_path and os.path.exists(card_to_delete.photo_path):
                        os.remove(card_to_delete.photo_path)
                    if card_to_delete.front_card_path and os.path.exists(card_to_delete.front_card_path):
                        os.remove(card_to_delete.front_card_path)
                    if card_to_delete.back_card_path and os.path.exists(card_to_delete.back_card_path):
                        os.remove(card_to_delete.back_card_path)

                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM business_cards WHERE id=?", (self.selected_item_id,))
                conn.commit()
                conn.close()
                self._load_data()
                self._clear_fields()
                self.update_button.configure(state="disabled")
                self.delete_button.configure(state="disabled")
                self.selected_item_id = None
        else:
            messagebox.showinfo("Info", "Please select a card to delete.")

    def _clear_fields(self):
        self.first_name_entry.delete(0, ctk.END)
        self.last_name_entry.delete(0, ctk.END)
        self.email_entry.delete(0, ctk.END)
        self.phone_entry.delete(0, ctk.END)
        self.comment_entry.delete("1.0", ctk.END)
        self.photo_path_label.configure(text="")
        self.front_card_path_label.configure(text="")
        self.back_card_path_label.configure(text="")
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        if hasattr(self, 'temp_photo_path'):
            del self.temp_photo_path
        if hasattr(self, 'temp_front_card_path'):
            del self.temp_front_card_path
        if hasattr(self, 'temp_back_card_path'):
            del self.temp_back_card_path
        self.selected_item_id = None

    def _populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email, phone_number FROM business_cards")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", ctk.END, values=(f"{row[1]} {row[2]}", row[3], row[4]), tags=row[0])
        conn.close()

    def _search_cards(self):
        search_term = self.search_entry.get().lower()
        # Clear the current treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone_number
            FROM business_cards
            WHERE LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(phone_number) LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Search Results", "No matching business cards found.")
        else:
            for row in rows:
                self.tree.insert("", ctk.END, values=(f"{row[1]} {row[2]}", row[3], row[4]), tags=row[0])

        conn.close()
        self.search_entry.delete(0, ctk.END) # Clear the search entry


    def _open_compose_email(self, recipient_emails):
        if self.compose_email_window is None or not self.compose_email_window.winfo_exists():
            self.compose_email_window = ctk.CTkToplevel(self.root)
            self.compose_email_window.title("Compose Email")

            recipients_label = ctk.CTkLabel(self.compose_email_window, text="To:")
            recipients_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            recipients_entry = ctk.CTkEntry(self.compose_email_window)
            recipients_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            recipients_entry.insert(0, ", ".join(recipient_emails))

            subject_label = ctk.CTkLabel(self.compose_email_window, text="Subject:")
            subject_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            subject_entry = ctk.CTkEntry(self.compose_email_window)
            subject_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

            body_label = ctk.CTkLabel(self.compose_email_window, text="Body:")
            body_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
            body_text = ctk.CTkTextbox(self.compose_email_window, height=150)
            body_text.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

            # Removed sender_email_label and sender_email_entry

            # Removed sender_password_label and sender_password_entry

            send_button = ctk.CTkButton(self.compose_email_window, text="Send",
                                         command=lambda: self._send_actual_email(
                                             recipients_entry.get(),
                                             subject_entry.get(),
                                             body_text.get("1.0", ctk.END)
                                             # Removed the now unnecessary arguments
                                         ))
            send_button.grid(row=3, column=1, padx=10, pady=10, sticky="e") # Adjusted grid row

            self.compose_email_window.grid_columnconfigure(1, weight=1)
        else:
            self.compose_email_window.focus()

    def _send_email(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select one or more business cards to send an email to.")
            return

        recipient_emails = []
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        for item_id in selected_items:
            tags = self.tree.item(item_id, 'tags')
            if tags:
                card_id = tags[0]
                cursor.execute("SELECT email FROM business_cards WHERE id=?", (card_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    recipient_emails.append(result[0])
        conn.close()

        if recipient_emails:
            self._open_compose_email(recipient_emails)
        else:
            messagebox.showinfo("Info", "No email addresses found for the selected business cards.")


    def _send_actual_email(self, recipients, subject, body):
        smtp_server = "smtp.gmail.com"
        port = 587  # For TLS

        sender_email = config('EMAIL_USER')
        sender_password = config('EMAIL_PASSWORD')

        server = None  # Initialize server outside the try block
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()  # Upgrade connection to secure TLS
            server.login(sender_email, sender_password)

            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipients

            server.sendmail(sender_email, recipients.split(", "), msg.as_string())
            messagebox.showinfo("Email Sent", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Email Failed", f"Failed to send email. Error: {e}")
        finally:
            if server:  # Check if the server object was successfully created
                try:
                    server.quit()
                except smtplib.SMTPServerDisconnected:
                    # Handle the case where the server disconnected unexpectedly
                    pass
                except Exception as e:
                    print(f"Error during server.quit(): {e}")
            if self.compose_email_window and self.compose_email_window.winfo_exists():
                self.compose_email_window.destroy()
                self.compose_email_window = None

    def _display_details(self, event):
        selected_item = self.tree.selection()
        print(f"self.details_window: {self.details_window}")
        if not selected_item:
            return

        if self.details_window is None or not self.details_window.winfo_exists():
            self.selected_item_id = self.tree.item(selected_item[0], 'tags')[0]
            card = self._fetch_card_details(self.selected_item_id)

            if card:
                self.first_name_entry.delete(0, ctk.END)
                self.first_name_entry.insert(0, card.first_name)
                self.last_name_entry.delete(0, ctk.END)
                self.last_name_entry.insert(0, card.last_name)
                self.email_entry.delete(0, ctk.END)
                self.email_entry.insert(0, card.email)
                self.phone_entry.delete(0, ctk.END)
                self.phone_entry.insert(0, card.phone_number)
                self.comment_entry.delete("1.0", ctk.END)
                self.comment_entry.insert("1.0", card.comment)
                self.photo_path_label.configure(text=card.photo_path if card.photo_path else "")
                self.front_card_path_label.configure(text=card.front_card_path if card.front_card_path else "")
                self.back_card_path_label.configure(text=card.back_card_path if card.back_card_path else "")

                self.update_button.configure(state="normal")
                self.delete_button.configure(state="normal")

                self.details_window = ctk.CTkToplevel(self.root)
                self.details_window.title(f"{card.first_name} {card.last_name} Details")
                self.details_window.protocol("WM_DELETE_WINDOW", self._close_details_window) # Handle window closing

                row = 0
                ctk.CTkLabel(self.details_window, text=f"First Name:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.details_window, text=card.first_name).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                row += 1
                ctk.CTkLabel(self.details_window, text=f"Last Name:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.details_window, text=card.last_name).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                row += 1
                ctk.CTkLabel(self.details_window, text=f"Email:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.details_window, text=card.email).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                row += 1
                ctk.CTkLabel(self.details_window, text=f"Phone:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.details_window, text=card.phone_number).grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                row += 1
                ctk.CTkLabel(self.details_window, text=f"Comment:").grid(row=row, column=0, padx=10, pady=5, sticky="nw")
                comment_label = ctk.CTkLabel(self.details_window, text=card.comment, justify="left")
                comment_label.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                row += 1

                if card.photo_path and os.path.exists(card.photo_path):
                    try:
                        img = Image.open(card.photo_path)
                        ctk_image = ctk.CTkImage(img, size=(150, 150))
                        photo_label = ctk.CTkLabel(self.details_window, image=ctk_image, text="")
                        photo_label.grid(row=0, column=2, padx=10, pady=5, rowspan=row, sticky="ns")
                    except Exception as e:
                        ctk.CTkLabel(self.details_window, text=f"Error loading photo: {e}").grid(row=0, column=2, padx=10, pady=5, rowspan=row, sticky="ns")

                card_row = row
                if card.front_card_path and os.path.exists(card.front_card_path):
                    try:
                        img = Image.open(card.front_card_path)
                        ctk_image = ctk.CTkImage(img, size=(300, 200))
                        front_label = ctk.CTkLabel(self.details_window, image=ctk_image, text="Front Card")
                        front_label.grid(row=card_row, column=0, columnspan=3, padx=10, pady=5)
                        card_row += 1
                    except Exception as e:
                        ctk.CTkLabel(self.details_window, text=f"Error loading front card: {e}").grid(row=card_row, column=0, columnspan=3, padx=10, pady=5)
                        card_row += 1

                if card.back_card_path and os.path.exists(card.back_card_path):
                    try:
                        img = Image.open(card.back_card_path)
                        ctk_image = ctk.CTkImage(img, size=(300, 200))
                        back_label = ctk.CTkLabel(self.details_window, image=ctk_image, text="Back Card")
                        back_label.grid(row=card_row, column=0, columnspan=3, padx=10, pady=5)
                    except Exception as e:
                        ctk.CTkLabel(self.details_window, text=f"Error loading back card: {e}").grid(row=card_row, column=0, columnspan=3, padx=10, pady=5)

                self.details_window.grid_columnconfigure(1, weight=1) # Make the second column resizable
            elif self.details_window.winfo_exists():
                self.details_window.focus() # Bring the existing window to the front

    def _close_details_window(self):
        if self.details_window:
            self.details_window.destroy()
            self.details_window = None

    def _create_widgets(self):
        # --- Input Frame ---
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(padx=20, pady=20, fill="x")

        try:
            bg_pil_image = Image.open("images/mia2025.png")  # Replace with your actual image path
            bg_ctk_image = ctk.CTkImage(light_image=bg_pil_image, dark_image=bg_pil_image, size=(300, 300)) # Adjust size as needed
            self.bg_label = ctk.CTkLabel(self.input_frame, text="", image=bg_ctk_image)
            self.bg_label.grid(row=0, column=3, columnspan=3, rowspan=6, padx=20, pady=5, sticky="nsew")
        except FileNotFoundError:
            print("Error: Background image file not found.")
        except Exception as e:
            print(f"Error loading background image: {e}")

        self.first_name_label = ctk.CTkLabel(self.input_frame, text="First Name:")
        self.first_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.first_name_entry = ctk.CTkEntry(self.input_frame)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.last_name_label = ctk.CTkLabel(self.input_frame, text="Last Name:")
        self.last_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.last_name_entry = ctk.CTkEntry(self.input_frame)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.email_label = ctk.CTkLabel(self.input_frame, text="Email:")
        self.email_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ctk.CTkEntry(self.input_frame)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.phone_label = ctk.CTkLabel(self.input_frame, text="Phone Number:")
        self.phone_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = ctk.CTkEntry(self.input_frame)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.comment_label = ctk.CTkLabel(self.input_frame, text="Comment:")
        self.comment_label.grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        self.comment_entry = ctk.CTkTextbox(self.input_frame, height=50)
        self.comment_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.photo_button = ctk.CTkButton(self.input_frame, text="Select Photo", command=self._select_photo)
        self.photo_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.photo_path_label = ctk.CTkLabel(self.input_frame, text="")
        self.photo_path_label.grid(row=6, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.front_card_button = ctk.CTkButton(self.input_frame, text="Select Front Card", command=self._select_front_card)
        self.front_card_button.grid(row=7, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.front_card_path_label = ctk.CTkLabel(self.input_frame, text="")
        self.front_card_path_label.grid(row=8, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.back_card_button = ctk.CTkButton(self.input_frame, text="Select Back Card", command=self._select_back_card)
        self.back_card_button.grid(row=9, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.back_card_path_label = ctk.CTkLabel(self.input_frame, text="")
        self.back_card_path_label.grid(row=10, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.search_entry = ctk.CTkEntry(self.input_frame)
        self.search_entry.grid(row=11, column=0, padx=5, pady=5, sticky="ew")
        self.search_button = ctk.CTkButton(self.input_frame, text="Search", command=self._search_cards)
        self.search_button.grid(row=11, column=1, padx=5, pady=5, sticky="ew")


        self.send_email_button = ctk.CTkButton(self.input_frame, text="Send Email", command=self._send_email) # New button
        self.send_email_button.grid(row=11, column=3, padx=5, pady=5, sticky="ew")

        # --- Treeview Frame ---
        self.treeview_frame = ctk.CTkFrame(self.root)
        self.treeview_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree_scrollbar = ctk.CTkScrollbar(self.treeview_frame)
        self.tree_scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.treeview_frame, columns=("Name", "Email", "Phone"), show="headings", yscrollcommand=self.tree_scrollbar.set, selectmode="extended") # Enable multiple selection
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._display_details) # Bind double-click

        self.tree_scrollbar.configure(command=self.tree.yview)



        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(padx=20, pady=10, fill="x")

        self.add_button = ctk.CTkButton(self.button_frame, text="Add", command=self._add_card)
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        self.update_button = ctk.CTkButton(self.button_frame, text="Update", command=self._update_card, state="disabled")
        self.update_button.grid(row=0, column=1, padx=5, pady=5, sticky="nw")

        self.delete_button = ctk.CTkButton(self.button_frame, text="Delete", command=self._delete_card, state="disabled")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="nw")

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self._clear_fields)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5, sticky="nw")

        # self.send_email_button = ctk.CTkButton(self.button_frame, text="Send Email", command=self._send_email) # New button
        # self.send_email_button.grid(row=0, column=4, padx=5, pady=5, sticky="nw")

        self.close_button = ctk.CTkButton(self.button_frame, text="Close", command=self.root.destroy)
        self.close_button.grid(row=0, column=4, padx=5, pady=5, sticky="nw")

if __name__ == "__main__":
    root = ctk.CTk()
    app = BusinessCardApp(root)
    root.mainloop()