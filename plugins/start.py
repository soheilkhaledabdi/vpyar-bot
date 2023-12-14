from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date
import paramiko
import random
import string


server_host_address = "srv.vpyar.ir"
server_ip_address = "65.109.209.133"
server_username = "root"
server_password = "fpvENVRbAXmELJEJwR4a"

def create_user_on_linux_server(server_ip, ssh_username, ssh_password):
    random_password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=12))

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=server_ip,
                           username=ssh_username, password=ssh_password)

        find_last_user_command = "ls -t /home | grep vpyar | head -1"
        stdin, stdout, stderr = ssh_client.exec_command(find_last_user_command)

        last_user = stdout.read().decode('utf-8').strip()

        if last_user:
            last_user_number = int(last_user.split('_')[-1])
            new_user_number = last_user_number + 1
        else:
            new_user_number = 1

        new_username = f"vpyar_{new_user_number}"
        create_user_command = f"sudo useradd -m {new_username}"
        
        f = open("users.txt", "a").write(f"{new_username}:{random_password}\n")
        
        stdin, stdout, stderr = ssh_client.exec_command(create_user_command)

        set_password_command = f"sudo echo -e '{random_password}\n{random_password}' | sudo passwd {new_username}"
        stdin, stdout, stderr = ssh_client.exec_command(set_password_command)

        set_expire_date_command = f"sudo chage -E {date.today()} {new_username}"
        stdin, stdout, stderr = ssh_client.exec_command(
            set_expire_date_command)

        return new_username, random_password

    except paramiko.AuthenticationException:
        print("Authentication failed, please check your credentials")
    except paramiko.SSHException as ssh_ex:
        print(f"Error occurred while establishing SSH connection: {ssh_ex}")
    finally:
        ssh_client.close()


@Client.on_message(filters.command("start"))
def start(client: Client, message: Message):
    welcome_message = (
        "سلام به ربات ویپی یار خوش اومدی🚀\n\n"
        "اینجا میتونی فیلترشکن رایگان بگیری🏂\n\n@vpyarbo"
    )

    keyboard = [
        [
            InlineKeyboardButton("🔥دریافت اکانت تست",
                                 callback_data="GetTestConfig"),
            InlineKeyboardButton("💥اموزش فعال سازی",
                                 callback_data="activation_guide")
        ],
        [
            InlineKeyboardButton("📣کانال ما", url="https://t.me/vpyar"),
            InlineKeyboardButton("👨‍💻سفارش کافینگ شخصی ", url="https://t.me/vpyar_support")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text(welcome_message, reply_markup=reply_markup)


@Client.on_callback_query()
def callback_handler(client, callback):
    data = callback.data
    message = callback.message
    if data == "GetTestConfig":
        f = open("user_id.txt", "r")
        for line in f.readlines():
            if str(message.chat.id) in line:
                client.send_message(message.chat.id, "شما قبلا اکانت تست گرفته اید")
                return
        open("user_id.txt", "a").write(f"{message.chat.id}\n")
        message.edit_text("در حال ساخت اکانت تست...")
        new_username, new_password = create_user_on_linux_server(
            server_ip_address, server_username, server_password)
        client.send_message(
            message.chat.id, f"هاست : `{server_host_address}`\nنام کاربری: `{new_username}`\nرمز عبور: `{new_password}` \n `پورت : `993` , 995` \n تاریخ انقضا : {date.today()}\n\n@vpyarbot")
        client.send_message(message.chat.id, "اکانتت امادس لذتشو ببر😎"  ,reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💥اموزش فعال سازی", callback_data="activation_guide")
                ],
                [
            InlineKeyboardButton("📣کانال ما", url="https://t.me/vpyar"),
            InlineKeyboardButton("👨‍💻سفارش کافینگ شخصی ", url="https://t.me/vpyar_support")
        ]
            ]
        ))

    elif data == "activation_guide":
        message.edit_text("در حال نمایش اموزش فعال سازی...")
        try:
            # client.send_video(
            #         chat_id=message.chat.id,
            #         video="https://dl.yozcourse.ir/bot/config_in_android.mp4",
            #         caption="آموزش فعال‌سازی روی اندروید"
            #     )
            
            # client.send_document(
            #         chat_id=message.chat.id,
            #         document="https://dl.yozcourse.ir/bot/NapsternetV.apk",
            #         caption="فایل کانفیگ"
            #     )

            client.send_video(
                    chat_id=message.chat.id,
                    video="https://dl.yozcourse.ir/bot/config_in_apple.mp4",
                    caption="آموزش فعال‌سازی روی iOS"
                )
        except Exception as e:
            print(f"Error sending videos: {e}")

        
        keyboard = [
        [
            InlineKeyboardButton("🔥دریافت اکانت تست",
                                 callback_data="GetTestConfig"),
        ],
        [
            InlineKeyboardButton("📣کانال ما", url="https://t.me/vpyar"),
            InlineKeyboardButton("👨‍💻سفارش کافینگ شخصی ", url="https://t.me/vpyar_support")
        ]
        ]
        
        client.send_message(message.chat.id, "اموزش ها رو دیدی کانفیگتو بزنـــــــو حالشو ببر 🚀💥"  ,reply_markup=InlineKeyboardMarkup(keyboard))
        
