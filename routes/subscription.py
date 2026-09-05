from flask import Blueprint, render_template, session, redirect, url_for, send_from_directory, send_file
from models.user import User
from extensions import db
import razorpay
from config import Config
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_mail import Message
from extensions import mail
import os
import io
from reportlab.pdfgen import canvas



subscription = Blueprint(
    "subscription",
    __name__
)

@subscription.route("/download_invoice")
def download_invoice():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("auth.login"))

    if not user.payment_id:
        return "Invoice not available"

    if not user.plan or user.plan.lower() == "free":
        return "Invoice not available"

    invoice_file = generate_invoice(
        user,
        user.plan,
        user.payment_id
    )

    return send_file(
        invoice_file,
        as_attachment=True,
        download_name=f"invoice_{user.payment_id}.pdf",
        mimetype="application/pdf"
    )

print("RAZORPAY KEY ID:", Config.RAZORPAY_KEY_ID)
print("RAZORPAY SECRET EXISTS:", bool(Config.RAZORPAY_KEY_SECRET))

client = razorpay.Client(
    auth=(
        Config.RAZORPAY_KEY_ID,
        Config.RAZORPAY_KEY_SECRET
    )
)

plans = {

    "Bronze": 299,

    "Silver": 599,

    "Gold": 999

}

def generate_invoice(user, plan, payment_id):

    # Create PDF in memory instead of saving to Vercel filesystem
    pdf_buffer = io.BytesIO()

    pdf = canvas.Canvas(pdf_buffer)

    width, height = pdf._pagesize

    # ---------------- HEADER ----------------

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        60,
        height - 70,
        "YouTube Clone"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        60,
        height - 95,
        "Premium Subscription Invoice"
    )

    # Invoice number

    pdf.drawRightString(
        540,
        height - 70,
        "INVOICE"
    )

    pdf.drawRightString(
        540,
        height - 90,
        payment_id
    )

    # Line

    pdf.line(
        60,
        height - 120,
        540,
        height - 120
    )

    # ---------------- CUSTOMER DETAILS ----------------

    y = height - 170

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        60,
        y,
        "Customer Details"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        y - 30,
        f"Name: {user.username}"
    )

    pdf.drawString(
        60,
        y - 50,
        f"Email: {user.email}"
    )

    # ---------------- PLAN DETAILS ----------------

    y = y - 130

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        60,
        y,
        "Subscription Details"
    )

    # Table Header

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        70,
        y - 40,
        "Plan"
    )

    pdf.drawString(
        230,
        y - 40,
        "Duration"
    )

    pdf.drawString(
        380,
        y - 40,
        "Amount"
    )

    pdf.line(
        60,
        y - 50,
        540,
        y - 50
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        70,
        y - 80,
        plan
    )

    pdf.drawString(
        230,
        y - 80,
        "30 Days"
    )

    pdf.drawString(
        380,
        y - 80,
        f"Rs. {plans[plan]}"
    )

    # ---------------- PAYMENT DETAILS ----------------

    y = y - 160

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        60,
        y,
        "Payment Information"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        y - 30,
        f"Payment ID: {payment_id}"
    )

    pdf.drawString(
        60,
        y - 50,
        "Payment Status: Successful"
    )

    pdf.drawString(
        60,
        y - 70,
        f"Valid Until: {user.subscription_end.strftime('%d-%m-%Y')}"
    )

    # ---------------- FOOTER ----------------

    pdf.line(
        60,
        120,
        540,
        120
    )

    pdf.setFont(
        "Helvetica-Oblique",
        10
    )

    pdf.drawCentredString(
        300,
        90,
        "Thank you for choosing YouTube Clone Premium"
    )

    pdf.drawCentredString(
        300,
        70,
        "This is a computer generated invoice."
    )

    pdf.save()

    # Move pointer back to beginning
    pdf_buffer.seek(0)

    return pdf_buffer

@subscription.route("/reset_subscription")
def reset_subscription():

    if "user_id" not in session:
        return "Please login first"

    user = User.query.get(session["user_id"])

    if not user:
        return "User not found"

    user.plan = "Free"
    user.subscription_status = "Inactive"
    user.subscription_start = None
    user.subscription_end = None
    user.payment_id = None
    user.invoice_file = None

    session["plan"] = "Free"

    db.session.commit()

    return "Subscription reset successfully. You can now test Razorpay again."

@subscription.route("/subscription")
def subscription_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    return render_template(
        "subscription.html",
        user=user,
        config=Config
    )


@subscription.route("/create_order/<plan>")
def create_order(plan):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    amount = plans.get(plan)

    if not amount:
        return jsonify({
            "status": "failed",
            "message": "Invalid Plan"
        }), 400

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify(order)

@subscription.route("/payment_success", methods=["POST"])
def payment_success():


    if "user_id" not in session:
        return jsonify({
            "status":"failed",
            "message":"Login required"
        })


    data = request.get_json()


    plan = data["plan"]

    payment_id = data["razorpay_payment_id"]

    order_id = data["razorpay_order_id"]

    signature = data["razorpay_signature"]



    # 🔐 VERIFY RAZORPAY SIGNATURE

    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id": order_id,

            "razorpay_payment_id": payment_id,

            "razorpay_signature": signature

        })


        print("✅ Payment verification successful")


    except Exception as e:

        print("❌ Payment verification failed", e)

        return jsonify({

            "status":"failed"

        })



    user = User.query.get(
        session["user_id"]
    )


    # Update subscription

    user.plan = plan
    
    session["plan"] = plan

    user.subscription_status = "Active"

    user.subscription_start = datetime.utcnow()

    user.subscription_end = datetime.utcnow() + timedelta(days=30)

    user.payment_id = payment_id



    db.session.commit()



    # Generate invoice in memory
    invoice_file = generate_invoice(
        user,
        plan,
        payment_id
    )



    # Email confirmation

    msg = Message(

        subject="🎉 Subscription Activated - YouTube Clone",

        recipients=[user.email]

    )


    msg.body = f"""

Hello {user.username},


Your {plan} subscription has been activated successfully 🎉


Payment ID:
{payment_id}


Valid Until:
{user.subscription_end.strftime('%B %d, %Y')}


Thank you for using YouTube Clone 🚀

"""


    try:

        msg.attach(
            f"invoice_{payment_id}.pdf",
            "application/pdf",
            invoice_file.getvalue()
    )

        mail.send(msg)

        print("✅ Email sent successfully")

    except Exception as e:

        print("❌ Email sending failed:", e)

    return jsonify({
    "status": "success"
})