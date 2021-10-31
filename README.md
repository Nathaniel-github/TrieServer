<div id="top"></div>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://raw.githubusercontent.com/Nathaniel-github/TrieServer/main/imgs/trie.png">
    <img src="https://raw.githubusercontent.com/Nathaniel-github/TrieServer/main/imgs/trie.png" alt="Logo" width="200" height="200">
  </a>

<h3 align="center">Trie Server</h3>

  <p align="center">
    The server code for my globally hosted trie through GCP
    <br />
    <a href="https://trieserver.readthedocs.io/en/latest/index.html"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://pypi.org/project/trie-nathaniel/">View on PyPi</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


<!-- GETTING STARTED -->
## Getting Started

To setup your own version of this server, merely clone the project and run the `trie_server.py` file

### Prerequisites

Requires python>=3.6 and pip
  ```sh
sudo apt-get update
sudo apt-get install python3.6
  ```



<!-- USAGE EXAMPLES -->
## Usage

To run the server on a vm without any interruptions you can use no hold up:
```
nohup python3 trie_server.py &
```
disecting the statement a little bit we have `nohup` which tells the shell we are running the no hold up command in order to allow the process to run in the background and also gives a nice `nohup.out` file that stores output from the command as it was being run. Next is `python3` which is the command to start the python interpreter followed by `trie_server.py` which is the python file that is being fed to the interpreter. Lastly there is `&` which tells the shell to run this process in the background and assign a process number to it which can be used to later kill the process with `kill {process_num}` where `{process_num}` is the number given earlier.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Best README](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Nathaniel-github/TrieServer.svg?style=for-the-badge
[contributors-url]: https://github.com/Nathaniel-github/TrieServer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Nathaniel-github/TrieServer.svg?style=for-the-badge
[forks-url]: https://github.com/Nathaniel-github/TrieServer/network/members
[stars-shield]: https://img.shields.io/github/stars/Nathaniel-github/TrieServer.svg?style=for-the-badge
[stars-url]: https://github.com/Nathaniel-github/TrieServer/stargazers
[issues-shield]: https://img.shields.io/github/issues/Nathaniel-github/TrieServer.svg?style=for-the-badge
[issues-url]: https://github.com/Nathaniel-github/TrieServer/issues
[license-shield]: https://img.shields.io/github/license/Nathaniel-github/TrieServer.svg?style=for-the-badge
[license-url]: https://github.com/Nathaniel-github/TrieServer/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/nathaniel-thomas-profile