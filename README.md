# 🎬 YouTube Clone

A full-stack **YouTube-inspired video-sharing web application** built with **Flask, MySQL, SQLAlchemy, HTML, CSS, and JavaScript**.

The project implements core video-platform functionality such as user authentication, video uploading and playback, search, comments, reactions, premium subscriptions, Razorpay payment integration, and a custom video player.

---

## 📌 Project Overview

This project was developed to understand and implement the architecture of a modern full-stack web application.

It includes a Flask-based backend, MySQL database integration, dynamic Jinja templates, JavaScript-based frontend interactions, user authentication, video management, comments, subscriptions, and payment processing.

The application follows a modular structure using Flask Blueprints and SQLAlchemy models.

---

## ✨ Features

### 👤 User Authentication

* User registration and login
* Session-based authentication
* Password hashing
* Protected routes for authenticated users
* User profile-related functionality

### 🎥 Video Management

* Upload videos
* Upload video thumbnails
* Store video information in the database
* Watch uploaded videos
* Automatic view counting
* Next-video functionality
* Search videos

### ▶️ Custom Video Player

The application includes a custom video player with:

* Play / Pause
* Volume control
* Fullscreen mode
* Seek forward by 10 seconds
* Seek backward by 10 seconds
* Video duration display
* Loading state
* Next-video option
* Gesture-based controls

### 💬 Comments

* Add comments to videos
* Display comments on the watch page
* Comment reactions
* Support for displaying comments with location-related information
* Comment translation functionality

### 👍 Video Reactions

* Like videos
* Dislike videos
* Comment reactions

### 💎 Premium Subscriptions

The application provides multiple subscription plans:

| Plan   | Price |
| ------ | ----: |
| Free   |    ₹0 |
| Bronze |  ₹299 |
| Silver |  ₹599 |
| Gold   |  ₹999 |

Premium subscription functionality is integrated with **Razorpay Test Mode** for payment processing.

### 💳 Payment Integration

* Razorpay payment integration
* Test-mode payment processing
* Payment verification
* Subscription activation
* Email-related payment notifications

### 🔐 Security & Verification

* Password hashing
* Session-based authentication
* OTP-related user verification functionality
* User/device/location verification logic

### 🌐 Watch Party

The project also contains a watch-party feature allowing users to participate in synchronized video-watching functionality.

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap
* Jinja2 Templates

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Mail
* Flask-SocketIO

### Database

* MySQL
* SQLAlchemy
* PyMySQL

### Payment

* Razorpay API (Test Mode)

### Development Tools

* Visual Studio Code
* Git
* GitHub
* XAMPP / phpMyAdmin

---

## 📂 Project Structure

```text
youtube_clone/
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── .gitignore
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── video.py
│   ├── comment.py
│   └── comment_reaction.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── video.py
│   ├── subscription.py
│   └── watchparty.py
│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── ...
│
└── templates/
    ├── login.html
    ├── register.html
    ├── index.html
    ├── upload.html
    ├── watch.html
    └── ...
```

---

## ⚙️ Application Architecture

The application is organized into separate layers to keep the code maintainable.

```text
                ┌─────────────────────┐
                │      Frontend       │
                │ HTML / CSS / JS     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │    Flask Routes     │
                │   Authentication    │
                │ Videos / Comments   │
                │ Subscriptions       │
                │ Watch Party         │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │    SQLAlchemy ORM   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │       MySQL         │
                └─────────────────────┘

       External Services
              │
       ┌──────┴─────────┐
       ▼                ▼
   Razorpay          Gmail SMTP
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Riya04-web/youtube_clone.git
```

Navigate into the project:

```bash
cd youtube_clone
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

If PowerShell blocks script execution, you can activate the environment using Command Prompt:

```cmd
venv\Scripts\activate.bat
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

This project uses **MySQL**.

You can use **XAMPP** to run MySQL and phpMyAdmin.

### Start MySQL

1. Open XAMPP.
2. Start **MySQL**.
3. Open phpMyAdmin.
4. Create a database for the application.

Example:

```sql
CREATE DATABASE youtube_clone;
```

Configure the database connection through the application's environment variables.

---

## 🔑 Environment Variables

For security, sensitive credentials should **not** be stored directly in the source code or committed to GitHub.

Create a `.env` file locally and configure the required variables.

Example:

```env
SECRET_KEY=your_secret_key

DATABASE_URL=mysql+pymysql://username:password@localhost/youtube_clone

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

> **Important:** Never upload your `.env` file or API keys, payment secrets, email passwords, or other credentials to GitHub.

---

## ▶️ Running the Application

After activating the virtual environment and configuring MySQL:

```bash
python app.py
```

The Flask development server will start locally.

Open the application in your browser:

```text
http://127.0.0.1:5000
```

---

## 💳 Razorpay Configuration

The project uses **Razorpay Test Mode** for subscription payments.

To test payments:

1. Create/configure a Razorpay test account.
2. Obtain the test API credentials.
3. Add the credentials to your local environment variables.
4. Start the Flask application.
5. Select a subscription plan.
6. Complete the payment using Razorpay's test environment.

No real payment should be made while using test credentials.

---

## 📧 Email Configuration

The application can use Gmail SMTP for sending email-related notifications.

For Gmail:

* Enable 2-Step Verification.
* Generate a Gmail App Password.
* Use the App Password instead of the normal Gmail password.
* Store it in your environment variables.

Never commit the App Password to GitHub.

---

## 🧪 Testing

Before deployment, test the major application flows:

### Authentication

* Register a new user
* Login
* Logout
* Invalid login credentials

### Videos

* Upload a video
* Upload a thumbnail
* Watch a video
* Check view count
* Search for videos

### Comments

* Add a comment
* Display comments
* Test reactions
* Test translation functionality

### Subscriptions

* Select a subscription plan
* Open Razorpay checkout
* Test payment
* Verify subscription status

### Email

* Verify SMTP configuration
* Test email notification functionality

---

## 🔒 Security Considerations

The project uses several security-related practices, including:

* Password hashing
* Session-based authentication
* Environment variables for sensitive configuration
* Protected routes
* OTP-related verification functionality
* Razorpay payment verification

For production deployment, additional security measures should be implemented, including:

* CSRF protection
* Strong production secret keys
* Secure cookies
* HTTPS
* Production-grade database configuration
* File-upload validation
* Rate limiting
* Proper production logging
* Secure handling of uploaded media

---

## 🎯 Learning Objectives

Through this project, I worked with:

* Flask application structure
* Python backend development
* REST-style routing
* SQLAlchemy ORM
* MySQL database integration
* User authentication
* Password hashing
* File uploads
* Dynamic Jinja templates
* JavaScript frontend interactions
* Payment gateway integration
* Email integration
* WebSocket-based functionality
* Git and GitHub
* Environment-based configuration

---

## 🔮 Future Improvements

Possible future improvements include:

* Video recommendation algorithm
* User channels
* Creator dashboards
* Video categories
* Playlists
* Video editing
* Advanced notification system
* Improved recommendation/search system
* Production deployment
* Cloud-based video storage
* Adaptive video streaming
* Automated testing
* Improved responsive design
* Admin dashboard
* Content moderation

---

## 👩‍💻 Author

**Riya Sharma**

BCA Graduate | Python & Flask Developer

### Skills Used

`Python` `Flask` `MySQL` `SQLAlchemy` `HTML` `CSS` `JavaScript` `Bootstrap` `Razorpay` `Git` `GitHub`

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

**Repository:**
https://github.com/Riya04-web/youtube_clone

---

## 📄 License

This project was created for educational and portfolio purposes.
