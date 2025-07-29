import logging
import backoff
from requests.exceptions import HTTPError

from typing import List, TypedDict, Union, Dict
from typing_extensions import NotRequired

from mailjet_rest import Client as MailerClient

_LOGGER = logging.getLogger(__name__)

class NotifMessage(TypedDict):
    """ A message to send to a list of recipients """
    subject: str
    mail_content: str
    recipient: str
    bcc_recipients: NotRequired[list[str]]
    sender: str
    app_name: str


class Client(MailerClient):
    def __init__(self, api_key=None, api_secret=None, version=None):
        super().__init__(auth=(api_key, api_secret), version=version)

    def send_to_recipients(
        self,
        recipients: List[Union[str, Dict]],
        subject: str,
        mail_content: str,
        sender: str,
        app_name: str,
        bcc_recipients: List[Union[str, Dict]] = []):
        """ Send one mail to a list of recipients
        Returns:
            List of responses, one for each chunk of recipients.
        """
        
        MAX_RECIPIENTS = 50
        
        def chunk_recipients(recipients_list: List, chunk_size: int):
            """Split recipients into chunks of specified size"""
            for i in range(0, len(recipients_list), chunk_size):
                yield recipients_list[i:i + chunk_size]
        
        @backoff.on_exception(backoff.expo, HTTPError, max_tries=5)
        def send_chunk(recipients_chunk):
            """Send a single chunk of recipients and retry on failure."""
            messages = [
                {
                    "From": {"Email": sender, "Name": f"{app_name} alerting"},
                    "To": [{"Email": recipient}],
                    "Bcc": bcc_recipients,
                    "Subject": subject,
                    "HTMLPart": mail_content
                }
                for recipient in recipients_chunk
            ]
            response = self.send.create(data={"Messages": messages})
            response.raise_for_status()
            return response

        all_responses= []
        total_chunks = (len(recipients) + MAX_RECIPIENTS - 1) // MAX_RECIPIENTS
        
        for chunk_index, recipients_chunk in enumerate(chunk_recipients(recipients, MAX_RECIPIENTS), 1):
            try:
                _LOGGER.debug(f"Sending email to chunk {chunk_index}/{total_chunks} ({len(recipients_chunk)} recipients)")
                response = send_chunk(recipients_chunk)
                all_responses.append(response)
                _LOGGER.info(f"Successfully sent email to {len(recipients_chunk)} recipients")
                
            except Exception as e:
                error_msg = f"Error sending email to chunk {chunk_index} ({len(recipients_chunk)} recipients): {e}"
                _LOGGER.error(error_msg)
                raise
        
        _LOGGER.info(f"Completed sending emails to {len(recipients)} total recipients in {total_chunks} chunks")
        return all_responses
        
    def send_bulk(
        self,
        messages: list[NotifMessage],
        ):
        """ Send one mail to a list of recipients """
        formated_messages = [{"From": {"Email": msg['sender'], "Name": f"{msg['app_name']} alerting"},
                              "To": [{'Email': msg['recipient']}],
                              "Bcc": msg.get('bcc_recipients', []),
                              "Subject": msg['subject'],
                              "HTMLPart": msg['mail_content']} for msg in messages]
        return self.send.create(data={
            'Messages': formated_messages
        })

