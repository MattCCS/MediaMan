
import concurrent.futures


def exists(clients, file_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(client.exists, file_id) for client in clients]
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result() is True:
                    return True
            except Exception as exc:
                print(type(exc))
        return False
