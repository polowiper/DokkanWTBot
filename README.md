# Ludicolo

Ludicolo is an open source discord bot that fetches data from the game Dokkan Battle and generates user data out of it

## Installation
First make sure you have [python](https://www.python.org/) installed.
 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install -r dependencies.txt
```

## Usage
To use Ludicolo you will need to update the `BOT_TOKEN` and the `API_TOKEN` in the `config.py` file.

(Note: The api used is from [T6](https://x.com/ThievingSix) so you don't have access to it. If you want to run this bot yourself, please refer to:
- The old version of the bot [93ed7cb](https://github.com/polowiper/DokkanWTBot/tree/93ed7cb861b597861e4e5a84bafe06bd6dae0540).
- The [dokkan-bot](https://github.com/polowiper/dokkan-bot-adapted) to fetch the data out of the game yourself.

Once everything is setup you will need to run 2 processes.
```bash
python fetch_and_save.py
```

```bash
python main.py
```
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Credits
Special thanks to 
- [T6](https://x.com/ThievingSix): For the help on dokkan's api and for providing one of the api used.
- [Darkruss](https://x.com/Darkruss47): For making a good looking ui and making the overall bot pleasing to use.
## License

[MIT](https://choosealicense.com/licenses/mit/)
