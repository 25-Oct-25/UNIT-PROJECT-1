import json
import os
from PyPDF2 import PdfReader

JSON_PATH = os.path.join("data", "user_files.json")

class ViewHistory:
    def __init__(self):
        self.data = self.load_all_records()

    def load_all_records(self):
        """Load all saved records from the JSON file."""
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def get_user_files(self, user_email):
        """Get all files belonging to a specific user."""
        return [record for record in self.data if record.get("user_email") == user_email]

    def read_file_content(self, path):
        """Read and display text content from a file."""
        if not os.path.exists(path):
            print("\nFile not found on disk.")
            return None

        
        if path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        elif path.endswith(".pdf"):
            try:
                reader = PdfReader(path)
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return None
        else:
            print("\nUnsupported file type for preview.")
            return None

    def show_user_videos(self, user_email):
        """Display all unique videos for the logged-in user."""
        self.data = self.load_all_records()
        user_files = self.get_user_files(user_email)

        if not user_files:
            print("\nYou have no saved files yet.")
            return None

  
        videos = list({f["video_title"] for f in user_files})
        print("\n--- Your Saved Videos ---")
        for i, video in enumerate(videos, 1):
            print(f"{i}.  {video}")
        print("-------------------------")

        choice = input("Enter the number of the video to view its files (or press Enter to go back): ").strip()
        if not choice.isdigit():
            print("Returning to menu...")
            return None

        index = int(choice) - 1
        if index < 0 or index >= len(videos):
            print("Invalid selection.")
            return None

        self.show_files_for_video(user_email, videos[index])

    def show_files_for_video(self, user_email, video_name):
        """Display all related files for a specific video."""
        from email_sender import EmailSender
        email_sender = EmailSender()

        self.data = self.load_all_records()
        user_files = self.get_user_files(user_email)
        video_files = [f for f in user_files if f["video_title"] == video_name]

        print(f"\n--- Files for {video_name} ---")
        for i, file in enumerate(video_files, 1):
            print(f"{i}.  {file['file_type'].capitalize()} | {file['path']} | 🕓 {file['date_created']}")
        print("-----------------------------")

        choice = input("Enter the number of the file to open (or press Enter to go back): ").strip()
        if not choice.isdigit():
            print("Returning to menu...")
            return None

        index = int(choice) - 1
        if index < 0 or index >= len(video_files):
            print("Invalid selection.")
            return None

        selected_file = video_files[index]
        content = self.read_file_content(selected_file["path"])
        if content:
            print("\n--- File Content ---")
            print(content[:1000])  
            print("---------------------")

            send_choice = input("\nWould you like to send this file to your email? (yes/no): ").strip().lower()
            if send_choice == "yes":
                email_sender.send_email(
                    user_email,
                    subject=f"Your {selected_file['file_type']} File",
                    body=f"Here’s your {selected_file['file_type']} file from Smart Video Assistant.",
                    attachment_path=selected_file["path"]
                )
                print("File sent successfully!")
            else:
                print("Skipped sending.")
        print("\nPress Enter to return to Main Menu...")
        input()
