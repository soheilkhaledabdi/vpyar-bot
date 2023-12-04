from datetime import date

today = date.today()
f = open("users.txt", "a")
f.write(today + "\n")
f.close()
print("Today's date:", today)