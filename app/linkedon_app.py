import json
import os
import re
import uuid

from models.user import User
from models.experience import Experience
from models.education import Education
# from models.post import Post, TextPost, JobPost, AchievementPost
# from models.connection import Connection

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database.json"
)


class LinkedOnApp:
    """
    Main controller class for the LinkedOn terminal application.
    Manages the database, user sessions, and all terminal menus.
    """

    def __init__(self):
        self.__users = {}         # { user_id: User }
        self.__posts = {}         # { post_id: Post }
        self.__connections = []   # [ Connection ]
        self.__current_user = None
        self.__load_database()

    # =========================================================================
    #  DATABASE
    # =========================================================================

    def __load_database(self):
        if not os.path.exists(DB_PATH):
            return
        try:
            with open(DB_PATH, "r") as f:
                data = json.load(f)
            self.__users = {
                uid: User.from_dict(u)
                for uid, u in data.get("users", {}).items()
            }
        except (json.JSONDecodeError, KeyError):
            print("  ⚠️  Database file is corrupted. Starting fresh.")

    def __save_database(self):
        data = {
            "users": {uid: u.to_dict() for uid, u in self.__users.items()},
            "posts": {pid: p.to_dict() for pid, p in self.__posts.items()},
            "connections": [c.to_dict() for c in self.__connections],
        }
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)

    # =========================================================================
    #  HELPERS
    # =========================================================================

    def __clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def __pause(self):
        input("\n  Press Enter to continue...")

    def __header(self, subtitle=""):
        self.__clear()
        print()
        print("  ██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗  ██████╗ ███╗   ██╗")
        print("  ██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██╔═══██╗████╗  ██║")
        print("  ██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██║  ██║██║   ██║██╔██╗ ██║")
        print("  ██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██║  ██║██║   ██║██║╚██╗██║")
        print("  ███████╗██║██║ ╚████║██║  ██╗███████╗██████╔╝╚██████╔╝██║ ╚████║")
        print("  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝")
        if subtitle:
            print()
            print(f"  {'─'*48}")
            print(f"  {subtitle}")
        print(f"  {'─'*48}")
        print()

    def __prompt(self, label, allow_empty=False):
        """Get non-empty input from the user."""
        while True:
            val = input(f"  {label}: ").strip()
            if val or allow_empty:
                return val
            print("  ⚠️   This field cannot be empty. Please try again.")

    @staticmethod
    def __valid_email(email):
        return re.match(r'^[\w.%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$', email) is not None

    def __email_taken(self, email):
        return any(u.email == email for u in self.__users.values())

    def __find_by_email(self, email):
        for u in self.__users.values():
            if u.email == email:
                return u
        return None

    # =========================================================================
    #  ENTRY POINT
    # =========================================================================

    def run(self):
        while True:
            self.__main_menu()

    # =========================================================================
    #  MAIN MENU
    # =========================================================================

    def __main_menu(self):
        self.__header()
        print("  Your Professional Network Starts Here.")
        print()
        print("  [1]  Register")
        print("  [2]  Log In")
        print("  [3]  Exit")
        print()
        choice = input("  Choose an option: ").strip()

        if choice == "1":
            self.__register()
        elif choice == "2":
            self.__login()
        elif choice == "3":
            self.__header()
            print("  Thanks for using LinkedOn. Goodbye! 👋")
            print()
            exit(0)
        else:
            print("\n  ⚠️   Invalid option. Please choose 1, 2, or 3.")
            self.__pause()

    # =========================================================================
    #  LOGIN & REGISTRATION
    # =========================================================================

    def __register(self):
        self.__header("CREATE AN ACCOUNT")

        # Email
        while True:
            email = self.__prompt("Email")
            if not self.__valid_email(email):
                print("  ⚠️   Invalid email format. Example: name@example.com")
                continue
            if self.__email_taken(email):
                print("  ⚠️   That email is already registered.")
                continue
            break

        # Password
        while True:
            password = self.__prompt("Password (min. 8 characters)")
            if len(password) < 8:
                print("  ⚠️   Password must be at least 8 characters long.")
                continue
            confirm = self.__prompt("Confirm Password")
            if password != confirm:
                print("  ⚠️   Passwords do not match. Please try again.")
                continue
            break

        user_id = str(uuid.uuid4())
        new_user = User(
            user_id=user_id,
            email=email,
            password_hash=User.hash_password(password),
        )
        self.__users[user_id] = new_user
        self.__save_database()

        print()
        print("  ✅  Account created successfully!")
        print("  Tip: Log in and complete your profile to get started.")
        self.__pause()

    def __login(self):
        self.__header("LOG IN")
        email = self.__prompt("Email")
        password = self.__prompt("Password")

        user = self.__find_by_email(email)
        if user is None or not user.verify_password(password):
            print()
            print("  ❌  Incorrect email or password.")
            self.__pause()
            return

        self.__current_user = user
        display_name = user.name if user.name else user.email
        print()
        print(f"  ✅  Welcome back, {display_name}!")
        self.__pause()
        self.__dashboard()

    # =========================================================================
    #  DASHBOARD
    # =========================================================================

    def __dashboard(self):
        while True:
            display_name = self.__current_user.name or self.__current_user.email
            self.__header(f"Logged in as: {display_name}")

            print("  [1]  View My Profile")
            print("  [2]  Edit Profile")
            print("  [3]  My Posts")
            print("  [4]  Network")
            print("  [5]  Feed")
            print("  [6]  Log Out")
            print()

            choice = input("  Choose an option: ").strip()

            if choice == "1":
                self.__view_my_profile()
            elif choice == "2":
                self.__edit_profile_menu()
            elif choice == "3":
                pass  # !!!
            elif choice == "4":
                pass  # !!!
            elif choice == "5":
                pass  # !!!
            elif choice == "6":
                self.__current_user = None
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # =========================================================================
    #  VIEW MY PROFILE
    # =========================================================================

    def __view_my_profile(self):
        self.__header("MY PROFILE")
        self.__current_user.display()
        print()
        post_count = len(self.__current_user.post_ids)
        conn_count = 0  # !!!
        print(f"  📝 Posts: {post_count}     🤝 Connections: {conn_count}")
        self.__pause()

    # =========================================================================
    #  EDIT PROFILE MENU
    # =========================================================================

    def __edit_profile_menu(self):
        while True:
            self.__header("EDIT PROFILE")
            print("  [1]  Edit Basic Info  (name, age, location, bio)")
            print("  [2]  Manage Skills")
            print("  [3]  Manage Work Experience")
            print("  [4]  Manage Education")
            print("  [5]  Change Password")
            print("  [6]  Back")
            print()
            choice = input("  Choose an option: ").strip()

            if choice == "1":
                self.__edit_basic_info()
            elif choice == "2":
                self.__manage_skills()
            elif choice == "3":
                self.__manage_experience()
            elif choice == "4":
                self.__manage_education()
            elif choice == "5":
                self.__change_password()
            elif choice == "6":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # Edit Basic Info 

    def __edit_basic_info(self):
        self.__header("EDIT BASIC INFO")
        u = self.__current_user
        print("  Press Enter to keep the current value.\n")

        name = input(f"  Name [{u.name}]: ").strip()
        if name:
            u.name = name

        while True:
            age_in = input(f"  Age [{u.age}]: ").strip()
            if not age_in:
                break
            if age_in.isdigit() and 1 <= int(age_in) <= 120:
                u.age = int(age_in)
                break
            print("  ⚠️   Please enter a valid age (1–120).")

        location = input(f"  Location [{u.location}]: ").strip()
        if location:
            u.location = location

        bio = input(f"  Headline/Bio [{u.bio}]: ").strip()
        if bio:
            u.bio = bio

        self.__save_database()
        print()
        print("  ✅  Profile updated!")
        self.__pause()

    # Manage Skills 

    def __manage_skills(self):
        while True:
            self.__header("MANAGE SKILLS")
            skills = self.__current_user.skills

            if skills:
                print("  Your Skills:\n")
                for i, s in enumerate(skills, 1):
                    print(f"  [{i}]  {s}")
            else:
                print("  You haven't added any skills yet.")

            print()
            print("  [A]  Add Skill")
            print("  [D]  Delete Skill")
            print("  [B]  Back")
            print()
            choice = input("  Choose an option: ").strip().upper()

            if choice == "A":
                skill = self.__prompt("Skill name")
                self.__current_user.add_skill(skill)
                self.__save_database()
                print(f"\n  ✅  '{skill}' added to your skills!")
                self.__pause()

            elif choice == "D":
                if not skills:
                    print("\n  ⚠️   No skills to delete.")
                    self.__pause()
                    continue
                idx = input("  Enter skill number to delete: ").strip()
                if idx.isdigit() and 1 <= int(idx) <= len(skills):
                    removed = skills[int(idx) - 1]
                    self.__current_user.remove_skill(removed)
                    self.__save_database()
                    print(f"\n  ✅  '{removed}' removed.")
                    self.__pause()
                else:
                    print("\n  ⚠️   Invalid number.")
                    self.__pause()

            elif choice == "B":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # Manage Work Experience

    def __manage_experience(self):
        while True:
            self.__header("WORK EXPERIENCE")
            exps = self.__current_user.experiences

            if exps:
                print("  Your Work Experience:\n")
                for i, e in enumerate(exps, 1):
                    print(f"  [{i}]")
                    e.display()
                    print()
            else:
                print("  No work experience added yet.\n")

            print("  [A]  Add Experience")
            print("  [E]  Edit Experience")
            print("  [D]  Delete Experience")
            print("  [B]  Back")
            print()
            choice = input("  Choose an option: ").strip().upper()

            if choice == "A":
                self.__add_experience()
            elif choice == "E":
                if not exps:
                    print("\n  ⚠️   Nothing to edit.")
                    self.__pause()
                else:
                    self.__edit_experience(exps)
            elif choice == "D":
                if not exps:
                    print("\n  ⚠️   Nothing to delete.")
                    self.__pause()
                else:
                    idx = input("  Enter experience number to delete: ").strip()
                    if idx.isdigit() and 1 <= int(idx) <= len(exps):
                        self.__current_user.remove_experience(int(idx) - 1)
                        self.__save_database()
                        print("\n  ✅  Experience removed.")
                        self.__pause()
                    else:
                        print("\n  ⚠️   Invalid number.")
                        self.__pause()
            elif choice == "B":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __add_experience(self):
        self.__header("ADD WORK EXPERIENCE")
        company = self.__prompt("Company name")
        role = self.__prompt("Job title / Role")
        start = self.__prompt("Start date  (e.g. Jan 2025)")

        is_curr = input("  Is this your current job? (y/n): ").strip().lower() == "y"
        end = None
        if not is_curr:
            end = self.__prompt("End date  (e.g. Dec 2026)")

        exp = Experience(company=company, role=role,
                         start_date=start, end_date=end, is_current=is_curr)
        self.__current_user.add_experience(exp)
        self.__save_database()
        print("\n  ✅  Work experience added!")
        self.__pause()

    def __edit_experience(self, exps):
        idx = input("  Enter experience number to edit: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(exps)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        exp = exps[int(idx) - 1]
        self.__header("EDIT WORK EXPERIENCE")
        print("  Press Enter to keep the current value.\n")

        c = input(f"  Company [{exp.company}]: ").strip()
        if c:
            exp.company = c

        r = input(f"  Role [{exp.role}]: ").strip()
        if r:
            exp.role = r

        s = input(f"  Start date [{exp.start_date}]: ").strip()
        if s:
            exp.start_date = s

        curr = input(f"  Currently working here? (y/n) [{'y' if exp.is_current else 'n'}]: ").strip().lower()
        if curr == "y":
            exp.is_current = True
            exp.end_date = None
        elif curr == "n":
            exp.is_current = False
            e = input(f"  End date [{exp.end_date}]: ").strip()
            if e:
                exp.end_date = e

        self.__save_database()
        print("\n  ✅  Experience updated!")
        self.__pause()

    # Manage Education
    def __manage_education(self):
        while True:
            self.__header("EDUCATION")
            edus = self.__current_user.educations

            if edus:
                print("  Your Education:\n")
                for i, e in enumerate(edus, 1):
                    print(f"  [{i}]")
                    e.display()
                    print()
            else:
                print("  No education added yet.\n")

            print("  [A]  Add Education")
            print("  [E]  Edit Education")
            print("  [D]  Delete Education")
            print("  [B]  Back")
            print()
            choice = input("  Choose an option: ").strip().upper()

            if choice == "A":
                self.__add_education()
            elif choice == "E":
                if not edus:
                    print("\n  ⚠️   Nothing to edit.")
                    self.__pause()
                else:
                    self.__edit_education(edus)
            elif choice == "D":
                if not edus:
                    print("\n  ⚠️   Nothing to delete.")
                    self.__pause()
                else:
                    idx = input("  Enter education number to delete: ").strip()
                    if idx.isdigit() and 1 <= int(idx) <= len(edus):
                        self.__current_user.remove_education(int(idx) - 1)
                        self.__save_database()
                        print("\n  ✅  Education removed.")
                        self.__pause()
                    else:
                        print("\n  ⚠️   Invalid number.")
                        self.__pause()
            elif choice == "B":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __add_education(self):
        self.__header("ADD EDUCATION")
        school = self.__prompt("School name")
        degree = self.__prompt("Degree / Course")
        year_start = self.__prompt("Year started  (e.g. 2020)")

        ongoing = input("  Still studying here? (y/n): ").strip().lower() == "y"
        year_end = None
        if not ongoing:
            year_end = self.__prompt("Year ended  (e.g. 2024)")

        edu = Education(school_name=school, degree=degree,
                        year_started=year_start, year_ended=year_end)
        self.__current_user.add_education(edu)
        self.__save_database()
        print("\n  ✅  Education added!")
        self.__pause()

    def __edit_education(self, edus):
        idx = input("  Enter education number to edit: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(edus)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        edu = edus[int(idx) - 1]
        self.__header("EDIT EDUCATION")
        print("  Press Enter to keep the current value.\n")

        s = input(f"  School [{edu.school_name}]: ").strip()
        if s:
            edu.school_name = s

        d = input(f"  Degree [{edu.degree}]: ").strip()
        if d:
            edu.degree = d

        ys = input(f"  Year started [{edu.year_started}]: ").strip()
        if ys:
            edu.year_started = ys

        ye = input(f"  Year ended [{edu.year_ended or 'Present'}]: ").strip()
        if ye:
            edu.year_ended = ye

        self.__save_database()
        print("\n  ✅  Education updated!")
        self.__pause()

    # Change Password 

    def __change_password(self):
        self.__header("CHANGE PASSWORD")
        old = self.__prompt("Current password")
        if not self.__current_user.verify_password(old):
            print("\n  ❌  Incorrect current password.")
            self.__pause()
            return

        while True:
            new_pass = self.__prompt("New password (min. 8 characters)")
            if len(new_pass) < 8:
                print("  ⚠️   Must be at least 8 characters.")
                continue
            confirm = self.__prompt("Confirm new password")
            if new_pass != confirm:
                print("  ⚠️   Passwords do not match.")
                continue
            break

        self.__current_user.change_password(new_pass)
        self.__save_database()
        print("\n  ✅  Password changed successfully!")
        self.__pause()
