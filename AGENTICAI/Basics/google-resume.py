import os
import google.generativeai as genai

# 🔐 Use environment variable
api_key = os.getenv("GOOGLE_API_KEY")

MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """
You are a professional resume builder.
Generate a clean, ATS-friendly resume.
Format it properly with sections:
Name
Contact Information
Career Objective
Education
Skills
Projects
Experience (if any)
Certifications
Keep it professional and well structured.
"""

def setup():
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT
    )

    chat = model.start_chat(history=[])
    return chat


def generate_resume(chat, user_data: str):
    response = chat.send_message(user_data)
    print("\n\n📄 ===== YOUR GENERATED RESUME ===== 📄\n")
    print(response.text)
    print("\n=====================================\n")


chat = setup()

print("📝 Resume Builder\n")

name = input("Enter your full name: ")
email = input("Enter your email: ")
phone = input("Enter your phone number: ")
education = input("Enter your education details: ")
skills = input("Enter your skills (comma separated): ")
projects = input("Enter your projects: ")
experience = input("Enter your experience (or type Fresher): ")
certifications = input("Enter certifications (if any): ")

user_input_data = f"""
Name: {name}
Email: {email}
Phone: {phone}
Education: {education}
Skills: {skills}
Projects: {projects}
Experience: {experience}
Certifications: {certifications}
"""

generate_resume(chat, user_input_data)