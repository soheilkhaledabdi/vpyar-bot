from fabric import Connection

def download_file_from_server(name, username, ip, password):
    try:
        remote_file_path = '/etc/x-ui/x-ui.db'
        local_file_path = f"{name}_x-ui.db"
        print(name, username, ip, password)
        with Connection(host=ip, user=username, connect_kwargs={"password": password}) as conn:
            conn.get(remote_file_path, local=local_file_path)
        print("File downloaded successfully")
    except Exception as e:
        print(e)
        
        
download_file_from_server("soheil","91.107.251.57","root","uURNjtwLsjxLVJWMthWM")