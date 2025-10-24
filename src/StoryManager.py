#Project imports 
from src.FileHandler import FileHandler
from src.AiHelper import AIHelper
from src.Story import Story
from src.EmailHelper import EmailHelper

#Built-in modules
import os
import re
from datetime import datetime

#ReportLab (PDF generation)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors

#CLI colors 
from colorama import Fore, Style, init

init(autoreset=True, convert=True)


class StoryManager:
    def __init__(self, username):
        """Initialize StoryManager with the current username and helper classes."""
        self.username = username
        self.file_handler = FileHandler()
        self.ai_helper = AIHelper()

    # MAIN MENU 

    def resume_last_story(self):
        """Load and continue the user's most recent story if available."""
        last_story_title = self.file_handler.get_last_story(self.username)
        if not last_story_title:
            print(Fore.YELLOW + "⚠️ No recent story found.")
            return

        stories_data = self.file_handler.load_stories(self.username)
        stories = [Story.from_dict(s) for s in stories_data]
        selected = next((s for s in stories if s.title == last_story_title), None)

        if not selected:
            print(Fore.RED + "❌ Last story not found.")
            return

        print(Fore.CYAN + f"\n📖 Your last story was: {selected.title}")
        choice = input("Do you want to continue it? (y/n): ").strip().lower()
        if choice == "y":
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")

    def start_new_story(self):
        """Start a new story by getting user input, generating the first part, and saving it."""
        print(Fore.CYAN + "\n🪄 Let's create your new story!" + Style.RESET_ALL)
        title = input("Enter a title for your story: ").strip()
        genre = input("Choose a genre (Drama, Adventure, Fantasy, Romance): ").strip()
        length = input("Do you want it short or long? ").strip().lower()
        prompt = input("Write the opening for your story: ").strip()

        print(Fore.LIGHTBLUE_EX + "\n✨ Generating the first part of your story...\n")
        result = self.ai_helper.generate_part(prompt, genre, length)

        story = Story(title, genre, length)
        story.add_part(result["text"])

        stories = self.file_handler.load_stories(self.username)
        stories.append(story.to_dict())
        self.file_handler.save_stories(self.username, stories)
        self.file_handler.set_last_story(self.username, story.title)

        print(Fore.CYAN + f"\n📚 You’re now reading: '{story.title}' 🌙")
        print(Fore.CYAN + "=" * 50)
        print(f"Genre: {story.genre.capitalize()} | Length: {story.length.capitalize()}")
        print("=" * 50 + "\n" + Style.RESET_ALL)

        self._print_story_text(result["text"])
        self._ask_user_choice(result, story, stories)

    # ASK USER CHOICE 

    def _ask_user_choice(self, result, story, stories):
        """Display the generated choices and handle user's selection for the next part."""

        if not result["options"] or len(result["options"]) < 3:
            print(Fore.YELLOW + "⚠️ AI did not generate full options, adding defaults..." + Fore.RESET)
            result["options"] = [
                "1. Continue the journey.",
                "2. Change direction of the story.",
                "3. End the story gracefully."
            ]


        print(Fore.CYAN + "\nChoose what happens next:" + Style.RESET_ALL)
        for opt in result["options"]:
            print(Fore.LIGHTYELLOW_EX + opt)
        print(Fore.LIGHTRED_EX + "0. 🛑 Stop and save progress to contune later" + Style.RESET_ALL)

        while True:
            choice = input(Fore.CYAN + "\nEnter 1, 2, 3 to continue or 0 to stop: ").strip()
            if choice == "0":
                print(Fore.GREEN + "\n✅ Progress saved. You can resume later.")
                self._save_stories(stories)
                print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")
                return
            elif choice in ["1", "2", "3"]:
                index = int(choice) - 1
                if index < len(result["options"]):
                    story.last_choice = result["options"][index]
                    self._story_loop(story, stories, auto_continue=True)
                    break
                else:
                    print(Fore.RED + "⚠️ This choice is unavailable, please try again.")
            else:
                print(Fore.RED + "❌ Invalid input. Please enter 1, 2, 3 or 0.")

    # STORY LOOP 

    def _story_loop(self, selected, stories, auto_continue=False):
        """Generate and display the next part of the story, continuing based on user choices."""

        print(Fore.LIGHTBLUE_EX + "\n✨ Generating the next part...\n")

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
        print(Fore.CYAN + f"\n🪄 Part {part_number}:")
        print(Fore.LIGHTBLUE_EX + "-" * 40)
        self._print_story_text(new_part)
        print(Fore.LIGHTBLUE_EX + "-" * 40)
        print(Fore.GREEN + f"🕯️ End of Part {part_number} — progress saved automatically.\n")

        self._save_stories(stories)

        lines = [l.strip() for l in new_part.split("\n") if l.strip()]
        has_choices = any(line.startswith(("1.", "2.", "3.")) for line in lines)
        is_true_end = "THE END" in new_part.upper() and not has_choices

        if is_true_end:
            print(Fore.MAGENTA + "\n🏁 The story has reached its end. Well done!")
            print(Fore.LIGHTBLUE_EX + "=" * 50)
            print("Generated using AI Interactive Story Creator 🌙")
            print("=" * 50 + "\n")
            print(Fore.LIGHTBLUE_EX + "↩️ Returning to main menu...")
            return

        self._ask_user_choice(result, selected, stories)

    # STORY MANAGEMENT 

    def load_old_stories(self):
        """Load and allow the user to continue one of their saved stories."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n📂 No saved stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print(Fore.CYAN + "\n📜 Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.title} ({s.genre}, {len(s.parts)} parts)")

        choice = input(Fore.CYAN + "\nEnter the number of the story to continue: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(stories):
            selected = stories[int(choice) - 1]
            print(Fore.LIGHTBLUE_EX + f"\n✨ Continuing '{selected.title}'...")
            self._story_loop(selected, stories, auto_continue=True)
        else:
            print(Fore.RED + "⚠️ Invalid selection. Returning to main menu.")

    def view_old_story(self):
        """Display a list of all saved stories with their details (title, genre, parts count)."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n📂 You don’t have any saved stories.")
            return

        print(Fore.CYAN + "\n📚 Your old stories:")
        for s in stories_data:
            print(f"• {s['title']} ({s['genre']}, {len(s['parts'])} parts)")

    def delete_story(self):
        """Allow the user to delete one of their saved stories (with confirmation)."""
        stories_data = self.file_handler.load_stories(self.username)

        if not stories_data:
            print(Fore.YELLOW + "📭 No saved stories found.")
            return

        stories = [Story.from_dict(s) for s in stories_data]
        print(Fore.CYAN + "\n🗑️ Your saved stories:")
        for i, s in enumerate(stories, start=1):
            print(f"{i}. {s.get_summary()}")

        choice = input(Fore.CYAN + "\nEnter the number of the story to delete (or 0 to cancel): ").strip()

        if choice == "0":
            print(Fore.LIGHTBLUE_EX + "❎ Deletion canceled. Returning to main menu...")
            return

        if not choice.isdigit() or int(choice) not in range(1, len(stories) + 1):
            print(Fore.RED + "⚠️ Invalid choice.")
            return

        selected_story = stories[int(choice) - 1]
        confirm = input(Fore.YELLOW + f"Are you sure you want to delete '{selected_story.title}'? (y/n): ").strip().lower()
        if confirm != "y":
            print(Fore.LIGHTBLUE_EX + "❎ Deletion canceled. Returning to main menu...")
            return

        deleted_story = stories.pop(int(choice) - 1)
        self.file_handler.save_stories(self.username, [s.to_dict() for s in stories])

        last_story = self.file_handler.get_last_story(self.username)
        if last_story == deleted_story.title:
            data = self.file_handler._read_data()
            if self.username in data and "last_story" in data[self.username]:
                del data[self.username]["last_story"]
                self.file_handler._write_data(data)
            print(Fore.CYAN + "🗒️ Removed from recent story record.")

        print(Fore.GREEN + f"✅ Story '{deleted_story.title}' has been deleted successfully!")

    def export_story(self):
        """Export a story as a TXT or PDF file, or send it via email with attachments."""
        stories_data = self.file_handler.load_stories(self.username)
        if not stories_data:
            print(Fore.YELLOW + "\n⚠️ No stories to export.")
            return

        print(Fore.CYAN + "\n📤 Select a story to export:")
        for i, s in enumerate(stories_data, start=1):
            print(f"{i}. {s['title']}")

        choice = input(Fore.CYAN + "Enter number: ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(stories_data) + 1):
            print(Fore.RED + "❌ Invalid choice.")
            return

        selected = stories_data[int(choice) - 1]
        title = selected['title'].replace(' ', '_')

        export_dir = "Exports"
        os.makedirs(export_dir, exist_ok=True)

        print(Fore.CYAN + "\n Choose export type:")
        print("1. 🧾 Export as PDF file")
        print("2. ✉️ Send via Email")

        export_choice = input(Fore.CYAN + "Enter 1 or 2: ").strip()
        creation_date = datetime.now().strftime("%d %b %Y")


        # 1. PDF Export 
        if export_choice == "1":
                    
            pdf_path = os.path.join(export_dir, f"{title}.pdf")
            self._export_as_novel_pdf(selected, pdf_path, creation_date)

        # 2. EMAIL EXPORT 
        elif export_choice == "2":
            email_helper = EmailHelper()
            receiver_email = input(Fore.CYAN + "Enter recipient email: ").strip()

            print(Fore.CYAN + "\n📧 Sending story as PDF attachment...")
            attachments = []

            pdf_path = os.path.join(export_dir, f"{title}.pdf")
            self._export_as_novel_pdf(selected, pdf_path, creation_date)
            attachments.append(pdf_path)
            print(Fore.GREEN + f"📎 PDF ready: {pdf_path}")

            subject = f"Your Story: {selected['title']}"
            body = (
                f"Hello 🌙,\n\n"
                f"Attached below is your beautifully formatted story titled '{selected['title']}'.\n"
                "Enjoy reading your adventure, and thank you for using AI Interactive Story Creator! 📖\n\n"
                "— The Story Creator Team 🌙"
            )

            email_helper.send_email(receiver_email, subject, body, attachments=attachments)



        else:
            print(Fore.RED + "⚠️ Invalid option. Returning to main menu.")


    def _print_story_text(self, text):
        """Print the story text without showing the choice options."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        story_only = []
        for line in lines:
            if not line.startswith(("1.", "2.", "3.")):
                story_only.append(line)
            else:
                break
        print(Fore.WHITE + "\n".join(story_only)+Fore.RESET)

    def _summarize_story(self, parts):
        """Generate a short summary of previous story parts to avoid repetition in AI generation."""
        if not parts:
            return ""
        text = " ".join(parts)
        return text[-600:] if len(text) > 600 else text

    def _save_stories(self, stories):
        """Save the updated list of stories for the current user."""
        story_dicts = [s.to_dict() if isinstance(s, Story) else s for s in stories]
        self.file_handler.save_stories(self.username, story_dicts)
    
    def _export_as_novel_pdf(self, selected, output_path, creation_date):
        """
        export story as novel style pdf (with cover page, light background, and footer logo)
        """

        # pdf setup
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60 )

        story_flow = []
        styles = getSampleStyleSheet()

        #text styles 
        cover_title = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName='Times-Bold',
            fontSize=26,
            textColor=colors.darkblue,  
            alignment=TA_CENTER,
            spaceAfter=20 )

        cover_sub = ParagraphStyle(
            'CoverSub',
            parent=styles['Normal'],
            fontName='Times-Italic',
            fontSize=14,
            textColor='gray',
            alignment=TA_CENTER,
            spaceAfter=10 )

        cover_info = ParagraphStyle(
            'CoverInfo',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            textColor='darkgray',
            alignment=TA_CENTER,
            spaceAfter=20 )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=16,
            leading=18,
            alignment=4,  
            firstLineIndent=20  )

        # cover page 
        story_flow.append(Spacer(1, 2.5 * inch))
        story_flow.append(Paragraph(selected['title'], cover_title))
        story_flow.append(Spacer(1, 0.1 * inch))
        story_flow.append(Paragraph("<font color='grey'>───────────────</font>", cover_sub))
        story_flow.append(Spacer(1, 0.15 * inch))
        cover_author = ParagraphStyle(
            'CoverAuthor',
            parent=styles['Normal'],
            fontName='Times-BoldItalic',
            fontSize=15,
            textColor=colors.slategrey,
            alignment=TA_CENTER,
            spaceAfter=12 )
        story_flow.append(Paragraph(f"By {self.username}", cover_author))
        story_flow.append(Paragraph(f"{selected['genre'].capitalize()} Story", cover_sub))
        story_flow.append(Paragraph(f"Created on: {creation_date}", cover_info))
        story_flow.append(PageBreak())

        # main story page 
        combined_story = ""
        for part in selected["parts"]:
            clean_text = re.sub(r'\b\d+\.\s.*', '', part)  # remove choices option
            clean_text = re.sub(r'(possible actions|choices|options).*', '', clean_text, flags=re.IGNORECASE)
            combined_story += " " + clean_text.strip()

        # remove extra spaces
        combined_story = re.sub(r'\s+', ' ', combined_story).strip()

        # add full story paragraph
        story_flow.append(Paragraph(combined_story, body_style))

        # export final pdf
        doc.build(story_flow, onFirstPage=self._draw_cover_background)
        print(Fore.GREEN + f"\n✅ Story exported successfully : '{output_path}'" + Fore.RESET)


    def _draw_cover_background(self,canvas_obj, doc):
        """draw light gray background and footer logo"""
        canvas_obj.saveState()
        width, height = A4

        # light gray background
        canvas_obj.setFillColorRGB(0.95, 0.95, 0.95)
        canvas_obj.rect(0, 0, width, height, fill=1)

        # footer logo
        canvas_obj.setFont("Helvetica-Oblique", 10)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawCentredString(width / 2, 40, "Generated using AI Interactive Story Creator 🌙")

        canvas_obj.restoreState()

