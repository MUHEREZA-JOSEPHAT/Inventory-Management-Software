import os
from services.email_service import EmailService

def main():
    svc = EmailService()
    test_body = "This is a professional test message to verify the new 5 STAR branded supplier template. If you can see the Star logo and Charcoal header, the branding is working correctly!"
    template = svc._get_branded_template(test_body)
    
    preview_path = "D:/inventory management system/branding_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"Preview generated at: {preview_path}")

if __name__ == "__main__":
    main()
