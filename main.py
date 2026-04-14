import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.message import EmailMessage

USERNAME = os.getenv("UBS_USERNAME")
PASSWORD = os.getenv("UBS_PASSWORD")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER = os.getenv("RECEIVER_EMAIL")
DATA_FILE = "grades_data.json"

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })

    try:
        # Step 1: Access the root page to extract the verification token
        login_page = session.get("https://ubs.ikc.edu.tr/")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if token_input is None:
            print("CRITICAL ERROR: Could not find the verification token on the root page.")
            print(f"HTTP Status Code: {login_page.status_code}")
            raise Exception("Authentication token not found. Execution halted.")
            
        token = token_input['value']
        
        # Step 2: Send credentials via POST request to the correct login endpoint
        payload = {
            "__RequestVerificationToken": token,
            "username": USERNAME,
            "password": PASSWORD
        }
        session.post("https://ubs.ikc.edu.tr/Account/Login", data=payload)
        
        # Step 3: Fetch the grades page
        grades_url = "https://ubs.ikc.edu.tr/AIS/Student/Class/Index?sapid=jv5D8qXMcIiLg5!xDDx!3yOBwlg!xGGx!!xGGx!" 
        response = session.get(grades_url)
        current_grades = {}
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all("table")
            for table in tables:
                headers = [th.text.strip() for th in table.find_all('th')]
                
                # 'Ders Kodu' is required to locate the correct table correctly
                if 'Ders Kodu' in headers:
                    rows = table.find('tbody').find_all('tr', recursive=False)
                    for row in rows:
                        course_link = row.find('a', class_='btn-link')
                        if course_link:
                            course_name = row.find_all('td', recursive=False)[1].text.strip()
                            active_course = f"{course_link.text.strip()} - {course_name}"
                            current_grades[active_course] = {}
                            
                            inner_table = row.find('table', class_='table-condensed')
                            if inner_table:
                                for g_row in inner_table.find_all('tr'):
                                    cells = g_row.find_all('td')
                                    if len(cells) == 2:
                                        g_type = cells[0].text.strip().replace(" :", "")
                                        current_grades[active_course][g_type] = cells[1].text.strip()
                    break

        # Step 4: Compare data and send notification if required
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                old_grades = json.load(f)
            
            updates = ""
            for course, grades in current_grades.items():
                for g_type, val in grades.items():
                    old_val = old_grades.get(course, {}).get(g_type, "N/A")
                    if val != old_val:
                        updates += f"Course: {course}\nAssessment: {g_type}\nGrade: {old_val} -> {val}\n\n"
            
            if updates:
                send_email("Grade Update Detected", f"The automation detected new grade entries:\n\n{updates}")
        else:
            send_email("Automation Active", "The grade tracker has been successfully deployed and performed its first scan.")
                
        # Step 5: Save the latest data
        with open(DATA_FILE, "w") as f:
            json.dump(current_grades, f, indent=4)

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
