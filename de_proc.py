import shutil
from email.message import EmailMessage
from shutil import copy2
from datetime import datetime
import os
import smtplib
import logging


def get_date_string():
    """Function: Get date string for log file name
        Returns: An array of strings containing current year and month ex. [2021, Aug]"""
    return datetime.now().strftime('%Y-%b').split('-')



def check_year_month_dir(dir):
    """Function: Check if year and month directories exist in src directory
       Parameters: dir = A string containing the the directory needed to be checked
       Returns: A string containing the directory for the current year and month"""
    
    try:
        year, month = datetime.now().strftime('%Y-%b').split('-')
        year_dir = os.path.join(dir, year)
        month_dir = os.path.join(year_dir, month)
        
        if os.path.isdir(year_dir):
            if not os.path.isdir(month_dir):
                logging.info(f"Current month folder not found. Creating {month} folder")
                os.mkdir(month_dir)
                
        else:
            logging.info(f"Current year folder not found. Creating {year} and {month} folders")
            os.mkdir(year_dir)
            os.mkdir(month_dir)
            
        return month_dir
    
    except Exception as e:
        logging.error(f'Error in check_year_month_dir function: {e}')
        

       

def move_files(src, destinations):
    """Function: Move files from source directory to destination directories
       Parameters: src = A string containing the source directory for the files to be moved, destinations = An array containing strings of the destination directories
       Returns: An array of file paths for the files to be moved from the source directory"""
    
    try:
        file_paths = []
        file_names = []
        
        for file in os.scandir(src):
            file_name = os.path.basename(file.name)
            file_path = file.path
            file_paths.append(file_path)
            file_names.append(file_name)
        
        for dest in destinations:
            logging.info(f'Moving files from {src} to {dest}')
            new_dest = check_year_month_dir(dest)
            
            for file_path in file_paths: 
                file_name = os.path.basename(file_path)
                             
                if os.path.isfile(os.path.join(new_dest, file_name)):
                    logging.warning(f'File {file_name} already exists in {new_dest}. Moving to dupes folder.')
                    copy2(file_path, 'dupes')
                    
                else:
                    logging.info(f'Moving {file_name} to {new_dest}')
                    copy2(file_path, new_dest)
                    
        logging.info(f'{len(file_names)} cert(s) backed up.')
        
        for file_name in file_names:
            logging.info(f'{file_name}')
            
                
        return file_paths
    
    except Exception as e:
        logging.error(f'Error in move_files function: {e}')
        



def delete_certs(dir):
    """Function: Delete files from source directory
       Parameters: dir = A string containing the directory for the files to be deleted"""
    logging.info(f'Deleting certs from {dir}')
    try:
        for file in os.scandir(dir):
            os.remove(file)
    except Exception as e:
        logging.error(f'Error in delete_certs function: {e}')
        
    


def send_email(contacts, subject, body, files=None):
    """Function: Send emails and attachments for backup success or Errors
       Parameters: contacts = An array containing strings of the recipient emails, subject = A string containing the email subject, 
                   body = A string containing the email message body, files = An array containing strings of the files to be attached in the email"""
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ', '.join(contacts)
        msg.set_content(body)
        
        logging.info(f'Sending email to {", ".join(contacts)} with {len(files)} file(s) attached.')
        
        for file in files:
            with open (file, "rb") as attachment:
                file_data = attachment.read()
                file_name = os.path.basename(attachment.name)
            
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    
    except Exception as e:
        logging.error(f'Error in send_email function: {e}')
        

          

def launch_DE_backup():
    """Function: Launch DE backup procedure"""
    
    today = datetime.now().strftime('%m-%d-%Y')
    logging.info(f'<---------------------Launching DE Backup Process for {today} --------------------->')
    try:
        src = 'docs' # DE working folder
        destinations = ['docs1', 'docs2'] # 4thBin server and box 
        attachments = move_files(src, destinations)
        contacts = ['gustavobrcn@hkotmail.com', EMAIL_ADDRESS] # DE team and management
        subject = f'DE Certs Backup Success'
        body = f'DE Certs Backup process for {today} has completed successfully.'
        attachments.append(log_path) # add log file to attachments with certs may not be needed
        send_email(contacts, subject, body, attachments)
        delete_certs(src)
    except Exception as e:
        logging.error(f'Error in backup process: {e}')
        subject = "DE Certs Backup Error"
        body = "Error in DE backup script. Please review logs and check certs."
        send_email(contacts, subject, body, [log_path])
 
 
def check_log_dir():
    """Function: Check if log directory exists"""
    
    try:
        year, month = get_date_string()
        log_path = os.path.join('log', year, month)
        
        if not os.path.isdir(log_path):
            os.mkdir('log\\' + year)
            os.mkdir(log_path)    
        
        return log_path + '\\4thBin_DE.log'
    
    except Exception as e:
        logging.basicConfig(filename='log\\4thBin_DE.log', level=logging.DEBUG)
        logging.error(f'Error in check_log_dir function: {e}')
        
        return 'log\\4thBin_DE.log'   

       
log_path = check_log_dir()  
logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

EMAIL_ADDRESS = os.environ.get('EMAIL_ADD')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

launch_DE_backup()




