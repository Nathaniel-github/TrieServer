import socket
from queue import Queue
from threading import Thread
import ast


def get_new_level() -> dict:
    return {'size': 0}


def pop_layer_safe(lv: dict, pop_key: str):
    lv.pop(pop_key)
    lv['size'] -= 1


def get_final_level() -> dict:
    lv = get_new_level()
    lv['end'] = True
    return lv


def add_to_trie(word: str):
    all_words.append(word)
    lv = trie
    length = len(word)
    for k in range(length):
        letter = word[k]
        if not (letter in lv):
            if k != length-1:
                lv[letter] = get_new_level()
            else:
                lv[letter] = get_final_level()
            lv['size'] += 1
        if k == length-1:
            lv[letter]['end'] = True
        lv = lv[letter]


def recursive_delete(lv: dict, word: str, length: int, i: int) -> tuple:
    if i == length:
        if lv['size'] == 0 and lv.get('end'):
            return True, True
        elif lv.get('end') is not None:
            return False, True
        else:
            return False, False

    next_lv = lv.get(word[i])
    if next_lv is None:
        return False, False

    answer = recursive_delete(next_lv, word, length, i + 1)
    if answer[0]:
        pop_layer_safe(lv, word[i])
        if lv['size'] == 0:
            return True, True
    return False, answer[1]


def delete_from_trie(word: str) -> bool:
    return recursive_delete(trie, word, len(word), 0)[1]


def search_trie(word: str) -> bool:
    lv = trie
    for letter in word:
        lv = lv.get(letter)
        if lv is None:
            return False
    if lv.get('end'):
        return True
    else:
        return False


def find_words(starting_lv: dict, prefix: str, letters: str = '', ) -> list:
    answer = []
    for k, v in starting_lv.items():
        if k != 'end' and k != 'final' and k != 'size':
            answer += find_words(v, prefix + letters + k)
        if k == 'end':
            answer.append(prefix + letters)
    return answer


def autocomplete(prefix: str):
    lv = trie
    for letter in prefix:
        lv = lv.get(letter)
        if lv is None:
            return False
    return find_words(lv, prefix)


class ClientHandler:
    def __init__(self, conn: socket.socket, add, packet):
        self.conn = conn
        self.add = add
        self.packet = packet

    def execute(self):
        if self.packet[0] == 'Add keyword':
            add_to_trie(self.packet[1])
            self.conn.sendall(bytes(f'Successfully added {self.packet[1]}', encoding='utf8'))
        elif self.packet[0] == 'Delete keyword':
            success = delete_from_trie(self.packet[1])
            if success:
                self.conn.sendall(bytes(f'Successfully deleted {self.packet[1]}', encoding='utf8'))
            else:
                self.conn.sendall(bytes(f'Could not delete {self.packet[1]} because it does not exist', encoding='utf8'))
        elif self.packet[0] == 'Search for keyword':
            answer = search_trie(self.packet[1])
            if not answer:
                self.conn.sendall(bytes(f'The keyword {self.packet[1]} does not exist', encoding='utf8'))
            else:
                self.conn.sendall(bytes(f'The keyword {self.packet[1]} exists', encoding='utf8'))
        elif self.packet[0] == 'Autocomplete by prefix':
            answer = autocomplete(self.packet[1])
            if not answer:
                self.conn.sendall(bytes(f'The prefix {self.packet[1]} does not exist', encoding='utf8'))
            else:
                self.conn.sendall(bytes(f'Words that complete the prefix {self.packet[1]} include {answer}', encoding='utf8'))
        elif self.packet[0] == 'Display trie fast':
            self.conn.sendall(bytes(str(all_words), encoding='utf8'))
        else:
            self.conn.sendall(bytes(str(find_words(trie, '')), encoding='utf8'))


def queue_reader(queue: Queue):
    while True:
        queue.get().execute()
        print(f"State of trie: {trie}")


if __name__ == '__main__':

    trie = get_new_level()
    q = Queue()
    IP = ''
    PORT = 61135
    all_words = []

    Thread(target=queue_reader, args=(q,)).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((IP, PORT))
        s.listen()
        print(s.getsockname())
        while True:
            connection, address = s.accept()
            print('Connected by', address)
            data = ast.literal_eval(connection.recv(1024).decode('utf8'))
            q.put(ClientHandler(connection, address, data))
            print(f"Added {data} to queue")
