package main

import (
	"gopkg.in/telegram-bot-api.v4"
	"log"
	"os"
	"strings"
	"time"
	"golang.org/x/crypto/ssh"
)

const (
	token = "6495534406:AAHLkl9FJQdw42c8h0-ACs7AsgF3MVwM1L8"
)

func saveUserInfo(name, username, ip, password string) {
	file, err := os.OpenFile("user_info.txt", os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		log.Fatalf("Error opening file: %s", err)
	}
	defer file.Close()

	if _, err := file.WriteString(name + "|" + username + "|" + ip + "|" + password + "\n"); err != nil {
		log.Fatalf("Error writing to file: %s", err)
	}
}

func getCredentials() []string {
	file, err := os.Open("user_info.txt")
	if err != nil {
		log.Fatalf("Error opening file: %s", err)
	}
	defer file.Close()

	var lines []string
	buf := make([]byte, 1024)
	for {
		n, err := file.Read(buf)
		if n == 0 || err != nil {
			break
		}
		lines = append(lines, string(buf[:n]))
	}
	return lines
}

func downloadFileFromServer(bot *tgbotapi.BotAPI, chatID int64, name, username, ip, password string) {
	config := &ssh.ClientConfig{
		User: username,
		Auth: []ssh.AuthMethod{
			ssh.Password(password),
		},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(), // Change this to implement proper host key validation
	}

	conn, err := ssh.Dial("tcp", ip+":22", config)
	if err != nil {
		bot.Send(tgbotapi.NewMessage(chatID, "Failed to connect to the server"))
		log.Fatalf("Failed to connect to the server: %s", err)
		return
	}
	defer conn.Close()

	session, err := conn.NewSession()
	if err != nil {
		bot.Send(tgbotapi.NewMessage(chatID, "Failed to create session"))
		log.Fatalf("Failed to create session: %s", err)
		return
	}
	defer session.Close()

	remoteFilePath := "/etc/x-ui/x-ui.db"
	localFilePath := name + "_x-ui.db"

	// Download file from remote server
	err = scp(session, remoteFilePath, localFilePath)
	if err != nil {
		bot.Send(tgbotapi.NewMessage(chatID, "Failed to download the file"))
		log.Fatalf("Failed to download the file: %s", err)
		return
	}

	// Read the downloaded file content
	fileContent, err := os.ReadFile(localFilePath)
	if err != nil {
		bot.Send(tgbotapi.NewMessage(chatID, "Failed to read the downloaded file"))
		log.Fatalf("Failed to read the downloaded file: %s", err)
		return
	}

	// Send the downloaded file using Telegram bot
	msg := tgbotapi.NewDocumentUpload(chatID, tgbotapi.FileBytes{Name: localFilePath, Bytes: fileContent})
	bot.Send(msg)
	bot.Send(tgbotapi.NewMessage(chatID, "File downloaded and sent successfully"))
}


func scp(session *ssh.Session, remoteFilePath, localFilePath string) error {
    // Prepare the SCP command to download a file from the remote server
    cmd := "scp -f " + remoteFilePath

    // Start the SCP process on the remote server
    scpOut, err := session.StdoutPipe()
    if err != nil {
        return err
    }

    scpIn, err := session.StdinPipe()
    if err != nil {
        return err
    }

    if err := session.Start(cmd); err != nil {
        return err
    }

    // Read the response from SCP output
    buf := make([]byte, 4096)
    _, err = scpOut.Read(buf)
    if err != nil {
        return err
    }

    // Write the confirmation to SCP input to start the file transfer
    scpIn.Write([]byte("\x00"))

    // Read the file content from SCP output and write it to the local file
    fileContent := make([]byte, 0)
    for {
        n, err := scpOut.Read(buf)
        if err != nil {
            break
        }
        fileContent = append(fileContent, buf[:n]...)
    }

    // Write the downloaded content to the local file
    if err := os.WriteFile(localFilePath, fileContent, 0644); err != nil {
        return err
    }

    return nil
}



func handleMessage(bot *tgbotapi.BotAPI, update tgbotapi.Update) {
	chatID := update.Message.Chat.ID
	text := update.Message.Text

	switch {
	case strings.HasPrefix(text, "/start"):
		bot.Send(tgbotapi.NewMessage(chatID, "Welcome! Please provide your information in this format: /add_server Name Username IP Password"))

	case strings.HasPrefix(text, "/add_server"):
		bot.Send(tgbotapi.NewMessage(chatID, "Processing your information..."))
		args := strings.Fields(text)
		if len(args) != 5 {
			bot.Send(tgbotapi.NewMessage(chatID, "Please enter your information in the correct format: /add_server Name Username IP Password"))
			return
		}
		name, username, ip, password := args[1], args[2], args[3], args[4]
		saveUserInfo(name, username, ip, password)
		bot.Send(tgbotapi.NewMessage(chatID, "Your information has been saved successfully!"))

	case strings.HasPrefix(text, "/download"):
		bot.Send(tgbotapi.NewMessage(chatID, "Downloading file from servers..."))
		servers := getCredentials()
		for _, server := range servers {
			fields := strings.Split(server, "|")
			name, username, ip, password := fields[0], fields[1], fields[2], fields[3]
			bot.Send(tgbotapi.NewMessage(chatID, "Downloading file from "+name+"..."))
			downloadFileFromServer(bot, chatID, name, username, ip, password)
		}
		bot.Send(tgbotapi.NewMessage(chatID, "Download process completed for all servers!"))

	case strings.HasPrefix(text, "/list_servers"):
		servers := getCredentials()
		if len(servers) > 0 {
			var serverList strings.Builder
			for _, server := range servers {
				fields := strings.Split(server, "|")
				serverList.WriteString("Name: " + fields[0] + ", IP: " + fields[2] + "\n")
			}
			bot.Send(tgbotapi.NewMessage(chatID, "List of servers:\n\n"+serverList.String()))
		} else {
			bot.Send(tgbotapi.NewMessage(chatID, "No servers found!"))
		}

	case strings.HasPrefix(text, "/help"):
		helpText := `
		Available commands:
		/start - Start the bot
		/add_server Name Username IP Password - Add a new server
		/download - Download the file from the server
		/list_servers - View the list of servers
		/help - Show this help message
		`
		bot.Send(tgbotapi.NewMessage(chatID, helpText))
	}
}

func main() {
	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Fatalf("Error initializing bot: %s", err)
	}

	bot.Debug = true
	log.Printf("Authorized on account %s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates, err := bot.GetUpdatesChan(u)
	if err != nil {
		log.Fatalf("Error getting update channel: %s", err)
	}

	for update := range updates {
		if update.Message == nil {
			continue
		}

		go handleMessage(bot, update)
	}

	// Run a periodic function every hour to download files from servers
	go func() {
		for {
			servers := getCredentials()
			for _, server := range servers {
				fields := strings.Split(server, "|")
				name, username, ip, password := fields[0], fields[1], fields[2], fields[3]
				// Download file from server using downloadFileFromServer function
				downloadFileFromServer(bot, int64(123456789), name, username, ip, password)
			}
			time.Sleep(time.Hour) // Change the duration as needed
		}
	}()

	select {}
}
