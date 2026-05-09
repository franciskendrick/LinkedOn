import json
import os
import re
import uuid

from models.user import User
from models.experience import Experience
from models.education import Education
from models.post import Post, TextPost, JobPost, AchievementPost
from models.connection import Connection

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.json")


class LinkedOnApp:
    """
    Main controller class for the LinkedOn terminal application.
    Manages the database, user sessions, and all terminal menus.
    """

    def __init__(self):
        self.__users = {}
        self.__posts = {}
        self.__connections = []
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
            self.__posts = {
                pid: Post.from_dict(p)
                for pid, p in data.get("posts", {}).items()
            }
            self.__connections = [
                Connection.from_dict(c) for c in data.get("connections", [])
            ]
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

    def __get_connection(self, uid1, uid2):
        for c in self.__connections:
            if (c.sender_id == uid1 and c.receiver_id == uid2) or \
               (c.sender_id == uid2 and c.receiver_id == uid1):
                return c
        return None

    def __pending_count(self):
        return sum(
            1 for c in self.__connections
            if c.receiver_id == self.__current_user.user_id
            and c.status == Connection.PENDING
        )

    def __connection_count(self):
        return sum(
            1 for c in self.__connections
            if c.involves(self.__current_user.user_id)
            and c.status == Connection.ACCEPTED
        )

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
            pending = self.__pending_count()
            display_name = self.__current_user.name or self.__current_user.email
            self.__header(f"Logged in as: {display_name}")

            pending_tag = f"  ⚠️  {pending} pending" if pending > 0 else ""
            print("  [1]  View My Profile")
            print("  [2]  Edit Profile")
            print("  [3]  My Posts")
            print(f"  [4]  Network{pending_tag}")
            print("  [5]  Feed")
            print("  [6]  Log Out")
            print()

            choice = input("  Choose an option: ").strip()

            if choice == "1":
                self.__view_my_profile()
            elif choice == "2":
                self.__edit_profile_menu()
            elif choice == "3":
                self.__my_posts_menu()
            elif choice == "4":
                self.__network_menu()
            elif choice == "5":
                self.__view_feed()
            elif choice == "6":
                self.__current_user = None
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # =========================================================================
    # PROFILE
    # =========================================================================

    def __view_my_profile(self):
        self.__header("MY PROFILE")
        self.__current_user.display()
        print()
        post_count = len(self.__current_user.post_ids)
        conn_count = self.__connection_count()
        print(f"  📝 Posts: {post_count}     🤝 Connections: {conn_count}")
        self.__pause()

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
        start = self.__prompt("Start date  (e.g. Jan 2022)")

        is_curr = input("  Is this your current job? (y/n): ").strip().lower() == "y"
        end = None
        if not is_curr:
            end = self.__prompt("End date  (e.g. Dec 2023)")

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

    # =========================================================================
    #  POSTS
    # =========================================================================

    def __my_posts_menu(self):
        while True:
            self.__header("MY POSTS")
            post_ids = self.__current_user.post_ids

            if post_ids:
                print(f"  You have {len(post_ids)} post(s):\n")
                for i, pid in enumerate(post_ids, 1):
                    post = self.__posts.get(pid)
                    if post:
                        print(f"  [{i}]  " + "─" * 40)
                        post.display()
                        print()
            else:
                print("  You haven't made any posts yet.\n")

            print("  [A]  Create Post")
            print("  [D]  Delete Post")
            print("  [B]  Back")
            print()
            choice = input("  Choose an option: ").strip().upper()

            if choice == "A":
                self.__create_post()
            elif choice == "D":
                if not post_ids:
                    print("\n  ⚠️   No posts to delete.")
                    self.__pause()
                else:
                    self.__delete_post(post_ids)
            elif choice == "B":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __create_post(self):
        self.__header("CREATE A POST")
        print("  What type of post would you like to create?\n")
        print("  [1]  Text Post       — share a general update")
        print("  [2]  Job Posting     — advertise an open position")
        print("  [3]  Achievement     — celebrate a milestone")
        print()

        choice = input("  Choose post type: ").strip()
        pid = str(uuid.uuid4())
        uid = self.__current_user.user_id
        uname = self.__current_user.name or self.__current_user.email

        if choice == "1":
            content = self.__prompt("What's on your mind?")
            post = TextPost(pid, uid, uname, content)

        elif choice == "2":
            job_title = self.__prompt("Job Title")
            company = self.__prompt("Company")
            job_type = self.__prompt("Job Type  (e.g. Full-time / Part-time / Remote)")
            content = self.__prompt("Job Description")
            post = JobPost(pid, uid, uname, content, job_title, company, job_type)

        elif choice == "3":
            achievement_title = self.__prompt("Achievement Title")
            content = self.__prompt("Tell us more about it")
            post = AchievementPost(pid, uid, uname, content, achievement_title)

        else:
            print("\n  ⚠️   Invalid post type.")
            self.__pause()
            return

        self.__posts[pid] = post
        self.__current_user.add_post_id(pid)
        self.__save_database()
        print("\n  ✅  Post published!")
        self.__pause()

    def __delete_post(self, post_ids):
        idx = input("  Enter post number to delete: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(post_ids)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        pid = post_ids[int(idx) - 1]
        self.__current_user.remove_post_id(pid)
        if pid in self.__posts:
            del self.__posts[pid]
        self.__save_database()
        print("\n  ✅  Post deleted.")
        self.__pause()

    # =========================================================================
    #  NETWORK
    # =========================================================================

    def __network_menu(self):
        while True:
            pending = self.__pending_count()
            self.__header("NETWORK")
            print("  [1]  Search for a User")
            print("  [2]  My Connections")
            print(f"  [3]  Connection Requests  ({pending} pending)")
            print("  [4]  Back")
            print()
            choice = input("  Choose an option: ").strip()

            if choice == "1":
                self.__search_users()
            elif choice == "2":
                self.__view_connections()
            elif choice == "3":
                self.__manage_requests()
            elif choice == "4":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __search_users(self):
        self.__header("SEARCH USERS")
        query = self.__prompt("Search by name or school").lower()

        results = [
            u for u in self.__users.values()
            if u.user_id != self.__current_user.user_id
            and (
                query in (u.name or "").lower()
                or any(query in (e.school_name or "").lower() for e in u.educations)
            )
        ]

        if not results:
            print("\n  No users found matching that query.")
            self.__pause()
            return

        print(f"\n  Found {len(results)} user(s):\n")
        for i, u in enumerate(results, 1):
            conn = self.__get_connection(self.__current_user.user_id, u.user_id)
            tag = f"  [{conn.status}]" if conn else ""
            bio_snippet = f"  — {u.bio}" if u.bio else ""
            print(f"  [{i}]  {u.name or u.email}{bio_snippet}{tag}")

        print()
        idx = input("  Enter number to view profile (0 to cancel): ").strip()
        if idx == "0":
            return
        if idx.isdigit() and 1 <= int(idx) <= len(results):
            self.__view_other_profile(results[int(idx) - 1])
        else:
            print("\n  ⚠️   Invalid number.")
            self.__pause()

    def __view_other_profile(self, user):
        self.__header(f"PROFILE: {user.name or user.email}")
        user.display()

        # Show up to 3 recent posts
        if user.post_ids:
            recent = user.post_ids[-3:]
            print(f"\n  Recent Posts ({len(user.post_ids)} total):\n")
            for pid in recent:
                post = self.__posts.get(pid)
                if post:
                    print("  " + "─" * 46)
                    post.display()
            print("  " + "─" * 46)

        # Connection action
        my_id = self.__current_user.user_id
        conn = self.__get_connection(my_id, user.user_id)
        print()

        if conn is None:
            send = input("  Send connection request? (y/n): ").strip().lower()
            if send == "y":
                self.__connections.append(Connection(my_id, user.user_id))
                self.__save_database()
                print("  ✅  Connection request sent!")

        elif conn.status == Connection.PENDING:
            # Maybe it's ours, maybe it's theirs
            if conn.sender_id == my_id:
                print("  ⏳  Your connection request is still pending.")
            else:
                print("  📨  This user has sent you a connection request.")
                print("  Go to Network > Connection Requests to respond.")

        elif conn.status == Connection.ACCEPTED:
            print("  🤝  You are already connected.")
            remove = input("  Remove this connection? (y/n): ").strip().lower()
            if remove == "y":
                self.__connections.remove(conn)
                self.__save_database()
                print("  ✅  Connection removed.")

        elif conn.status == Connection.DECLINED:
            print("  ❌  This connection request was previously declined.")

        self.__pause()

    def __view_connections(self):
        self.__header("MY CONNECTIONS")

        connected_users = []
        for c in self.__connections:
            if c.involves(self.__current_user.user_id) and c.status == Connection.ACCEPTED:
                other_id = c.get_other(self.__current_user.user_id)
                other = self.__users.get(other_id)
                if other:
                    connected_users.append(other)

        if not connected_users:
            print("  You have no connections yet.")
            print("  Use Search to find and connect with other users.")
            self.__pause()
            return

        print(f"  You have {len(connected_users)} connection(s):\n")
        for i, u in enumerate(connected_users, 1):
            bio = u.bio if u.bio else "No headline"
            print(f"  [{i}]  {u.name or u.email}  —  {bio}")

        print()
        idx = input("  Enter number to view profile (0 to go back): ").strip()
        if idx == "0":
            return
        if idx.isdigit() and 1 <= int(idx) <= len(connected_users):
            self.__view_other_profile(connected_users[int(idx) - 1])
        else:
            print("\n  ⚠️   Invalid number.")
            self.__pause()

    def __manage_requests(self):
        self.__header("CONNECTION REQUESTS")

        pending = [
            c for c in self.__connections
            if c.receiver_id == self.__current_user.user_id
            and c.status == Connection.PENDING
        ]

        if not pending:
            print("  No pending connection requests.")
            self.__pause()
            return

        print(f"  {len(pending)} pending request(s):\n")
        senders = []
        for i, c in enumerate(pending, 1):
            sender = self.__users.get(c.sender_id)
            if sender:
                senders.append((c, sender))
                bio = sender.bio if sender.bio else "No headline"
                print(f"  [{i}]  {sender.name or sender.email}  —  {bio}")

        print()
        idx = input("  Enter number to respond (0 to go back): ").strip()
        if idx == "0":
            return
        if not (idx.isdigit() and 1 <= int(idx) <= len(senders)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        conn, sender = senders[int(idx) - 1]
        print()
        print(f"  Request from: {sender.name or sender.email}")
        print()
        print("  [1]  Accept")
        print("  [2]  Decline")
        print("  [3]  Decide later")
        print()
        action = input("  Choose: ").strip()

        if action == "1":
            conn.accept()
            self.__save_database()
            print(f"\n  ✅  You are now connected with {sender.name or sender.email}!")
        elif action == "2":
            conn.decline()
            self.__save_database()
            print("\n  Request declined.")

        self.__pause()

    # =========================================================================
    #  FEED
    # =========================================================================

    def __view_feed(self):
        self.__header("FEED")

        # Gather all connected user IDs, plus the current user
        connected_ids = [self.__current_user.user_id]
        for c in self.__connections:
            if c.involves(self.__current_user.user_id) and c.status == Connection.ACCEPTED:
                connected_ids.append(c.get_other(self.__current_user.user_id))

        # Collect all posts from those users
        all_posts = []
        for uid in connected_ids:
            user = self.__users.get(uid)
            if user:
                for pid in user.post_ids:
                    post = self.__posts.get(pid)
                    if post:
                        all_posts.append(post)

        if not all_posts:
            print("  Your feed is empty.")
            print("  Connect with others to see their posts here!")
            self.__pause()
            return

        # Sort newest first
        all_posts.sort(key=lambda p: p.timestamp, reverse=True)

        print(f"  {len(all_posts)} post(s) in your feed:\n")
        for post in all_posts:
            print("  " + "─" * 46)
            post.display()
            print()
        print("  " + "─" * 46)

        self.__pause()