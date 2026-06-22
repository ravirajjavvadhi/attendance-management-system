def get_institution_welcome_email(management_name: str, institution_name: str, management_email: str, generated_password: str, portal_url: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2563eb; margin: 0;">EduFlow AI</h1>
        </div>
        
        <p>Dear {management_name},</p>
        
        <p>Welcome to EduFlow AI.</p>
        
        <p>We are delighted to partner with <strong>{institution_name}</strong> in transforming academic operations through intelligent attendance management, communication automation, and institutional workflow optimization.</p>
        
        <p>Your management account has been successfully created.</p>
        
        <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #1e293b;">Account Information:</h3>
            <p style="margin: 5px 0;"><strong>Institution:</strong> {institution_name}</p>
            <p style="margin: 5px 0;"><strong>Management Email:</strong> {management_email}</p>
            <p style="margin: 5px 0;"><strong>Temporary Password:</strong> <span style="background-color: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{generated_password}</span></p>
            <p style="margin: 5px 0;"><strong>Login Portal:</strong> <a href="{portal_url}" style="color: #2563eb;">{portal_url}</a></p>
        </div>
        
        <p>You may sign in using:</p>
        <ol>
            <li>Email + Password</li>
            <li>Google Sign-In</li>
        </ol>
        
        <p style="background-color: #fef2f2; color: #991b1b; padding: 10px; border-radius: 6px; font-size: 0.9em;">
            <strong>IMPORTANT:</strong> If you use Google Sign-In, the Google account email must exactly match the management email registered with EduFlow AI.
        </p>
        
        <p>Upon first login:</p>
        <ul>
            <li>Change your password</li>
            <li>Configure classes and sections</li>
            <li>Authorize faculty members</li>
            <li>Begin onboarding students</li>
        </ul>
        
        <p>Thank you for choosing EduFlow AI.</p>
        
        <div style="margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
            <p style="margin: 0;">Warm Regards,</p>
            <p style="margin: 5px 0 0 0;"><strong>Javvadi Ravi Raj</strong></p>
            <p style="margin: 0; font-size: 0.9em; color: #64748b;">Founder & Managing Director<br>EduFlow AI</p>
        </div>
    </body>
    </html>
    """

def get_faculty_invitation_email(faculty_name: str, institution_name: str, faculty_email: str, generated_password: str, portal_url: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2563eb; margin: 0;">EduFlow AI</h1>
        </div>
        
        <p>Hello {faculty_name},</p>
        
        <p>You have been authorized to access the EduFlow AI Faculty Portal for <strong>{institution_name}</strong>.</p>
        
        <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
            <p style="margin: 5px 0;"><strong>Login Email:</strong> {faculty_email}</p>
            <p style="margin: 5px 0;"><strong>Temporary Password:</strong> <span style="background-color: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{generated_password}</span></p>
            <p style="margin: 5px 0;"><strong>Login Portal:</strong> <a href="{portal_url}" style="color: #2563eb;">{portal_url}</a></p>
        </div>
        
        <p>You may also use Google Sign-In with this same email address.</p>
        
        <div style="margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
            <p style="margin: 0;">Regards,</p>
            <p style="margin: 5px 0 0 0;"><strong>EduFlow AI Team</strong></p>
        </div>
    </body>
    </html>
    """
