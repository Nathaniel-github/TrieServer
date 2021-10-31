import socket
from queue import Queue
from threading import Thread, Event
import ast
from struct import unpack, pack
import pickle
from pathlib import Path

if Path('save_trie.pkl').is_file():
    with open('save_trie.pkl', 'rb') as f:
        trie = pickle.load(f)
else:
    trie = {'size': 0}
q = Queue()
if Path('save_words.pkl').is_file():
    with open('save_words.pkl', 'rb') as f:
        all_words = pickle.load(f)
else:
    all_words = []


def get_new_level() -> dict:
    """Gets a new node that contains a flag for its size

    Returns:
        dict: A dictionary representing an empty node
    """
    return {'size': 0}


def pop_layer_safe(lv: dict, pop_key: str):
    """Pops a child from a layer 'safely' in that it maintains the node's size

    Args:
        lv (dict): The node to pop a child from
        pop_key (str): The key to the child that should be popped
    """
    lv.pop(pop_key)
    lv['size'] -= 1


def full_send(conn: socket.socket, data_: bytes) -> None:
    size_ = pack('>Q', len(data_))
    print(f'Size: {size}')
    conn.sendall(size_)
    conn.sendall(data_)


def get_final_level() -> dict:
    """Gets a node that represents the last character of a word

    Returns:
        dict: A dictionary representing an empty node that also marks the end of a word
    """
    lv = get_new_level()
    lv['end'] = True
    return lv


def add_to_trie(word: str):
    """Adds the given word to the trie

    Args:
        word (str): The word that should be added to the trie
    """
    global all_words
    global trie
    all_words.append(word)
    lv: dict = trie
    length = len(word)
    for k in range(length):
        letter = word[k]
        if not (letter in lv):
            if k != length - 1:
                lv[letter] = get_new_level()
            else:
                lv[letter] = get_final_level()
            lv['size'] += 1
        if k == length - 1:
            lv[letter]['end'] = True
        lv = lv[letter]


def delete_all_trie():
    """Deletes all values from the trie"""
    global trie
    global all_words
    trie = get_new_level()
    all_words = []


def recursive_delete(lv: dict, word: str, length: int, i: int) -> tuple:
    """Recursively iterates the trie and deletes the necessary nodes to delete the given word

    Args:
        lv (dict): The node that is being recursively called to
        word (str): The word that is looking to be deleted
        length (int): The length of the word in order to make operations much more efficient
        i (int): The index of the word being accessed on this call
    Returns:
        tuple: A tuple of booleans with the first being whether or not the node should be popped and the second
        being whether or not the word was found in the trie
    """
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
        if lv['size'] == 0 and lv.get('end') is None:
            return True, True
    return False, answer[1]


def delete_from_trie(word: str) -> bool:
    """Sends a TCP request to the server with a packet containing the desired operation and value to be added

    Args:
        word (str): The word that should be attempted to be deleted
    Returns:
        bool: Whether or not the deletion was successful (failing the delete means it wasn't a word that existed
        in the trie)
    """
    global all_words
    global trie
    index = None
    for i in range(len(all_words)):
        cur_word = all_words[i]
        if cur_word == word:
            index = i
    if index is None:
        return False
    else:
        del all_words[index]
    return recursive_delete(trie, word, len(word), 0)[1]


def search_trie(word: str) -> bool:
    """Searches the trie for a given word and returns whether or not it was something that was put into the trie

    Args:
        word (str): The word to look for in the trie
    Returns:
        bool: Whether or not the given word was found to be placed into the trie
    """
    global trie
    lv = trie
    for letter in word:
        lv = lv.get(letter)
        if lv is None:
            return False
    if lv.get('end'):
        return True
    else:
        return False


def find_words(starting_lv: dict, prefix: str, letters: str = '') -> list:
    """Finds all the words that branch off from a starting level

    Args:
        starting_lv (dict): The level to perform the search on
        prefix (str): The string of characters that you start the search with
        letters (str): The string of characters that are assembled from the starting point to the current point in
        the trie (current point meaning the level that this recursive method is at)
    Returns:
        list: A list that contains all words formed from the given level
    """
    answer = []
    for k, v in starting_lv.items():
        if k != 'end' and k != 'final' and k != 'size':
            answer += find_words(v, prefix + letters + k)
        if k == 'end':
            answer.append(prefix + letters)
    return answer


def autocomplete(prefix: str):
    """Autocompletes from the given prefix given the words in the trie

    Args:
        prefix (str): The prefix to search the trie with
    Returns:
        Any: Either a boolean that states there were no matches for the prefix or a list of matches
    """
    global trie
    lv = trie
    for letter in prefix:
        lv = lv.get(letter)
        if lv is None:
            return False
    return find_words(lv, prefix)


class ClientHandler:
    """A class to encapsulate individual clients and their requests into the queue

    Attributes:
        conn: A socket that represents the connection to the client that made the request
        add: The address of the client that made the request
        packet: The tuple that represents the client's request
    """

    def __init__(self, conn: socket.socket, add, packet: tuple):
        """Initializes the class with the socket, address, and packet"""
        self.conn = conn
        self.add = add
        self.packet = packet

    def execute(self) -> None:
        """Executes the packet this handler was instantiated with"""
        global trie
        global all_words
        if self.packet[0] == 'Add keyword':
            add_to_trie(self.packet[1])
            full_send(self.conn, bytes(f'Successfully added {self.packet[1]}', encoding='utf8'))
        elif self.packet[0] == 'Delete keyword':
            success = delete_from_trie(self.packet[1])
            if success:
                full_send(self.conn, bytes(f'Successfully deleted {self.packet[1]}', encoding='utf8'))
            else:
                full_send(self.conn,
                          bytes(f'Could not delete {self.packet[1]} because it does not exist', encoding='utf8'))
        elif self.packet[0] == 'Delete all':
            delete_all_trie()
            full_send(self.conn, bytes('Deleted all values from the trie', encoding='utf8'))
        elif self.packet[0] == 'Search for keyword':
            answer = search_trie(self.packet[1])
            if not answer:
                full_send(self.conn, bytes(f'The keyword {self.packet[1]} does not exist', encoding='utf8'))
            else:
                full_send(self.conn, bytes(f'The keyword {self.packet[1]} exists', encoding='utf8'))
        elif self.packet[0] == 'Autocomplete by prefix':
            answer = autocomplete(self.packet[1])
            if not answer:
                full_send(self.conn, bytes(f'The prefix {self.packet[1]} does not exist', encoding='utf8'))
            else:
                full_send(self.conn,
                          bytes(f'Words that complete the prefix {self.packet[1]} include {answer}', encoding='utf8'))
        elif self.packet[0] == 'Display trie fast':
            full_send(self.conn, bytes(str(all_words), encoding='utf8'))
        else:
            full_send(self.conn, bytes(str(find_words(trie, '')), encoding='utf8'))


class AutoSaver(Thread):
    """A class to automatically save the state of the trie and words stored in it

    Attributes:
        interval: The amount of time between triggers
        ev: An event object to wait on
    """

    def __init__(self, interval: int = 60):
        """Initializes the class with the interval and event object"""
        Thread.__init__(self)
        self.interval = interval
        self.ev = Event()

    def run(self):
        """Starts the saving loop once the thread is initialized"""
        while not self.ev.wait(self.interval):
            print('Saving objects')
            with open('save_trie.pkl', 'wb') as file:
                pickle.dump(trie, file)
            with open('save_words.pkl', 'wb') as file:
                pickle.dump(all_words, file)
            print('Objects saved!')


def queue_reader(queue: Queue) -> None:
    """Constantly reads from the queue

    Args:
        queue (Queue): The queue to be read from
    """
    global trie
    while True:
        packet: ClientHandler = queue.get()
        try:
            packet.execute()
            print(f"State of trie: {trie}")
        except Exception as ex:
            print(ex)
            full_send(packet.conn, bytes(f'An error occurred: {ex}', encoding='utf8'))


if __name__ == '__main__':

    IP = ''
    PORT = 61135

    Thread(target=queue_reader, args=(q,)).start()
    AutoSaver().start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((IP, PORT))
        s.listen()
        print(s.getsockname())
        while True:
            connection, address = s.accept()
            try:
                print('Connected by', address)
                (size,) = unpack('>Q', connection.recv(8))
                data = b''
                while len(data) < size:
                    left = size - len(data)
                    data += connection.recv(1024 if left > 1024 else left + 5)
                data = ast.literal_eval(data.decode(encoding='utf8'))
                q.put(ClientHandler(connection, address, data))
                print(f"Added {data} to queue")
            except Exception as e:
                print(e)
                full_send(connection, bytes(f'An error occurred: {e}', encoding='utf8'))
