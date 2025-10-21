import time
from utils.openai_helper import generate_puzzle
from utils.colors import *

class EscapeRoom:
    """
    Escape Room Game.
    - Each room is randomly generated with a logical puzzle.
    - Player has limited time and attempts to solve it.
    - Points and achievements are given based on performance.
    """

    def __init__(self, user=None):
        self.user = user
        self.room = None
        self.start_time = None
        self.time_limit = 60
        self.attempts_allowed = 3
        self.attempts_used = 0
        self.hints_used = 0

    @staticmethod
    def calculate_points(correct, total_elapsed, attempts_used, hints_used, time_limit=60):
        """Calculate points based on performance"""
        if correct:
            base = 20
            speed_bonus = max(0, int((time_limit - total_elapsed) // 2))
            attempt_penalty = (attempts_used - 1) * 5
            hint_penalty = hints_used * 7
            points = max(5, base + speed_bonus - attempt_penalty - hint_penalty)
        else:
            points = 0
        return points
 
    
    def _award_achievements(self, points, total_elapsed):
        """Grants achievements based on performance"""
        if not self.user:
            return

        # always award beginner
        self.user.add_achievement("Escape Beginner")
        print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Escape Beginner"+RESET)

        if points >= 40:
            self.user.add_achievement("Master of the Mind")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Master of the Mind"+RESET)

        if total_elapsed < 20:
            self.user.add_achievement("Fast Thinker")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: Fast Thinker"+RESET)

        if self.hints_used == 0:
            self.user.add_achievement("No Help Needed")
            print(Fore.LIGHTYELLOW_EX+"🏅 Achievement unlocked: No Help Needed"+RESET)

    

       

    
    def play(self):
        """Main game logic"""
        self.room = generate_puzzle("easy", "mystery room")
        print(CYAN + "\n🔐 You enter a mysterious chamber..." + RESET)
        print(YELLOW + f"Puzzle Type: {self.room.get('type', 'logic').upper()}" + RESET)
        print(self.room["puzzle"])
        print(GREEN + f"You have {self.time_limit} seconds and {self.attempts_allowed} attempts. Good luck!" + RESET)

        self.start_time = time.time()
        self.attempts_used = 0
        self.hints_used = 0
        correct = False

        while self.attempts_used < self.attempts_allowed:
            remaining_time = max(0, int(self.time_limit - (time.time() - self.start_time)))
            print(YELLOW + f"(⏳ {remaining_time} seconds left)" + RESET)
            ans = input("Your answer (or type 'hint'): ").strip().lower()

            if ans == "hint":
                if self.hints_used >= 1:
                    print(RED + "No more hints left!" + RESET)
                    continue
                self.hints_used += 1
                print(YELLOW + "Hint: " + RESET + self.room.get("hint", "No hint available."))
                continue

            self.attempts_used += 1

            if ans == self.room["answer"].lower():
                correct = True
                break
            else:
                print(RED + "Wrong answer. Try again!" + RESET)

        total_elapsed = time.time() - self.start_time
        points = self.calculate_points(correct, total_elapsed, self.attempts_used, self.hints_used, self.time_limit)

        if correct:
            print(GREEN + f"\nCorrect! You solved it in {int(total_elapsed)}s using {self.attempts_used} attempts." + RESET)
            print(GREEN + f"🏆 You earned {points} points!" + RESET)
            if self.user:
                self.user.add_score("EscapeRoom", points)
                self._award_achievements(points, total_elapsed)
        else:
            print(RED + "\n💥 You failed to solve the puzzle." + RESET)
            print(YELLOW + "Correct answer: " + RESET + self.room.get("answer"))
        
        again = input("Do you want to start again? (yes/no): ").lower()
        if again == "yes":
            self.play()

        input("\nPress Enter to continue...")
        return points


# test
'''if __name__ == "__main__":
    from users.user import User
    test_user = User("Ghala", "1234")
    game = EscapeRoom(test_user)
    game.play()'''