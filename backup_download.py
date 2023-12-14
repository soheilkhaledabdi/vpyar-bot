import telebot
import time
import schedule
import threading
import paramiko


TOKEN = '6495534406:AAHLkl9FJQdw42c8h0-ACs7AsgF3MVwM1L8'
bot = telebot.TeleBot(TOKEN)

def save_user_info(name, username, ip, password):
    with open('user_info.txt', 'a') as file:
        file.write(f"{name}|{username}|{ip}|{password}\n")

def get_credentials():
    with open('user_info.txt', 'r') as file:
        lines = file.readlines()
        return lines

def download_file_from_server(chat_id, name, username, ip, password):
    try:
        print("Downloading file from server")
        print("ip:", ip)
        print("username:", username)
        print("password:", password)
        print("name:", name)
        remote_file_path = '/etc/x-ui/x-ui.db'
        local_file_path = f"{name}_x-ui.db"

        print(name, username, ip, password)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip, port=22, username=username, password=password.replace("\n", ""))

        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_file_path, local_file_path)
        sftp_client.close()

        ssh_client.close()
        file = open(local_file_path, 'rb')
        bot.send_document(chat_id, file)

        bot.send_message(chat_id, f"File downloaded from {remote_file_path} and sent to you successfully.")
    except paramiko.AuthenticationException as auth_error:
        bot.send_message(chat_id, f"Authentication failed: {str(auth_error)}")
    except paramiko.SSHException as ssh_error:
        bot.send_message(chat_id, f"SSH error: {str(ssh_error)}")
    except Exception as e:
        bot.send_message(chat_id, f"Error in download command: {str(e)}")
        print(f"Error in download_file_from_server: {str(e)}")



# def download_file_from_server(chat_id, name, username, ip, password):
#     try:
#         remote_file_path = '/etc/x-ui/x-ui.db'
#         local_file_path = f"{name}_x-ui.db"
#         print(name, username, ip, password)
#         with Connection(host=ip, user=username, connect_kwargs={"password": password}) as conn:
#             conn.get(remote_file_path, local=local_file_path)
#         print("File downloaded successfully")
#         with open(local_file_path, 'rb') as file:
#             bot.send_document(chat_id, file)

#         bot.send_message(chat_id, f"File downloaded from {remote_file_path} and sent to you successfully.")
#     except Exception as e:
#         bot.send_message(chat_id, f"Error in download command: {str(e)}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Welcome! Please provide your information in this format: /add_server Name Username IP Password")

@bot.message_handler(commands=['add_server'])
def process_user_info(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Processing your information...")
    try:
        text = message.text.split(' ', 1)[1]
        name, username, ip, password = text.split()
        save_user_info(name, username, ip, password)
        bot.send_message(chat_id, "Your information has been saved successfully!")
    except (ValueError, IndexError):
        bot.send_message(chat_id, "Please enter your information in the correct format: /add_server Name Username IP Password")

@bot.message_handler(commands=['download'])
def download(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Downloading file from server")
    servers = get_credentials()
    for server in servers:
        name, username, ip, password = server.split('|')
        bot.send_message(chat_id, f"Downloading file from {name}...")
        download_file_from_server(chat_id,name, username,ip, password)
    else:
        bot.send_message(chat_id, "Download process completed for all servers!")

@bot.message_handler(commands=['list_servers'])
def list_servers(message):
    chat_id = message.chat.id
    servers = get_credentials()
    if servers:
        server_list = "\n".join([f"Name: {server.split('|')[2]}, IP: {server.split('|')[0]}" for server in servers])
        bot.send_message(chat_id, f"List of servers:\n\n{server_list}")
    else:
        bot.send_message(chat_id, "No servers found!")
   
@bot.message_handler(commands=['delete_server'])
def delete_server(message):
    chat_id = message.chat.id
    try:
        delete_param = message.text.split(' ', 1)[1].strip()

        servers = get_credentials()
        updated_servers = []
        deleted = False

        for server in servers:
            # Split server details
            server_info = server.split('|')
            name, _, ip, _ = server_info

            if delete_param.lower() != name.lower() and delete_param.lower() != ip.lower():
                updated_servers.append(server)  # Retain servers that are not to be deleted
            else:
                deleted = True

        if deleted:
            with open('user_info.txt', 'w') as file:
                for server in updated_servers:
                    file.write(server)

            bot.send_message(chat_id, f"Server '{delete_param}' deleted successfully!")
        else:
            bot.send_message(chat_id, f"Server '{delete_param}' not found!")

    except IndexError:
        bot.send_message(chat_id, "Please specify a server name or IP to delete.")
     
        
@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    help_text = '''
    Available commands:
    /start - Start the bot
    /add_server Name Username IP Password - Add a new server
    /delete_server Name_or_IP - Delete a server by its name or IP
    /download - Download the file from the server
    /list_servers - View the list of servers
    /help - Show this help message
    '''
    bot.send_message(chat_id, help_text)
    
    
def download_file():
    try:
        servers = get_credentials()
        for server in servers:
            name, username, ip, password = server.split('|')
            print(name, username, ip, password)
            
            download_file_from_server(int("1734062356"), name, username, ip, password)
    except Exception as e:
        print(f"Error in download file in cron job: {str(e)}")
        

def download_and_schedule():
    schedule.every().hour.do(download_file)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_bot():
    print("Bot is running...")
    print("==================================")
    try:
        bot.polling()
    except Exception as e:
        print(f"Error in start bot: {str(e)}")

schedule_thread = threading.Thread(target=download_and_schedule)
schedule_thread.start()

start_bot()