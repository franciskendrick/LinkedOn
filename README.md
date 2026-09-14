# LinkedOn

## Overview

**LinkedOn** is a simple, terminal-based social network built in Python. It is a direct copy of [LinkedIn](https://www.linkedin.com/in/francis-kendrick-maddumba-27288b402/), simulating key features of professional networking platforms, including the features to build profiles, add education and work experience, send connection requests, and create posts.

![Title screen of LinkedOn](title_screen.png)

## Context

This project was created as the **Final Project for Object-Oriented Programming (OOP)** at [De La Salle University - Dasmariñas](https://www.dlsud.edu.ph/).

To fulfill the project requirements, the application implements full CRUD operations (Create, Read, Update, Delete) and demonstrates the four pillars of Object-Oriented Programming:

* **Encapsulation:** Sensitive user data and profile details are protected inside objects using private attributes. Instead of changing data directly, the app uses getter and setter methods to control how data is viewed or modified.

* **Inheritance:** Common attributes are stored in a base class (`entity.py`), which child classes like `User`, `Education`, and `Experience` inherit to avoid repeating code.

* **Abstraction:** Complex code, like reading from files or filtering connection lists, is hidden behind clean, simple functions so the main application loop (`linkedon_app.py`) stays clean and easy to read.

* **Polymorphism:** Shared functions behave differently depending on the object using them (for example, displaying a user profile vs. displaying a post feed).


## Requirements & Setup

### Prerequisites

* **Python Version:** Python 3.12 or higher

* **External Packages:** None

### How to Run

1. Clone this repository:
```bash
git clone https://github.com/franciskendrick/LinkedOn.git
cd LinkedOn
```

2. Run the application:
```bash
python src/main.py
```

## File Structure

```text
LinkedOn/
├── database.json        # Saved data file
├── README.md            # Project documentation
└── src/                 # Source code directory
    ├── main.py          # Starts the program
    ├── linkedon_app.py  # Controls the app interface and menus
    ├── entity.py        # Shared base class for objects
    ├── user.py          # Manages user profile data
    ├── connection.py    # Manages user connections
    ├── education.py     # Manages education entries
    ├── experience.py    # Manages work experience entries
    └── post.py          # Manages post creation and feeds
```

## Recommendations

While the project met all requirements for the class, the following improvements would make the app more secure, stable, and ready for real-world use:

### 1. Hashing the Passwords

* **Issue:** Passwords are saved directly as plain text in the `database.json` file, which is unsafe.

* **Recommendation:** Encrypt or hash passwords using secure libraries (`hashlib` or `bcrypt`) before saving them to disk so raw passwords are never exposed.

### 2. Using a Real Database

* **Issue:** Saving everything in a single `database.json` file is risky. Data can easily get corrupted or lost.

* **Recommendation:** Switch from a JSON file to a relational database like **_SQLite_** or **_PostgreSQL_**.

### 3. Separate the App Logic from File Storage

* **Issue:** Parts of the menu code read and edit raw JSON dictionaries directly. If we change how data is saved in the future, we would have to rewrite the whole interface.

* **Recommendation:** Create a dedicated "Data Manager" class. The user interface will ask the Data Manager for objects, and the Data Manager will handle reading/writing to the file behind the scenes.

### 4. IS-A vs. HAS-A Inheritance

* **Issue:** Forcing every class (`User`, `Post`, `Connection`) to inherit from one master `Entity` class can cause issues later if these items need completely different rules.

* **Recommendation:** Instead of forcing classes to inherit everything from a single parent (**"IS-A"** relationship), build objects by combining smaller pieces (**"HAS-A"** relationship). For example, a `User` **has a** list of `Experience` objects.