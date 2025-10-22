from FileHandler import FileHandler
from AiHelper import AIHelper
from Story import Story
from EmailHelper import EmailHelper
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from EmailHelper import EmailHelper

class StoryManager:
    def __init__(self, username):
        self.username = username
        self.file_handler = FileHandler()
        self.ai_helper = AIHelper()

    # ====================== MAIN MENU ======================

    def resume_last_story(self):
        last_story_title = self.file_handler.get_last_story(self.username)
        if not last_story_title:
            print("No recent story found.")
            return

        stories_data = self.file_handler.load_stories(self.username)
        stories = [Story.from_dict(s) for s in stories_data]
        selected = next((s for s in stories if s.title == last_story_title), None)

        if not selected:
            print("Last story not found.")
            return

        print(f"\nYour last story was: {selected.title}")
        choice = input("Do you want to continue it? (y/n): ").strip().lower()
        if choice == "y":
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print("🔁 Returning to main menu...")

    def start_new_story(self):
        title = input("Enter a title for your story: ").strip()
        genre = input("Choose a genre (Drama, Adventure, Fantasy, Romance): ").strip()
        length = input("Do you want it short or long? ").strip().lower()
        prompt = input("Write the opening for your story: ").strip()

        print("\n✨ Generating the first part of your story...\n")
        result = self.ai_helper.generate_part(prompt, genre, length)

        story = Story(title, genre, length)
        story.add_part(result["text"])

        stories = self.file_handler.load_stories(self.username)
        stories.append(story.to_dict())
        self.file_handler.save_stories(self.username, stories)
        self.file_handler.set_last_story(self.username, story.title)

        print(f"\n📖 You’re now reading: '{story.title}' 🌙")
        print("=" * 50)
        print(f"Genre: {story.genre.capitalize()} | Length: {story.length.capitalize()}")
        print("=" * 50 + "\n")

        self._print_story_text(result["text"])
        self._ask_user_choice(result, story, stories)

    # ====================== ASK USER CHOICE ======================

    def _ask_user_choice(self, result, story, stories):
        if not result["options"]:
            print("⚠️ No choices were generated. Creating defaults...")
            result["options"] = [
                "1. Continue the journey.",
                "2. Change direction of the story.",
                "3. End the story gracefully."
            ]

        print("\nChoose what happens next:")
        for opt in result["options"]:
            print(opt)
        print("0. 🛑 Stop and save progress")

        while True:
            choice = input("\nEnter 1, 2, 3 to continue or 0 to stop: ").strip()
            if choice == "0":
                print("\n✅ Progress saved. You can resume later.")
                self._save_stories(stories)
                print("🔁 Returning to main menu...")
                return
            elif choice in ["1", "2", "3"]:
                index = int(choice) - 1
                if index < len(result["options"]):
                    story.last_choice = result["options"][index]
                    self._story_loop(story, stories, auto_continue=True)
                    break
                else:
                    print("⚠️ This choice is unavailable, please try again.")
            else:
                print("❌ Invalid input. Please enter 1, 2, 3 or 0.")

    # ====================== STORY LOOP ======================

    def _story_loop(self, selected, stories, auto_continue=False):
        print("\n✨ Generating the next part...\n")

        prompt = (
            f"Summary of previous parts:\n{self._summarize_story(selected.parts[:-1])}\n\n"
            f"Here’s the last scene of the story:\n{selected.parts[-1][-500:]}"
        )

        if selected.last_choice:
            prompt += f"\n\nContinue the story focusing on the choice: {selected.last_choice}"

        prompt += "\n\nContinue naturally from where the story left off. Do NOT restart or repeat previous events."

        result = self.ai_helper.generate_part(prompt, selected.genre, selected.length)
        new_part = result["text"]
        selected.add_part(new_part)

        part_number = len(selected.parts)
        print(f"\n🪄 Part {part_number}:")
        print("-" * 40)
        self._print_story_text(new_part)
        print("-" * 40)
        print(f"🕯️ End of Part {part_number} — progress saved automatically.\n")

        self._save_stories(stories)

        lines = [l.strip() for l in new_part.split("\n") if l.strip()]
        has_choices = any(line.startswith(("1.", "2.", "3.")) for line in lines)
        is_true_end = "THE END" in new_part.upper() and not has_choices

        if is_true_end:
            print("\n🏁 The story has reached its end. Well done!")
            print("=" * 50)
            print("Generated using AI Interactive Story Creator by Lama 🌙")
            print("=" * 50 + "\n")
            print("🔁 Returning to main menu...")
            return

        self._ask_user_choice(result, selected, stories)

    # ====================== STORY MANAGEMENT ======================

    def load_old_stories(self):
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("\n📂 No saved stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print("\n📜 Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.title} ({s.genre}, {len(s.parts)} parts)")

        choice = input("\nEnter the number of the story to continue: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(stories):
            selected = stories[int(choice) - 1]
            print(f"\n✨ Continuing '{selected.title}'...")
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print("⚠️ Invalid selection. Returning to main menu.")

    def view_old_story(self):
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("\n📂 You don’t have any saved stories.")
            return

        print("\n📚 Your old stories:")
        for s in stories_data:
            print(f"• {s['title']} ({s['genre']}, {len(s['parts'])} parts)")

    def export_story(self):


        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print("\n⚠️ No stories to export.")
            return

        print("\n📤 Select a story to export:")
        for i, s in enumerate(stories_data, start=1):
            print(f"{i}. {s['title']}")

        choice = input("Enter number: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories_data) + 1):
            print("❌ Invalid choice.")
            return

        selected = stories_data[int(choice) - 1]
        title = selected['title'].replace(' ', '_')

        export_dir = "Exports"
        os.makedirs(export_dir, exist_ok=True)

        print("\n📦 Choose export type:")
        print("1. 📄 Export as TXT file")
        print("2. 🧾 Export as PDF file")
        print("3. ✉️ Send via Email")

        export_choice = input("Enter 1, 2, or 3: ").strip()
        creation_date = datetime.now().strftime("%d %b %Y")  # 🗓️ التاريخ الحالي

        # ========== 1. TXT Export ==========
        if export_choice == "1":
            txt_path = os.path.join(export_dir, f"{title}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {selected['title']}\n")
                f.write(f"Genre: {selected['genre']}\n")
                f.write(f"Created on: {creation_date}\n")
                f.write(f"Author: {self.username}\n\n")
                for i, part in enumerate(selected["parts"], start=1):
                    f.write(f"--- Part {i} ---\n{part}\n\n")
                f.write("\nGenerated using AI Interactive Story Creator by Lama 🌙")
            print(f"\n✅ Story exported successfully as '{txt_path}'")

            open_now = input("\n📂 Open the exported file now? (y/n): ").strip().lower()
            if open_now == "y":
                try:
                    os.startfile(txt_path)
                except Exception as e:
                    print(f"⚠️ Couldn't open file automatically: {e}")

        # ========== 2. PDF Export ==========
        elif export_choice == "2":
            pdf_path = os.path.join(export_dir, f"{title}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            page_number = 1  # 🔢 بداية ترقيم الصفحات

            def draw_footer():
                """رقم الصفحة في الأسفل"""
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(colors.grey)
                c.drawCentredString(width / 2, 40, f"Page {page_number}")

            y = height - 100

            # 🌙 غلاف جميل بتفاصيل القصة
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(width / 2, y, selected['title'])
            y -= 30

            c.setFont("Helvetica-Oblique", 13)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, y, f"By {self.username.capitalize()} | {selected['genre']} Story")
            y -= 20

            c.setFont("Helvetica", 11)
            c.setFillColor(colors.grey)
            c.drawCentredString(width / 2, y, f"Created on: {creation_date}")  # 🗓️ التاريخ
            y -= 25

            c.setStrokeColor(colors.grey)
            c.line(80, y, width - 80, y)
            y -= 50

            # 📝 محتوى القصة
            for i, part in enumerate(selected["parts"], start=1):
                if y <= 100:
                    draw_footer()
                    c.showPage()
                    page_number += 1
                    y = height - 100

                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(colors.darkred)
                c.drawString(80, y, f"Part {i}")
                y -= 20

                c.setFont("Helvetica", 12)
                c.setFillColor(colors.black)
                for line in part.split("\n"):
                    if y <= 80:
                        draw_footer()
                        c.showPage()
                        page_number += 1
                        y = height - 100
                        c.setFont("Helvetica", 12)
                    c.drawString(80, y, line[:100])
                    y -= 16
                y -= 25

            # 🧾 تذييل + رقم الصفحة
            draw_footer()
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColor(colors.grey)
            c.drawCentredString(width / 2, 60, "Generated using AI Interactive Story Creator 🌙")
            c.save()

            print(f"\n✅ Story exported successfully as '{pdf_path}'")

            open_now = input("\n📂 Open the exported PDF now? (y/n): ").strip().lower()
            if open_now == "y":
                try:
                    os.startfile(pdf_path)
                except Exception as e:
                    print(f"⚠️ Couldn't open file automatically: {e}")

        # ========== 3. Email ==========
        elif export_choice == "3":
            email_helper = EmailHelper()
            receiver_email = input("Enter recipient email: ").strip()

            print("\n📧 Choose email attachment format:")
            print("1. Send as PDF")
            print("2. Send as TXT")
            attach_choice = input("Enter 1 or 2: ").strip()

            attachments = []

            if attach_choice == "1":
                pdf_path = os.path.join(export_dir, f"{title}.pdf")
                c = canvas.Canvas(pdf_path, pagesize=A4)
                width, height = A4
                page_number = 1

                def draw_footer_email():
                    c.setFont("Helvetica-Oblique", 9)
                    c.setFillColor(colors.grey)
                    c.drawCentredString(width / 2, 40, f"Page {page_number}")

                y = height - 100
                c.setFont("Helvetica-Bold", 22)
                c.setFillColor(colors.darkblue)
                c.drawCentredString(width / 2, y, selected['title'])
                y -= 30
                c.setFont("Helvetica-Oblique", 13)
                c.drawCentredString(width / 2, y, f"By {self.username.capitalize()} | {selected['genre']} Story")
                y -= 20
                c.setFont("Helvetica", 11)
                c.setFillColor(colors.grey)
                c.drawCentredString(width / 2, y, f"Created on: {creation_date}")
                y -= 40

                for i, part in enumerate(selected["parts"], start=1):
                    if y <= 100:
                        draw_footer_email()
                        c.showPage()
                        page_number += 1
                        y = height - 100
                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkred)
                    c.drawString(80, y, f"Part {i}")
                    y -= 20
                    c.setFont("Helvetica", 12)
                    c.setFillColor(colors.black)
                    for line in part.split("\n"):
                        if y <= 80:
                            draw_footer_email()
                            c.showPage()
                            page_number += 1
                            y = height - 100
                            c.setFont("Helvetica", 12)
                        c.drawString(80, y, line[:100])
                        y -= 16
                    y -= 25

                draw_footer_email()
                c.setFont("Helvetica-Oblique", 10)
                c.setFillColor(colors.grey)
                c.drawCentredString(width / 2, 60, "Generated using AI Interactive Story Creator by Lama 🌙")
                c.save()
                attachments.append(pdf_path)
                print(f"📎 PDF ready: {pdf_path}")

            elif attach_choice == "2":
                txt_path = os.path.join(export_dir, f"{title}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"Title: {selected['title']}\n")
                    f.write(f"Genre: {selected['genre']}\n")
                    f.write(f"Created on: {creation_date}\n")
                    f.write(f"Author: {self.username}\n\n")
                    for i, part in enumerate(selected["parts"], start=1):
                        f.write(f"--- Part {i} ---\n{part}\n\n")
                    f.write("\nGenerated using AI Interactive Story Creator by Lama 🌙")
                attachments.append(txt_path)
                print(f"📎 TXT ready: {txt_path}")
            else:
                print("❌ Invalid choice. Cancelled.")
                return

            subject = f"Your Story: {selected['title']}"
            body = f"Hey 🌙,\nHere’s your story '{selected['title']}' attached for you!"
            email_helper.send_email(receiver_email, subject, body, attachments=attachments)

        else:
            print("⚠️ Invalid option. Returning to main menu.")


    # ====================== UTILITIES ======================

    def _print_story_text(self, text):
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        story_only = []
        for line in lines:
            if not line.startswith(("1.", "2.", "3.")):
                story_only.append(line)
            else:
                break
        print("\n".join(story_only))

    def _summarize_story(self, parts):
        if not parts:
            return ""
        text = " ".join(parts)
        return text[-600:] if len(text) > 600 else text

    def _save_stories(self, stories):
        story_dicts = [s.to_dict() if isinstance(s, Story) else s for s in stories]
        self.file_handler.save_stories(self.username, story_dicts)
