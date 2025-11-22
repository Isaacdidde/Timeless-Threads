Timeless Threads — Modern Flask E-Commerce Platform

Timeless Threads is a full-stack e-commerce web application built with Flask, powered by MongoDB Atlas, and deployed on Render.
It features secure Email-OTP authentication, a responsive product catalog, shopping cart, reviews, and a clean modern UI.

Live Demo

Website: https://timeless-threads.onrender.com

(Hosted on Render free tier — may take 30 seconds to wake up.)

📌 Key Features
🔐 Authentication

- Login & Signup via Email OTP (no password required)

- Professional HTML email sent via Resend Email API

- Secure OTP validation stored in temporary memory

- Session-based login system

- Safe error handling & sanitization

🛍️ E-Commerce Features

- Category-based product browsing

- Product detail page with:

- Image gallery slider

- Thumbnails + auto slide

- Size & color selection

- Highlights & specifications

- Customer review system (Add/Edit/Delete)

- Add to cart, remove from cart

- Full cart page with:

- Price breakdown

- Quantity display

- Color preview badge

- Review system showing star ratings & averages

💾 Backend

- Flask (Python)

- MongoDB Atlas (Cloud NoSQL)

- Simple MVC structure:

- /controllers

- /models

- /routes

- /static

- /templates

- Fully modular & easy to extend

🌐 Deployment

- Deployed on Render

Uses:

- gunicorn as production server

- .env environment variables

- Production MongoDB Atlas cluster

🗂 Project Structure

timeless-threads/
│── app.py
│── requirements.txt
│── .env (local only)
│── controllers/
│     ├── auth_controller.py
│     ├── product_controller.py
│     └── review_controller.py
│
│── models/
│     ├── user_model.py
│     ├── otp_model.py
│     └── product_model.py
│
│── routes/
│     ├── auth_routes.py
│     ├── product_routes.py
│     └── review_routes.py
│
│── templates/
│     ├── base.html
│     ├── home.html
│     ├── login.html
│     ├── signup.html
│     ├── product_detail.html
│     ├── cart.html
│     └── verify_otp.html
│
│── static/
│     ├── css/
│     ├── js/
│     └── images/
│
└── utils/
      └── otp_generator.py
Tech Stack
Backend

Python 3.11

Flask 2.3

Flask-PyMongo

JWT (for safe token utilities)

Gunicorn (production server)

Database

MongoDB Atlas

Collections:

users

products

reviews

cart

otp_store (temporary storage)

Frontend

HTML / Jinja2

CSS

JavaScript

Bootstrap-enhanced components

Email Delivery

Resend Email API (SMTP-less)

HTML-styled email template

📦 Installation & Setup (Local)
1️⃣ Clone the repository
git clone https://github.com/Isaacdidde/Timeless-Threads.git
cd Timeless-Threads

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate  (Windows)

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add your .env file (local)
SECRET_KEY=your-secret-key
MONGO_URI=your-mongodb-atlas-uri

RESEND_API_KEY=your-resend-key
SENDER_EMAIL=your-sender-email   # example: support@timelessthreads.store

5️⃣ Run the server
python app.py


App will run at:

http://127.0.0.1:5000

🚀 Deploying to Render
1️⃣ Push to GitHub
git add .
git commit -m "deploy update"
git push origin main

2️⃣ Create Render Web Service

Select repo

Choose Python environment

Set build command:

pip install -r requirements.txt


Set start command:

gunicorn app:app

3️⃣ Add Environment Variables (Render Dashboard)
SECRET_KEY=
MONGO_URI=
RESEND_API_KEY=
SENDER_EMAIL=

4️⃣ Deploy

Render will auto-build & host your project.

📝 Environment Variables
Variable	Purpose
SECRET_KEY	Flask session encryption
MONGO_URI	MongoDB Atlas connection
RESEND_API_KEY	For sending OTP emails
SENDER_EMAIL	Verified email in Resend
🧪 Testing the OTP Flow

Open /auth/login

Enter your email

Check inbox for OTP

Enter OTP → login successful

Same flow works for signup

🛠 Future Enhancements (Upcoming)

Admin dashboard

Wishlist system

Payment gateway integration (Razorpay/Stripe)

Order management & tracking

User profile page

Address book for checkout

Coupon system

Inventory stock management

Product filters & sorting

❤️ Contributing

Contributions are welcome!
Feel free to fork the repo and submit pull requests.

📄 License

This project is open-source under the MIT License.
