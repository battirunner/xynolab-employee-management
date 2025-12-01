import aiosmtplib
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from typing import List, Optional
from app.core.config import settings
from app.models.employee import Employee
from app.models.salary import SalaryRecord
import csv

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    attachments: Optional[List[dict]] = None
):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to_email

    if text_content:
        text_part = MIMEText(text_content, "plain")
        message.attach(text_part)

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    if attachments:
        for attachment in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment["content"])
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment["filename"]}"'
            )
            message.attach(part)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_username,
            password=settings.smtp_password,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def generate_salary_report_csv(employee: Employee, salary_record: SalaryRecord) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Employee Salary Report"])
    writer.writerow([])
    writer.writerow(["Employee Details"])
    writer.writerow(["Employee ID", employee.employee_id])
    writer.writerow(["Name", f"{employee.first_name} {employee.last_name}"])
    writer.writerow(["Department", employee.department or "N/A"])
    writer.writerow(["Position", employee.position or "N/A"])
    writer.writerow([])
    writer.writerow(["Salary Details"])
    writer.writerow(["Month", f"{salary_record.month}/{salary_record.year}"])
    writer.writerow(["Base Amount", f"${salary_record.base_amount}"])
    writer.writerow(["Overtime Amount", f"${salary_record.overtime_amount}"])
    writer.writerow(["Bonus", f"${salary_record.bonus}"])
    writer.writerow(["Deductions", f"${salary_record.deductions}"])
    writer.writerow(["Net Amount", f"${salary_record.net_amount}"])
    writer.writerow(["Status", salary_record.status.value])
    writer.writerow(["Payment Date", str(salary_record.payment_date) if salary_record.payment_date else "Not paid"])
    
    return output.getvalue()

async def send_salary_update_notification(
    to_email: str,
    employee: Employee,
    salary_record: SalaryRecord
):
    subject = f"Salary Update - {salary_record.month}/{salary_record.year}"
    
    html_template = Template("""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Salary Update Notification</h2>
        
        <p>Dear {{ employee_name }},</p>
        
        <p>Your salary for <strong>{{ month }}/{{ year }}</strong> has been updated to <strong>{{ status }}</strong>.</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Salary Details:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px 0;"><strong>Base Amount:</strong></td>
                    <td style="padding: 5px 0;">${{ base_amount }}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>Overtime:</strong></td>
                    <td style="padding: 5px 0;">${{ overtime_amount }}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>Bonus:</strong></td>
                    <td style="padding: 5px 0;">${{ bonus }}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>Deductions:</strong></td>
                    <td style="padding: 5px 0;">${{ deductions }}</td>
                </tr>
                <tr style="border-top: 1px solid #ddd;">
                    <td style="padding: 5px 0;"><strong>Net Amount:</strong></td>
                    <td style="padding: 5px 0; font-weight: bold;">${{ net_amount }}</td>
                </tr>
            </table>
        </div>
        
        {% if payment_date %}
        <p><strong>Payment Date:</strong> {{ payment_date }}</p>
        {% endif %}
        
        <p>Please find the detailed salary report attached to this email.</p>
        
        <p>If you have any questions, please contact HR department.</p>
        
        <p>Best regards,<br>
        Employee Management System</p>
    </body>
    </html>
    """)
    
    html_content = html_template.render(
        employee_name=f"{employee.first_name} {employee.last_name}",
        month=salary_record.month,
        year=salary_record.year,
        status=salary_record.status.value,
        base_amount=salary_record.base_amount,
        overtime_amount=salary_record.overtime_amount,
        bonus=salary_record.bonus,
        deductions=salary_record.deductions,
        net_amount=salary_record.net_amount,
        payment_date=salary_record.payment_date
    )
    
    csv_content = generate_salary_report_csv(employee, salary_record)
    attachment = {
        "filename": f"salary_report_{employee.employee_id}_{salary_record.month}_{salary_record.year}.csv",
        "content": csv_content.encode()
    }
    
    return await send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        attachments=[attachment]
    )

async def send_welcome_email(to_email: str, employee_name: str, username: str, temp_password: str):
    subject = "Welcome to Employee Management System"
    
    html_template = Template("""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Welcome to the Team!</h2>
        
        <p>Dear {{ employee_name }},</p>
        
        <p>Welcome to our Employee Management System! Your account has been created successfully.</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Your Login Credentials:</h3>
            <p><strong>Username:</strong> {{ username }}</p>
            <p><strong>Temporary Password:</strong> {{ temp_password }}</p>
        </div>
        
        <p><strong>Important:</strong> Please change your password after your first login for security reasons.</p>
        
        <p>You can use the system to:</p>
        <ul>
            <li>Check in and check out daily</li>
            <li>View your attendance records</li>
            <li>View your salary information</li>
            <li>Submit leave requests</li>
        </ul>
        
        <p>If you have any questions, please contact your administrator.</p>
        
        <p>Best regards,<br>
        Employee Management System</p>
    </body>
    </html>
    """)
    
    html_content = html_template.render(
        employee_name=employee_name,
        username=username,
        temp_password=temp_password
    )
    
    return await send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )

async def send_employee_invitation(to_email: str, token: str):
    subject = "Employee Invitation - Join Our Team"
    
    # You'll need to replace this URL with your actual frontend URL
    invitation_link = f"http://localhost:3000/invitation/accept?token={token}"
    
    html_template = Template("""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">You're Invited to Join Our Team!</h2>
        
        <p>Dear Future Team Member,</p>
        
        <p>You have been invited to join our organization as an employee. We're excited to have you on board!</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">What's Next?</h3>
            <p>Click the button below to complete your registration and set up your account:</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="{{ invitation_link }}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Complete Registration
                </a>
            </div>
            
            <p style="font-size: 12px; color: #666;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{{ invitation_link }}">{{ invitation_link }}</a>
            </p>
        </div>
        
        <p>During registration, you'll be able to:</p>
        <ul>
            <li>Set your username and password</li>
            <li>Provide your personal information</li>
            <li>Review your employment details</li>
        </ul>
        
        <p><strong>Important:</strong> This invitation link will expire in 7 days for security purposes.</p>
        
        <p>If you have any questions or need assistance, please contact our HR department.</p>
        
        <p>We look forward to working with you!</p>
        
        <p>Best regards,<br>
        {{ company_name }}</p>
    </body>
    </html>
    """)
    
    html_content = html_template.render(
        invitation_link=invitation_link,
        company_name=settings.smtp_from_name
    )
    
    return await send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )