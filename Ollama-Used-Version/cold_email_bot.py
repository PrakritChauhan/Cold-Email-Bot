import requests
import time
from groq import Groq
import ollama
from bs4 import BeautifulSoup
import smtplib

SPREADSHEET_API_KEY = "YOUR_SPREADSHEET_API_KEY"
APP_ID = "YOUR SPREADSHEET_APP_ID"
ENDPOINT_URL = f"https://sheetdb.io/api/v1/{APP_ID}"
EMAIL = "YOUR EMAIL"
PASSWORD = "YOUR APP PASSWORD"

class ColdEmailBot:

    def __init__(self, email_count, email_length):
        self.sender_offer = "YOUR OFFER. WHAT ARE YOU ASKING OR DOING"
        self.email_count = email_count
        self.email_length = email_length
        self.groq_api_key = "YOUR GROQ API KEY"
        self.model_1 = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.client_1 = Groq(api_key=self.groq_api_key)
        self.model_2 = "email-bot"
        self.client_2 = ollama.Client()
        # start smtp connection
        self.connection = smtplib.SMTP('smtp.gmail.com', 587)
        self.connection.starttls()
        self.connection.login(EMAIL, PASSWORD)

    def read_spreadsheet(self):
        params = {
            "limit": self.email_count        #Add more params if needed. Refer to documentation
        }

        headers = {
            "Authorization": f"Bearer {SPREADSHEET_API_KEY}"
        }

        response = requests.get(ENDPOINT_URL, params=params, headers=headers)

        if response.status_code == 200:
            email_list_data = response.json()
            print(email_list_data)
            return email_list_data
        else:
            print(f"{response.status_code}: {response.text}")
            return None

    def scrape_information(self, name, role, website_data):
        # iterates through website_data list and appends website text into information.
        information = f"Name:{name}\n Role:{role}\n"
        for website in website_data.split(","):
            try:
                html_text = requests.get(website).text
                soup = BeautifulSoup(html_text, "html.parser")

                # Remove scripts, styles, and meta
                for tag in soup(['script', 'style', 'meta', 'footer', 'nav']):
                    tag.decompose()

                # Extract visible text
                visible_text = soup.get_text(separator='\n')

                # Clean empty lines
                lines = [line.strip() for line in visible_text.splitlines() if line.strip()]

                # Keep only first 10 non-empty lines that have 50+ characters (likely to be meaningful)
                significant_lines = [line for line in lines if len(line) > 50][:10]
                cleaned_text = '\n'.join(significant_lines)

                if len(cleaned_text) > 1500:
                    cleaned_text = cleaned_text[:1500] + "..."

                information += f"{website}: {cleaned_text}\n"
            except Exception as e:
                print(f"Error scraping website {website}: {e}")
        return information

    def generate_email(self, information):
        # Generates emails using the information
        #put your name in the prompt where ever you see my name. Edit the prompt to your needs before using it through either google gemini or chatgpt
        system_prompt = f"""
        You're a **master and expert cold email copywriter**. Your primary goal is to **write highly effective cold outreach emails that maximize response rates.**

        **Output Format Constraint: You MUST ONLY generate the Subject Line and the Email Body. No other text, no conversational filler, no pre-text, no post-text.**
        **The final output MUST strictly follow the exact format below, including the 'Subject:' and 'Email:' labels.**
    
        **Sender Information:**
        - FROM: Prakrit Chauhan
        - Offering: {self.sender_offer}
        - The email should focus entirely on the recipient and their business, not on Prakrit Chauhan's specific role or internal details.
    
        **Recipient Information & Personalization Strategy:**
        - The user will provide 'information' about the recipient. This 'information' will include their Name, Role, and other relevant details about them or their business/organization.
        - **Your core task is to analyze this provided 'information' to find the MOST relevant, unique, and compelling details about the recipient or their business.**
        - **Leverage these specific details to craft a highly personalized and human-toned email.** The email must clearly demonstrate you've done your research.
        - **The personalization should specifically connect Prakrit Chauhan's offering to a recognized need, challenge, or opportunity within the recipient's context.**
        - Do NOT invent any facts or details not present in the provided 'information'.
        - The email is FROM Prakrit Chauhan TO the recipient. Ensure the perspective is always from the sender.
        - **CRITICAL DOUBLE-CHECK: The email body MUST NOT include any beginning salutations (e.g., "Hi [Name]," "Dear [Name]," "Hello," "Hi there," "I hope this message finds you well," etc.) or any ending salutations/sign-offs (e.g., "Best," "Regards," "Sincerely," "Thanks," "Kind regards," "Prakrit," "Prakrit Chauhan," or any similar phrases).** The email body should start directly with the first sentence of the message content and end with the last sentence of the message content.
        - **NEVER use placeholders like "[Your Name]", "[Recipient Name]", or "[Sender Name]". If a name is needed, use "Prakrit Chauhan" if referring to the sender, or the recipient's actual name from 'information'.**
    
        **Email Body Template (MUST FOLLOW THIS STRUCTURE PRECISELY):**
        **[HOOK (1-2 sentences):** This is the crucial opener. Start by conveying **genuine enthusiasm or strong admiration** for a **SPECIFIC, truly unique, and impressive detail** about the recipient, their recent work, or their company's achievement, found **ONLY IN THE PROVIDED 'information'.** For example, "Your [specific achievement/insight] truly stands out." Immediately following this, briefly state your intention to be quick and directly explain *why* this specific admiration led you to reach out and offer Prakrit Chauhan's solution, connecting it to a relevant challenge or opportunity for them. Avoid generic time-saving phrases like "knowing you're busy"; let the directness and relevance imply respect for their time.]
        **[OFFERING & CONNECTION (1-2 sentences):** **Elaborate slightly on Prakrit Chauhan's offering, making its benefits clear and explicitly connecting them to the unique aspect highlighted in the hook.** Show how the offering directly supports, enhances, or solves a challenge related to that unique achievement or role of the recipient.]
        **[CALL TO ACTION (1 sentence):** A clear, low-friction conclusion inviting further discussion.]
    
        **Length Constraint:**
        - **The entire email body (including Hook, Offering & Connection, and Call to Action) MUST be between {self.email_length - 5} and {self.email_length + 10} words.**
        - **This word limit is NON-NEGOTIABLE and applies to EVERY SINGLE EMAIL GENERATED.**
        - **CRITICAL DOUBLE-CHECK: Ensure the word count is strictly within the specified range.**
    
        **Subject Line Requirements:**
        - Write a human, conversational, and compelling subject line.
        - Avoid generic, AI-sounding, or overly salesy phrases.
        - Aim for curiosity-driven, relevant, or benefit-focused subject lines that hint at the personalized value for the recipient's business.
        - Reflect Prakrit Chauhan's offering, framed by the recipient's specific context if possible.
    
        **Final Output Format:**
        Subject: [Your compelling subject line here]
        Email: [Your complete email body here, following all length and content rules]
    
        **SELF-CORRECTION / FINAL REVIEW:**
        Before providing the final output, mentally review your generated Subject and Email against these absolute rules:
        1.  **NO SALUTATIONS (start or end)?**
        2.  **Word count is STRICTLY {self.email_length - 5} to {self.email_length + 10} words?**
        3.  **NO PLACEHOLDERS like [Name]?**
        4.  **Exactly 'Subject: ...' and 'Email: ...' and nothing else?**
        If any rule is violated, re-generate immediately.
        """
        messages = [
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": information},
        ]
        response = self.client_1.chat.completions.create(model=self.model_1, messages=messages)
        email = response.choices[0].message.content
        print(email)

        subject_line = ""
        email_body = ""

        if "Subject:" in email and "Email:" in email:
            # Split once at "Subject" then at "Email"
            subject_line = email.split("Subject:", 1)[1].split("Email:", 1)[0].strip()
            email_body = email.split("Subject:", 1)[1].split("Email:", 1)[1].strip()
        else:
            print("Expected format not found in response.")
            return None

        ollama_enhancement_prompt_template = f"""
        SYSTEM \"\"\"
        You are an expert business email editor. Your job is to take the following draft cold email and rewrite it to sound more natural,
        conversational, human, and professional — while retaining the original intent and message.

        **CRITICAL RULES TO FOLLOW ABSOLUTELY:**
        -   **NO STARTING SALUTATIONS WHATSOEVER.** Do NOT include "Hi [Name]," "Hello," "Dear," "I hope this message finds you well," or any similar greetings. The email MUST begin directly with the first sentence of the message content.
        -   **NO ENDING SALUTATIONS, SIGN-OFFS, OR SENDER NAME WHATSOEVER.** Do NOT include "Best," "Regards," "Sincerely," "Thanks," "Kind regards," "Prakrit," "Prakrit Chauhan," or any similar phrases. The email MUST end directly with the last sentence of the message content.
        -   **MAINTAIN EXACT LENGTH:** The revised email MUST contain the exact same number of words as the original draft provided to you. Do NOT add or remove words. The original draft has {self.email_length} words.
        -   **NO PLACEHOLDERS:** Do NOT use "[Name]", "[Recipient Name]", "[Your Name]", or any similar placeholders.

        Ensure the revised email:
        - Is polite, persuasive, and business-appropriate.
        - Feels personal and authentic, not AI-generated.
        - Avoids overly robotic, formal, or salesy language.
        - Keeps the meaning and key points intact.
        - Do not modify names, dates, facts, or calls to action.

        Only return the improved email text — no extra commentary or formatting.
        \"\"\"

        Here is the draft email body to revise:
        ---
        {email_body}
        ---

        Revised Email:
        """
        enhanced_email = self.client_2.generate(model=self.model_2, prompt=ollama_enhancement_prompt_template).response
        if enhanced_email[0] == " ":
            enhanced_email = enhanced_email[1:]

        full_email = {"Subject": subject_line, "Email": enhanced_email}
        print(full_email)
        return full_email


    def remove_recipient(self, email, name, update_status):
        #removes recipient and sends update to GUI
        try:
            headers = {
                "Authorization": f"Bearer {SPREADSHEET_API_KEY}"
            }

            response = requests.delete(f"{ENDPOINT_URL}/Email/{email}", headers=headers)
            message = f"{name} with {email} was successfully removed."
        except requests.exceptions.RequestException as e:
            message = f"A requests related error occurred while attempting to remove {name} with {email}: {e}"
        except requests.exceptions.HTTPError as e:
            message = f"HTTP Error: {response.status_code} - {response.text}"
        except Exception as e:
            message = f"An error occurred while attempting to remove {name}: {e}"
        finally:
            update_status(message)


    def send_email(self, update_status):
        email_list = self.read_spreadsheet()

        if email_list is not None:
            for recipient in email_list:
                information = self.scrape_information(recipient["Name"], recipient["Role"], recipient["Websites"])
                email = self.generate_email(information)
                try:
                # In this line, add any honorifics you need to start email and salutation to end email in msg. Change my name into yours
                    self.connection.sendmail(from_addr=EMAIL, to_addrs=recipient["Email"], msg=f"Subject:{email["Subject"]}\n\nHey {recipient["Name"].split()[0]},\n\n{email["Email"]}\n\nBest,\nPrakrit Chauhan")
                    message = f"Email sent successfully to recipient:{recipient['Name']} at email:{recipient['Email']}"
                    self.remove_recipient(recipient["Email"],
                                          recipient["Name"], update_status)
                except smtplib.SMTPException as e:
                    message = f"Error sending email to recipient {recipient["Email"]}: {e}"
                except Exception as e:
                    message = f"An error occurred sending email to {recipient['Email']}: {e}"
                finally:
                    update_status(message)
                    time.sleep(5)
        self.connection.quit()