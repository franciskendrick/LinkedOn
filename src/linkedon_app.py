import json
import os

from user import User
from experience import Experience
from education import Education
from post import Post, TextPost, JobPost, AchievementPost
from connection import Connection

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
        # Open and load the raw JSON data
        with open(DB_PATH, "r") as f:
            data = json.load(f)
            
        # Extract raw data components using .get()
        raw_users = data.get("users", {})
        raw_posts = data.get("posts", {})
        raw_connections = data.get("connections", [])

        # Process Data
        self.__users = {}
        for uid, u in raw_users.items():
            self.__users[uid] = User.from_dict(u)

        self.__posts = {}
        for pid, p in raw_posts.items():
            self.__posts[pid] = Post.from_dict(p)

        self.__connections = []
        for c in raw_connections:
            self.__connections.append(Connection.from_dict(c))

    def __save_database(self):
        # Initialize empty containers
        users_dict = {}
        posts_dict = {}
        connections_list = []

        # Populate dictionaries
        for uid, u in self.__users.items():  # populate users
            users_dict[uid] = u.to_dict()
        for pid, p in self.__posts.items():  # populate posts
            posts_dict[pid] = p.to_dict()
        for c in self.__connections:  # populate connections
            connections_list.append(c.to_dict())

        # Assemble final data structure
        data = {
            "users": users_dict,
            "posts": posts_dict,
            "connections": connections_list,
        }

        # Dump Data Dictionary to JSON file 
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)

    # =========================================================================
    #  HELPERS
    # =========================================================================

    def __clear(self):
        os.system("cls" if os.name == "nt" else "clear")  # clear the screen

    def __pause(self):
        input("\n  Press Enter to continue...")

    def __header(self, subtitle=""):
        self.__clear()

        # ASCII art header (https://patorjk.com/software/taag/#p=display&f=ANSI+Shadow&t=LINKEDON&x=none&v=1&h=1&w=80&we=false)
        print()
        print("  ██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗  ██████╗ ███╗   ██╗")
        print("  ██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██╔═══██╗████╗  ██║")
        print("  ██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██║  ██║██║   ██║██╔██╗ ██║")
        print("  ██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██║  ██║██║   ██║██║╚██╗██║")
        print("  ███████╗██║██║ ╚████║██║  ██╗███████╗██████╔╝╚██████╔╝██║ ╚████║")
        print("  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝")

        # Subtitle and separator
        if subtitle:
            print()
            print(f"  {'─'*48}")
            print(f"  {subtitle}")
        print(f"  {'─'*48}")
        print()

    def __prompt(self, label, allow_empty=False):
        # Get non-empty input from the user.
        while True:
            val = input(f"  {label}: ").strip()
            if val or allow_empty:
                return val
            print("  ⚠️   This field cannot be empty. Please try again.")

    def __email_taken(self, email):
        return any(u.email == email for u in self.__users.values())

    def __is_valid_email(self, email):
        """
        Validates email domain using native string methods without regular expressions.
        """
        email_lower = email.lower()
        allowed_domains = ("@gmail.com", "@yahoo.com", "@outlook.com", "@edu.ph")

        # 1. Enforce allowed domains at the end
        if not email_lower.endswith(allowed_domains):
            print("  ⚠️   Registration restricted to approved domains (Gmail, Yahoo, Outlook, or .edu.ph).")
            return False

        # 2. Basic structural sanity check (No spaces allowed)
        if " " in email_lower:
            print("  ⚠️   Email cannot contain spaces.")
            return False

        # 3. Ensure there is substantial content before the domain
        # Find which domain matched to calculate prefix length
        for domain in allowed_domains:
            if email_lower.endswith(domain):
                prefix = email_lower[:-len(domain)]
                if not prefix:
                    print("  ⚠️   Email username cannot be empty.")
                    return False
                break

        return True

    def __find_by_email(self, email):
        for u in self.__users.values():
            if u.email == email:
                return u
        return None

    def __get_connection(self, uid1, uid2):
        for c in self.__connections:
            if (c.sender_id == uid1 and c.receiver_id == uid2) or (c.sender_id == uid2 and c.receiver_id == uid1):
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

        # Display all options
        print("  Your Professional Network Starts Here.")
        print()
        print("  [1]  Register")
        print("  [2]  Log In")
        print("  [3]  Exit")
        print()

        # Ask user what they want to do
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
        # Header
        self.__header("CREATE AN ACCOUNT")

        # Email Validation Loop
        while True:
            email = self.__prompt("Email")
            
            # Syntactic and domain validation
            if not self.__is_valid_email(email):
                continue
                
            # Uniqueness validation
            if self.__email_taken(email):
                print("  ⚠️   That email is already registered.")
                continue
            break

        # Password Validation Loop
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

        # Use the email as the user ID since it is already unique
        new_user = User(user_id=email, email=email, password=password)
        self.__users[email] = new_user
        self.__save_database()

        # Confirmation message
        print()
        print("  ✅   Account created successfully!")
        print("  Tip: Log in and complete your profile to get started.")
        self.__pause()

    def __login(self):
        # Header
        self.__header("LOG IN")
        email = self.__prompt("Email")
        password = self.__prompt("Password")

        # Find email
        user = self.__find_by_email(email)
        if user is None or not user.verify_password(password):
            print()
            print("  ❌  Incorrect email or password.")
            self.__pause()
            return

        # Confirmation message
        self.__current_user = user
        display_name = user.name if user.name else user.email
        print()
        print(f"  ✅  Welcome back, {display_name}!")
        self.__pause()

        # Back to dashboard
        self.__dashboard()

    # =========================================================================
    #  DASHBOARD
    # =========================================================================

    def __dashboard(self):
        while True:
            # Header
            pending = self.__pending_count()
            display_name = self.__current_user.name or self.__current_user.email
            self.__header(f"Logged in as: {display_name}")

            # Display all options
            pending_tag = f"  ⚠️  {pending} pending" if pending > 0 else ""
            print("  [1]  View My Profile")
            print("  [2]  Edit Profile")
            print("  [3]  My Posts")
            print(f"  [4]  Network{pending_tag}")
            print("  [5]  Feed")
            print("  [6]  Log Out")
            print()

            # Ask user to what they want to do
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # =========================================================================
    # PROFILE
    # =========================================================================

    def __view_my_profile(self):
        # Header
        self.__header("MY PROFILE")
        self.__current_user.display()
        print()

        # Display post and connections count
        post_count = len(self.__current_user.post_ids)
        conn_count = self.__connection_count()
        print(f"  📝 Posts: {post_count}     🤝 Connections: {conn_count}")
        self.__pause()

    def __edit_profile_menu(self):
        while True:
            # Header
            self.__header("EDIT PROFILE")

            # Display all options
            print("  [1]  Edit Basic Info  (name, age, location, bio)")
            print("  [2]  Manage Skills")
            print("  [3]  Manage Work Experience")
            print("  [4]  Manage Education")
            print("  [5]  Change Password")
            print("  [6]  Back")
            print()

            # Ask user what they want to add on their profile
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # Edit Basic Info
    def __edit_basic_info(self):
        u = self.__current_user

        # Header
        self.__header("EDIT BASIC INFO")
        print("  Press Enter to keep the current value.\n")

        # Edit name
        name = input(f"  Name [{u.name}]: ").strip()
        if name:
            u.name = name

        while True:  # error validation
            age_in = input(f"  Age [{u.age}]: ").strip()
            if not age_in:
                break
            if age_in.isdigit() and 1 <= int(age_in) <= 120:
                u.age = int(age_in)
                break
            print("  ⚠️   Please enter a valid age (1–120).")

        # Edit location
        location = input(f"  Location [{u.location}]: ").strip()
        if location:
            u.location = location

        # Edit bio
        bio = input(f"  Headline/Bio [{u.bio}]: ").strip()
        if bio:
            u.bio = bio

        # Save to Database and confirm changes
        self.__save_database()
        print()
        print("  ✅  Profile updated!")
        self.__pause()

    # Manage Skills
    def __manage_skills(self):
        while True:
            # Header
            self.__header("MANAGE SKILLS")

            # Display all the user's skills
            skills = self.__current_user.skills
            if skills:
                print("  Your Skills:\n")
                for i, s in enumerate(skills, 1):
                    print(f"  [{i}]  {s}")
            else:
                print("  You haven't added any skills yet.")

            # Display all options
            print()
            print("  [A]  Add Skill")
            print("  [D]  Delete Skill")
            print("  [B]  Back")
            print()

            # Ask user what they want to do with their skills
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # Manage Work Experience
    def __manage_experience(self):
        while True:
            # Header
            self.__header("WORK EXPERIENCE")

            # Display all the user's work experiences
            exps = self.__current_user.experiences
            if exps:
                print("  Your Work Experience:\n")
                for i, e in enumerate(exps, 1):
                    print(f"  [{i}]")
                    e.display()
                    print()
            else:
                print("  No work experience added yet.\n")

            # Display all options
            print("  [A]  Add Experience")
            print("  [E]  Edit Experience")
            print("  [D]  Delete Experience")
            print("  [B]  Back")
            print()

            # Ask user what they want to do with their work experience
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __add_experience(self):
        # Header
        self.__header("ADD WORK EXPERIENCE")

        # Collect all details for the new experience entry
        company = self.__prompt("Company name")
        role = self.__prompt("Job title / Role")
        start = self.__prompt("Start date  (e.g. Jan 2022)")

        # Determine if this is the user's current job to handle end date accordingly
        is_curr = input("  Is this your current job? (y/n): ").strip().lower() == "y"
        end = None
        if not is_curr:
            end = self.__prompt("End date  (e.g. Dec 2023)")

        # Create Experience object and attach it to the current user
        exp = Experience(company=company, role=role, start_date=start, end_date=end, is_current=is_curr)
        self.__current_user.add_experience(exp)
        self.__save_database()
        print("\n  ✅  Work experience added!")
        self.__pause()

    def __edit_experience(self, exps):
        # Ask which experience entry to edit
        idx = input("  Enter experience number to edit: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(exps)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        # Header
        exp = exps[int(idx) - 1]
        self.__header("EDIT WORK EXPERIENCE")
        print("  Press Enter to keep the current value.\n")

        # Edit company, role, and start date (only update if user provides a new value)
        c = input(f"  Company [{exp.company}]: ").strip()
        if c:
            exp.company = c

        r = input(f"  Role [{exp.role}]: ").strip()
        if r:
            exp.role = r

        s = input(f"  Start date [{exp.start_date}]: ").strip()
        if s:
            exp.start_date = s

        # Update current job status and end date based on user's answer
        curr = input(f"  Currently working here? (y/n) [{'y' if exp.is_current else 'n'}]: ").strip().lower()
        if curr == "y":
            exp.is_current = True
            exp.end_date = None  # clear end date since job is ongoing
        elif curr == "n":
            exp.is_current = False
            e = input(f"  End date [{exp.end_date}]: ").strip()
            if e:
                exp.end_date = e

        # Save changes to database and confirm
        self.__save_database()
        print("\n  ✅  Experience updated!")
        self.__pause()

    # Manage Education
    def __manage_education(self):
        while True:
            # Header
            self.__header("EDUCATION")

            # Display all the user's education entries
            edus = self.__current_user.educations
            if edus:
                print("  Your Education:\n")
                for i, e in enumerate(edus, 1):
                    print(f"  [{i}]")
                    e.display()
                    print()
            else:
                print("  No education added yet.\n")

            # Display all options
            print("  [A]  Add Education")
            print("  [E]  Edit Education")
            print("  [D]  Delete Education")
            print("  [B]  Back")
            print()

            # Ask user what they want to do with their education
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __add_education(self):
        # Header
        self.__header("ADD EDUCATION")

        # Collect all details for the new education entry
        school = self.__prompt("School name")
        degree = self.__prompt("Degree / Course")
        year_start = self.__prompt("Year started  (e.g. 2020)")

        # Determine if the user is still studying to handle year ended accordingly
        ongoing = input("  Still studying here? (y/n): ").strip().lower() == "y"
        year_end = None
        if not ongoing:
            year_end = self.__prompt("Year ended  (e.g. 2024)")

        # Create Education object and attach it to the current user
        edu = Education(school_name=school, degree=degree,
                        year_started=year_start, year_ended=year_end)
        self.__current_user.add_education(edu)
        self.__save_database()
        print("\n  ✅  Education added!")
        self.__pause()

    def __edit_education(self, edus):
        # Ask which education entry to edit
        idx = input("  Enter education number to edit: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(edus)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        # Header
        edu = edus[int(idx) - 1]
        self.__header("EDIT EDUCATION")
        print("  Press Enter to keep the current value.\n")

        # Edit all fields (only update if the user provides a new value)
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

        # Save changes to database and confirm
        self.__save_database()
        print("\n  ✅  Education updated!")
        self.__pause()

    # Change Password
    def __change_password(self):
        # Header
        self.__header("CHANGE PASSWORD")

        # Verify the user knows their current password before allowing a change
        old = self.__prompt("Current password")
        if not self.__current_user.verify_password(old):
            print("\n  ❌  Incorrect current password.")
            self.__pause()
            return

        # Collect and validate the new password
        while True:
            new_pass = self.__prompt("New password (min. 8 characters)")
            if len(new_pass) < 8:
                print("  ⚠️   Must be at least 8 characters.")
                continue
            confirm = self.__prompt("Confirm new password")
            if new_pass != confirm:  # error validation
                print("  ⚠️   Passwords do not match.")
                continue
            break

        # Save the new password and confirm
        self.__current_user.change_password(new_pass)
        self.__save_database()
        print("\n  ✅  Password changed successfully!")
        self.__pause()

    # =========================================================================
    #  POSTS
    # =========================================================================

    def __my_posts_menu(self):
        while True:
            # Header
            self.__header("MY POSTS")
            post_ids = self.__current_user.post_ids

            # Display all the user's posts if any exist
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

            # Display all options
            print("  [A]  Create Post")
            print("  [D]  Delete Post")
            print("  [B]  Back")
            print()

            # Ask user what they want to do with their posts
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
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __create_post(self):
        # Header
        self.__header("CREATE A POST")
        print("  What type of post would you like to create?\n")

        # Display all post types
        print("  [1]  Text Post       - share a general update")
        print("  [2]  Job Posting     - advertise an open position")
        print("  [3]  Achievement     - celebrate a milestone")
        print()

        # Generate a simple numeric post ID based on the current total post count
        choice = input("  Choose post type: ").strip()
        pid = str(len(self.__posts) + 1)
        uid = self.__current_user.user_id
        uname = self.__current_user.name or self.__current_user.email

        # Collect post-specific fields based on the chosen post type
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

        else:  # error validation
            print("\n  ⚠️   Invalid post type.")
            self.__pause()
            return

        # Register the post in the global posts dictionary and link it to the user
        self.__posts[pid] = post
        self.__current_user.add_post_id(pid)
        self.__save_database()
        print("\n  ✅  Post published!")
        self.__pause()

    def __delete_post(self, post_ids):
        # Ask which post to delete
        idx = input("  Enter post number to delete: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(post_ids)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        # Remove the post from the user's post list and from the global posts dictionary
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
            # Header (show live pending count on the requests option)
            pending = self.__pending_count()
            self.__header("NETWORK")

            # Display all options
            print("  [1]  Search for a User")
            print("  [2]  My Connections")
            print(f"  [3]  Connection Requests  ({pending} pending)")
            print("  [4]  Back")
            print()

            # Ask user what they want to do
            choice = input("  Choose an option: ").strip()
            if choice == "1":
                self.__search_users()
            elif choice == "2":
                self.__view_connections()
            elif choice == "3":
                self.__manage_requests()
            elif choice == "4":
                return
            else:  # error validation
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __search_users(self):
        # Header
        self.__header("SEARCH USERS")
        query = self.__prompt("Search by name or school").lower()

        # Filter all users by name or school name, excluding the current user
        results = []
        for u in self.__users.values():
            # Skip the current user
            if u.user_id == self.__current_user.user_id:
                continue

            # Check if the query matches the user's name
            name_match = query in u.name.lower()

            # Check if the query matches any of the user's school names
            school_match = False
            for e in u.educations:
                if query in e.school_name.lower():
                    school_match = True
                    break

            # Add the user to results if either the name or school matched
            if name_match or school_match:
                results.append(u)

        if not results:
            print("\n  No users found matching that query.")
            self.__pause()
            return

        # Display results, annotating each with the current connection status if one exists
        print(f"\n  Found {len(results)} user(s):\n")
        i = 1
        for u in results:
            conn = self.__get_connection(self.__current_user.user_id, u.user_id)

            # Build the connection status tag if a connection exists
            if conn:
                tag = f"  [{conn.status}]"
            else:
                tag = ""

            # Build the bio snippet if the user has a bio
            if u.bio:
                bio_snippet = f"  - {u.bio}"
            else:
                bio_snippet = ""

            # Display the user's name if they have one, otherwise show their email
            if u.name:
                display_name = u.name
            else:
                display_name = u.email

            print(f"  [{i}]  {display_name}{bio_snippet}{tag}")
            i += 1

        # Let the user select a result to view the full profile
        print()
        idx = input("  Enter number to view profile (0 to cancel): ").strip()
        if idx == "0":
            return
        if idx.isdigit() and 1 <= int(idx) <= len(results):
            self.__view_other_profile(results[int(idx) - 1])
        else:  # error validation
            print("\n  ⚠️   Invalid number.")
            self.__pause()

    def __view_other_profile(self, user):
        # Header
        self.__header(f"PROFILE: {user.name or user.email}")
        user.display()

        # Show up to 3 of the user's most recent posts
        if user.post_ids:
            recent = user.post_ids[-3:]
            print(f"\n  Recent Posts ({len(user.post_ids)} total):\n")
            for pid in recent:
                post = self.__posts.get(pid)
                if post:
                    print("  " + "─" * 46)
                    post.display()
            print("  " + "─" * 46)

        # Check the connection status between the viewer and this profile's owner
        my_id = self.__current_user.user_id
        conn = self.__get_connection(my_id, user.user_id)
        print()

        if conn is None:
            # No connection exists yet (offer to send a request)
            send = input("  Send connection request? (y/n): ").strip().lower()
            if send == "y":
                self.__connections.append(Connection(my_id, user.user_id))
                self.__save_database()
                print("  ✅  Connection request sent!")

        elif conn.status == Connection.PENDING:
            # A request is in progress (show who is waiting on whom)
            if conn.sender_id == my_id:
                print("  ⏳  Your connection request is still pending.")
            else:
                print("  📨  This user has sent you a connection request.")
                print("  Go to Network > Connection Requests to respond.")

        elif conn.status == Connection.ACCEPTED:
            # Already connected (offer the option to remove the connection)
            print("  🤝  You are already connected.")
            remove = input("  Remove this connection? (y/n): ").strip().lower()
            if remove == "y":
                self.__connections.remove(conn)
                self.__save_database()
                print("  ✅  Connection removed.")

        elif conn.status == Connection.DECLINED:
            # A previous request was declined (inform the user)
            print("  ❌  This connection request was previously declined.")

        self.__pause()

    def __view_connections(self):
        # Header
        self.__header("MY CONNECTIONS")

        # Gather all users who share an accepted connection with the current user
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

        # List all connected users with their headline
        print(f"  You have {len(connected_users)} connection(s):\n")
        for i, u in enumerate(connected_users, 1):
            bio = u.bio if u.bio else "No headline"
            print(f"  [{i}]  {u.name or u.email}  -  {bio}")

        # Let the user select a connection to view their full profile
        print()
        idx = input("  Enter number to view profile (0 to go back): ").strip()
        if idx == "0":
            return
        if idx.isdigit() and 1 <= int(idx) <= len(connected_users):
            self.__view_other_profile(connected_users[int(idx) - 1])
        else:  # error validation
            print("\n  ⚠️   Invalid number.")
            self.__pause()

    def __manage_requests(self):
        # Header
        self.__header("CONNECTION REQUESTS")

        # Collect all pending requests addressed to the current user
        pending = [
            c for c in self.__connections
            if c.receiver_id == self.__current_user.user_id
            and c.status == Connection.PENDING
        ]

        if not pending:
            print("  No pending connection requests.")
            self.__pause()
            return

        # List all senders with their headline
        print(f"  {len(pending)} pending request(s):\n")
        senders = []
        for i, c in enumerate(pending, 1):
            sender = self.__users.get(c.sender_id)
            if sender:
                senders.append((c, sender))
                bio = sender.bio if sender.bio else "No headline"
                print(f"  [{i}]  {sender.name or sender.email}  -  {bio}")

        # Ask the user to select a request to respond to
        print()
        idx = input("  Enter number to respond (0 to go back): ").strip()
        if idx == "0":
            return
        if not (idx.isdigit() and 1 <= int(idx) <= len(senders)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        # Display the selected sender and the response options
        conn, sender = senders[int(idx) - 1]
        print()
        print(f"  Request from: {sender.name or sender.email}")
        print()
        print("  [1]  Accept")
        print("  [2]  Decline")
        print("  [3]  Decide later")
        print()

        # Process the user's response and update the connection status
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
        # Header
        self.__header("FEED")

        # Gather the current user's ID plus all accepted connections' IDs
        connected_ids = [self.__current_user.user_id]
        for c in self.__connections:
            if c.involves(self.__current_user.user_id) and c.status == Connection.ACCEPTED:
                connected_ids.append(c.get_other(self.__current_user.user_id))

        # Collect every post from all gathered user IDs
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

        # Sort all posts newest first, then display them
        all_posts.sort(key=post.timestamp, reverse=True)

        print(f"  {len(all_posts)} post(s) in your feed:\n")
        for post in all_posts:
            print("  " + "─" * 46)
            post.display()
            print()
        print("  " + "─" * 46)

        self.__pause()
