import json  # Used for reading and writing JSON database files
import os  # Provides access to operating system functions
import re  # Used for validating email patterns using regular expressions
import uuid  # Generates unique IDs for users and posts

#========================================DIVIDER========================================

from models.user import User  # Imports User class
from models.experience import Experience  # Imports Experience class
from models.education import Education  # Imports Education class
from models.post import Post, TextPost, JobPost, AchievementPost
# Imports Post classes
# Pillar Used: Inheritance and Polymorphism

# from models.connection import Connection

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database.json"
)
# Creates the full file path for the database file

class LinkedOnApp:
    """
    Main controller class for the LinkedOn terminal application.
    Manages the database, user sessions, and all terminal menus. Pillar Used: Abstraction
    """

    def __init__(self):
        self.__users = {}         # { user_id: User }
        # Dictionary storing User objects
        # Pillar Used: Encapsulation
        self.__posts = {}         # { post_id: Post }
        # Dictionary storing Post objects
        self.__connections = []   # [ Connection ]
        # Stores user connections
        self.__current_user = None
        # Stores currently logged-in user
        self.__load_database()
        # Automatically loads saved database when app starts

    # =========================================================================
    #  DATABASE
    # =========================================================================

    def __load_database(self):
        if not os.path.exists(DB_PATH):
            return
        try:
            with open(DB_PATH, "r") as f:
                # Opens database file in read mode
                data = json.load(f)
                # Converts JSON data into Python dictionary
            
            self.__users = {
                uid: User.from_dict(u)
                for uid, u in data.get("users", {}).items()
            }
            # Reconstructs User objects from saved dictionaries
            # Pillar Used: Polymorphism
            
            self.__posts = {
                pid: Post.from_dict(p)
                for pid, p in data.get("posts", {}).items()
            }
            # Reconstructs Post objects from dictionaries
            # Pillar Used: Polymorphism
        
        except (json.JSONDecodeError, KeyError):
            # Handles corrupted database errors
            print("  ⚠️  Database file is corrupted. Starting fresh.")

    def __save_database(self):
        # Saves all users, posts, and connections into JSON database.
        # Pillar Used: Abstraction
        data = {
            "users": {uid: u.to_dict() for uid, u in self.__users.items()},
            # Converts all User objects into dictionaries
            # Pillar Used: Polymorphism
            "posts": {pid: p.to_dict() for pid, p in self.__posts.items()},
            # Converts all Post objects into dictionaries

            "connections": [c.to_dict() for c in self.__connections],
        }
        with open(DB_PATH, "w") as f:
            # Opens database file in write mode
            json.dump(data, f, indent=4)
            # Saves formatted JSON data into file

    # =========================================================================
    #  HELPERS
    # =========================================================================

    def __clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def __pause(self):
        input("\n  Press Enter to continue...")

    def __header(self, subtitle=""):
        
        self.__clear()
        # Clears terminal before printing menu
        
        print()
        print("  ██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗  ██████╗ ███╗   ██╗")
        print("  ██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██╔═══██╗████╗  ██║")
        print("  ██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██║  ██║██║   ██║██╔██╗ ██║")
        print("  ██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██║  ██║██║   ██║██║╚██╗██║")
        print("  ███████╗██║██║ ╚████║██║  ██╗███████╗██████╔╝╚██████╔╝██║ ╚████║")
        print("  ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝")
        if subtitle:
            # Displays subtitle only if one exists
            print()
            print(f"  {'─'*48}")
            print(f"  {subtitle}")
        print(f"  {'─'*48}")
        print()

    def __prompt(self, label, allow_empty=False):
        """Get non-empty input from the user."""
        # Reusable input method with validation.
        # Pillar Used: Abstraction
        
        while True:
            val = input(f"  {label}: ").strip()
            # Removes extra spaces from input
            
            if val or allow_empty:
                # Returns input if not empty
                return val
            print("  ⚠️   This field cannot be empty. Please try again.")

    @staticmethod
    def __valid_email(email):

        # Validates email format using regex.
        # Static method because it does not use object attributes.
        # Pillar Used: Abstraction
        
        return re.match(r'^[\w.%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$', email) is not None

    def __email_taken(self, email):
        # Checks if email already exists
        return any(u.email == email for u in self.__users.values())

    def __find_by_email(self, email):
        # Searches for a user by email
        
        for u in self.__users.values():
            if u.email == email:
                return u
        return None

    # =========================================================================
    #  ENTRY POINT
    # =========================================================================

    def run(self):
        # Main application loop
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
        # Handles user registration
        # Pillar Used: Abstraction
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
        # Generates unique user ID
        
        new_user = User(
            user_id=user_id,
            email=email,
            password_hash=User.hash_password(password),
        )
        # Creates User object
        # Pillar Used: Encapsulation
        
        self.__users[user_id] = new_user
        # Stores user in dictionary
        
        self.__save_database()

        print()
        print("  ✅  Account created successfully!")
        print("  Tip: Log in and complete your profile to get started.")
        self.__pause()

    def __login(self):

        # Handles user login authentication
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
        # Stores logged-in user session
        
        display_name = user.name if user.name else user.email
        print()
        print(f"  ✅  Welcome back, {display_name}!")
        self.__pause()
        self.__dashboard()
        # Redirects to dashboard after successful login

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
                self.__my_posts_menu()
            elif choice == "4":
                pass  # !!!
            elif choice == "5":
                pass  # !!!
            elif choice == "6":
                self.__current_user = None
                # Removes active session
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    # =========================================================================
    #  VIEW MY PROFILE
    # =========================================================================

    def __view_my_profile(self):
    # Displays the currently logged-in user's profile.
    # Pillar Used: Abstraction
        
        self.__header("MY PROFILE")
    # Displays profile page header

        
        self.__current_user.display()
    # Calls the User object's display() method
    # Pillar Used: Polymorphism
    # Different objects can have different display behaviors
        print()
        post_count = len(self.__current_user.post_ids)
        # Counts total posts made by the user
        
        conn_count = 0  # !!!
        # Placeholder value for future connection feature
        
        print(f"  📝 Posts: {post_count}     🤝 Connections: {conn_count}")
        # Displays profile statistics
        self.__pause()
        # Pauses before returning

    # =========================================================================
    #  MY POSTS
    # =========================================================================

    def __my_posts_menu(self):
        # Displays and manages the user's posts.
        # Pillar Used: Abstraction
        while True:
            self.__header("MY POSTS")
            # Displays page title

            post_ids = self.__current_user.post_ids
            # Gets all post IDs owned by current user
            
            my_posts = [self.__posts[pid] for pid in post_ids if pid in self.__posts]
            # Converts post IDs into actual Post objects

            if my_posts:
                print(f"  You have {len(my_posts)} post(s):\n")
                print(f"  {'─'*48}")
                for i, post in enumerate(my_posts, 1):
                    # Loops through all posts with numbering
                    
                    print(f"  [{i}]  ", end="")
                    if post.post_type == "text":
                        print(f"📝  TEXT  —  {post.content[:45]}{'...' if len(post.content) > 45 else ''}")
                    elif post.post_type == "job":
                        print(f"👔  JOB   —  {post.job_title} @ {post.company}")
                    elif post.post_type == "achievement":
                        print(f"🏆  ACHIEVEMENT  —  {post.achievement_title}")
                        # Different behavior depending on post type
                        # Pillar Used: Polymorphism
                    
                    print(f"      ⏳  {post.timestamp}")
                print(f"  {'─'*48}")
            else:
                print("  You haven't posted anything yet.\n")

            print()
            print("  [C]  Create Post")
            print("  [V]  View a Post")
            print("  [D]  Delete a Post")
            print("  [B]  Back")
            print()
            choice = input("  Choose an option: ").strip().upper()

            if choice == "C":
                self.__create_post()
            elif choice == "V":
                if not my_posts:
                    print("\n  ⚠️   No posts to view.")
                    self.__pause()
                else:
                    self.__view_post_detail(my_posts)
            elif choice == "D":
                if not my_posts:
                    print("\n  ⚠️   No posts to delete.")
                    self.__pause()
                else:
                    self.__delete_post(my_posts)
            elif choice == "B":
                return
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()

    def __create_post(self):
    # Creates different types of posts.
    # Pillar Used: Abstraction
        
        self.__header("CREATE A POST")
        print("  What type of post would you like to create?\n")
        print("  [M]    My Day — Share your thoughts or updates")
        print("  [J]    Job Post — Seek a Job you jobless")
        print("  [A]    Achievement Post — Achievements, certifications, awards, and more")
        print("  [B]    Back")
        print()
        choice = input("  Choose an option: ").strip().upper()

        post_id = str(uuid.uuid4())
        # Generates unique post ID
        
        author_id = self.__current_user.user_id
        # Gets current user's ID
        
        if choice == "M":
            self.__header("NEW TEXT  POST")
            content = self.__prompt("What's on your mind?")
            post = TextPost(post_id=post_id, author_id=author_id, content=content)
            # Creates TextPost object
            # Pillar Used: Inheritance

        elif choice == "J":
            self.__header("NEW JOB POST")
            job_title = self.__prompt("Job title")
            company = self.__prompt("Company")
            content = self.__prompt("Details / Description")
            post = JobPost(
                post_id=post_id, author_id=author_id,
                content=content, job_title=job_title, company=company
            )
            # Creates JobPost object
            # Pillar Used: Inheritance

        elif choice == "A":
            self.__header("NEW ACHIEVEMENT POST")
            achievement_title = self.__prompt("Achievement title  (e.g. 'Passed AWS Certification')")
            content = self.__prompt("Tell us more about it")
            post = AchievementPost(
                post_id=post_id, author_id=author_id,
                content=content, achievement_title=achievement_title
            )
        # Creates AchievementPost object
        # Pillar Used: Inheritance

        elif choice == "B":
            return

        else:
            print("\n  ⚠️   Invalid option.")
            self.__pause()
            return

        # Save the post
        self.__posts[post_id] = post
        # Stores new post in posts dictionary
        
        self.__current_user.add_post_id(post_id)
        # Links post to current user
        self.__save_database()
        # Saves changes to database

        print()
        print("✓  Post published successfully!")
        self.__pause()

    def __view_post_detail(self, my_posts):
        idx = input("Enter post number to view: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(my_posts)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        post = my_posts[int(idx) - 1]
        # Retrieves selected post object
        
        self.__header("POST DETAIL")
        print(f"  {'─'*48}")
        post.display()
        # Calls display() method of post object
        # Pillar Used: Polymorphism
        
        print(f"  {'─'*48}")
        self.__pause()

    def __delete_post(self, my_posts):
        idx = input("Enter post number to delete: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(my_posts)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        post = my_posts[int(idx) - 1]
        confirm = input(f"\n  ⚠️   Delete this post? (y/n): ").strip().lower()
        if confirm != "y":
            print("\n  Cancelled.")
            self.__pause()
            return

        self.__current_user.remove_post_id(post.post_id)
        # Removes post ID from current user
        
        del self.__posts[post.post_id]
        # Deletes post object from posts dictionary

        self.__save_database()

        print("\n  ✅  Post deleted.")
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
        #  Allows the user to edit basic profile information
        
        self.__header("EDIT BASIC INFO")
        u = self.__current_user
        # Shortcut variable for current user object
        
        print("  Press Enter to keep the current value.\n")

        name = input(f"  Name [{u.name}]: ").strip()
        if name:
            u.name = name
        # Uses setter method
        # Pillar Used: Encapsulation
        
        while True:
            age_in = input(f"  Age [{u.age}]: ").strip()
            if not age_in:
                break
            if age_in.isdigit() and 1 <= int(age_in) <= 120:
                u.age = int(age_in)
        # Uses Setter method
                
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
            # Retrieves skills list

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
                # Calls User class method
                # Pillar Used: Abstraction
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
                # Returns to previous menu
            
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()
                # Handles invalid menu choices

    # Manage Work Experience

    def __manage_experience(self):
    # Manages the user's work experiences.
    # Pillar Used: Abstraction
        
        while True:
            self.__header("WORK EXPERIENCE")
            # Displays page header
            exps = self.__current_user.experiences
            # Retrieves list of work experiences
            if exps:
                print("  Your Work Experience:\n")
                for i, e in enumerate(exps, 1):
                    # Loops through experience objects
                    
                    print(f"  [{i}]")
                    e.display()
                    # Displays experience details
                    # Pillar Used: Polymorphism
                    
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
                        # Removes experience using User class method
                        # Pillar Used: Abstraction
                        
                        self.__save_database()
                        print("\n  ✅  Experience removed.")
                        self.__pause()
                    else:
                        print("\n  ⚠️   Invalid number.")
                        self.__pause()
            elif choice == "B":
                return
                # Returns to previous menu
            
            else:
                print("\n  ⚠️   Invalid option.")
                self.__pause()
                # Handles invalid menu choices

    def __add_experience(self):
        self.__header("ADD WORK EXPERIENCE")
        company = self.__prompt("Company name")
        # Gets company name input
        role = self.__prompt("Job title / Role")
        # Gets role input
        start = self.__prompt("Start date  (e.g. Jan 2025)")
        # Gets start date input
        is_curr = input("  Is this your current job? (y/n): ").strip().lower() == "y"
        # Converts answer into boolean value
        
        end = None
        # Default end date value
        
        if not is_curr:
            end = self.__prompt("End date  (e.g. Dec 2026)")
            # Asks for end date only if not current job

        exp = Experience(company=company, role=role,
                         start_date=start, end_date=end, is_current=is_curr)
        # Creates Experience object
        # Pillar Used: Encapsulation
        self.__current_user.add_experience(exp)
        # Adds experience into current user's profile
        
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
        # Retrieves selected Experience object
        self.__header("EDIT WORK EXPERIENCE")
        print("  Press Enter to keep the current value.\n")

        c = input(f"  Company [{exp.company}]: ").strip()
        if c:
            exp.company = c
            # Updates company attribute


        r = input(f"  Role [{exp.role}]: ").strip()
        if r:
            exp.role = r
            # Updates role attribute

        s = input(f"  Start date [{exp.start_date}]: ").strip()
        if s:
            exp.start_date = s
            # Updates start date

        curr = input(f"  Currently working here? (y/n) [{'y' if exp.is_current else 'n'}]: ").strip().lower()
        if curr == "y":
            exp.is_current = True
            # Sets current employment status
            exp.end_date = None
            # Removes end date because work is ongoing
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
        # Manages education records.
        # Pillar Used: Abstraction
        while True:
            self.__header("EDUCATION")
            edus = self.__current_user.educations
            # Retrieves education list
            
            if edus:
                print("  Your Education:\n")
                for i, e in enumerate(edus, 1):
                    print(f"  [{i}]")
                    e.display()
                    # Displays education object details
                    # Pillar Used: Polymorphism
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
                        # Removes selected education record
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
        # Gets school name
        degree = self.__prompt("Degree / Course")
        # Gets degree or course
        year_start = self.__prompt("Year started  (e.g. 2020)")
        # Gets starting year

        ongoing = input("  Still studying here? (y/n): ").strip().lower() == "y"
        # Converts answer into boolean
        
        year_end = None
        if not ongoing:
            year_end = self.__prompt("Year ended  (e.g. 2024)")

        edu = Education(school_name=school, degree=degree,
                        year_started=year_start, year_ended=year_end)
        # Creates Education object
        # Pillar Used: Encapsulation
        self.__current_user.add_education(edu)
        # Adds education into user profile
        self.__save_database()
        print("\n  ✅  Education added!")
        self.__pause()

    def __edit_education(self, edus):
        # Edits an education record.
        idx = input("  Enter education number to edit: ").strip()
        if not (idx.isdigit() and 1 <= int(idx) <= len(edus)):
            print("\n  ⚠️   Invalid number.")
            self.__pause()
            return

        edu = edus[int(idx) - 1]
        # Retrieves selected education object

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
        # Verifies old password before allowing changes
        # Pillar Used: Abstraction
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
        # Updates password securely using hash encryption
        # Pillar Used: Encapsulation
        self.__save_database()
        print("\n  ✅  Password changed successfully!")
        self.__pause()
