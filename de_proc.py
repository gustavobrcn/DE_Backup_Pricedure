import shutil
from win10toast_click import ToastNotifier
from email.message import EmailMessage
from shutil import copy2
from datetime import datetime
import os
import smtplib
import logging
from time import sleep



def get_date_string():
    """Get date string for log file name"""
    return datetime.now().strftime('%Y-%b').split('-')



def check_year_month_dir(dest):
    """Check if year and month directories exist in src directory"""
    
    try:
        year, month = datetime.now().strftime('%Y-%b').split('-')
        year_dir = os.path.join(dest, year)
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
        return None

       

def move_files(src, destinations):
    """Move files from source directory to destination directory"""
    
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
                file_name = os.path.basename(file)                
                
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
        return None



def delete_certs(src):
    """Delete files from source directory"""
    logging.info(f'Deleting certs from {src}')
    try:
        for file in os.scandir(src):
            os.remove(file)
    except Exception as e:
        logging.error(f'Error in delete_certs function: {e}')
        return None
    


def send_email(contacts, subject, body, files=None):
    """Send emails and attachments"""
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
        return None

          

def launch_DE_backup():
    """Launch DE backup procedure"""
    today = datetime.now().strftime('%m-%d-%Y')
    logging.info(f'<---------------------Launching DE Backup Process for {today} --------------------->')
    try:
        src = 'docs' # DE working folder
        destinations = ['docs1', 'docs2'] # 4thBin server and box 
        attachments = move_files(src, destinations)
        contacts = ['gustavobrcn@hotmail.com', EMAIL_ADDRESS] # DE team and management
        subject = f'DE Certs Backup {today}'
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
    """Check if log directory exists"""
    year, month = get_date_string()
    log_path = os.path.join('log', year, month)
    
    if not os.path.isdir(log_path):
        os.mkdir('log\\' + year)
        os.mkdir(log_path)    
    
    return log_path + '\\4thBin_DE.log'   


def start_over():
    year, month = get_date_string()
    dirs = ['docs1', 'docs2', 'log', 'dupes']
    for file in os.scandir(f'docs1\\{year}\\{month}'):
        copy2(file.path, 'docs')
    
    for dir in dirs:
        for file in os.scandir(dir):
            shutil.rmtree(file.path)
    
        
log_path = check_log_dir()  
logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

EMAIL_ADDRESS = os.environ.get('EMAIL_ADD')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

launch_DE_backup()
# sleep(10)
# start_over()


