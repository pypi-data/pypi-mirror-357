import requests
import time
import re

from functools import wraps
from typing import Optional, List, Dict, Union, Callable
from logmagix import Logger

class CyberTemp:
    def __init__(self, debug: bool = True, api_key: str = None) -> None:
        self.debug = debug
        self.log = Logger()
        self.session = requests.Session()
        if api_key:
            self.session.headers = {"X-API-KEY": api_key}

    def debug_log(self, func_or_message: Union[Callable, str], *args, **kwargs) -> Callable:
        if callable(func_or_message):
            @wraps(func_or_message)
            def wrapper(*args, **kwargs):
                result = func_or_message(*args, **kwargs)
                if self.debug:
                    self.log.debug(f"{func_or_message.__name__} returned: {result}")
                return result
            return wrapper
        else:
            if self.debug:
                self.log.debug(f"Debug: {func_or_message}")

    def check_mailbox(self, email: str, max_retries: int = 5, delay_between_retries: float = 2.0) -> Optional[List[Dict]]:
        self.debug_log(f"Checking mailbox for {email}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(f'https://www.cybertemp.xyz/api/getMail?email={email}')
                if response.status_code == 200:
                    return response.json()
                else:
                    self.log.failure(f"Failed to check mailbox: {response.text}, {response.status_code}")
                    break
            except Exception as e:
                self.log.failure(f"Error checking mailbox: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay_between_retries * (attempt + 1))
                    continue
                break
        return None

    def get_mail_by_subject(self, email: str, subject_contains: str, max_attempts: int = 10, delay_between_retries: float = 1.5) -> Optional[str]:
        attempt = 0
        self.debug_log(f"Getting message with subject containing '{subject_contains}' for {email}")
        
        while attempt < max_attempts:
            messages = self.check_mailbox(email, max_retries=1, delay_between_retries=delay_between_retries)
            if messages:
                for message in messages:
                    if subject_contains in message.get("subject", ""):
                        self.debug_log(message)
                        return message.get("id")
            attempt += 1
            time.sleep(delay_between_retries)
        self.debug_log(f"No matching message found after {attempt} attempts")
        return None

    def get_message_content(self, email: str, message_id: str) -> Optional[Dict]:
        self.debug_log(f"Fetching message {message_id} for {email}")
        messages = self.check_mailbox(email, max_retries=1)
        if messages:
            for message in messages:
                if message.get("id") == message_id:
                    return {
                        "text": message.get("text", ""),
                        "html": message.get("html", ""),
                        "subject": message.get("subject", "")
                    }
        return None

    def extract_url_from_message(self, email: str, subject_contains: str, url_pattern: str, max_attempts: int = 10, delay_between_retries: float = 1.5) -> Optional[str]:
        self.debug_log(f"Extracting URL for {email}")
        
        mail_id = self.get_mail_by_subject(email, subject_contains, max_attempts, delay_between_retries)
        if mail_id:
            message = self.get_message_content(email, mail_id)
            if message and message.get("html"):
                url_match = re.search(url_pattern, message["html"])
                if url_match:
                    return url_match.group(0)
        return None

    def get_email_content(self, email: str, max_retries: int = 5, delay_between_retries: float = 2.0) -> Optional[List[Dict]]:
        """
        GET /api/getMail - Fetch emails inbox.
        """
        self.debug_log(f"Getting emails for {email}")
        return self.check_mailbox(email, max_retries, delay_between_retries)

    def get_email_content_by_id(self, email_id: str) -> Optional[Dict]:
        """
        GET /api/email/{id} - Fetch a single email by ID.
        """
        self.debug_log(f"Getting email with id {email_id}")
        try:
            response = self.session.get(f"https://cybertemp.xyz/api/email/{email_id}")
            if response.status_code == 200:
                return response.json()
            else:
                self.log.failure(f"Failed to get email: {response.text}, {response.status_code}")
        except Exception as e:
            self.log.failure(f"Error getting email: {str(e)}")
        return None

    def get_domains(self) -> Optional[List[str]]:
        """
        GET /api/getDomains - Fetch all available email domains.
        """
        self.debug_log("Getting domains")
        try:
            response = self.session.get("https://cybertemp.xyz/api/getDomains")
            if response.status_code == 200:
                return response.json()
            else:
                self.log.failure(f"Failed to get domains: {response.text}, {response.status_code}")
        except Exception as e:
            self.log.failure(f"Error getting domains: {str(e)}")
        return None

    def get_balance(self) -> Optional[Dict]:
        self.debug_log("Getting balance")
        try:
            response = self.session.get("https://cybertemp.xyz/api/balance")
            if response.status_code == 200:
                return response.json()
            else:
                self.log.failure(f"Failed to get balance: {response.text}, {response.status_code}")
        except Exception as e:
            self.log.failure(f"Error getting balance: {str(e)}")
        return None
