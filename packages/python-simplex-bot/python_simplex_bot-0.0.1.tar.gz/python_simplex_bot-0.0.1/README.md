# python-simplex-bot

A high-level python library for building bots for [simplex chat](https://simplex.chat)

Currently supported `simplex-chat` version: **6.3.6.0**

## Installation

`pip install python-simplex-bot`

Alternatively, clone this repository into a desired location

## Usage

### Creating your first bot

1. Install [simplex-chat terminal client](https://github.com/simplex-chat/simplex-chat/tree/stable?tab=readme-ov-file#zap-quick-installation-of-a-terminal-app)
2. Start client using `simplex-chat -p 5225 -d my-bot-name`
3. If running for the first time, answer the initial questions e.g. username (this will be your bot's name as users see it)
4. Save this code as `bot.py`:
   ```python
   from simplex_bot import Bot
   from sumplex_bot.types import UpdateNewContact, UpdateTextMessage, BaseContext

   # 5225 is the port number you passed to the -p argument in step 2:
   bot = Bot(url="ws://localhost:5225")

   @bot.hello_handler
   async def hello_handler(update: UpdateNewContact, context: BaseContext):
       await context.reply(f"Hello, {update.peer.user.username}!")
   
   @bot.text_handler
   async def echo_handler(update: UpdateTextMessage, context: BaseContext):
       await context.reply(f"You said: {update.text})
   
   bot.start()
   ```
5. Run your bot with `python3 bot.py`
6. Bot will print its address into the terminal output. Insert this address into your favourite simplex chat client application to connect to your bot.

### Example bots

Love to learn by example? See [./examples/](./examples/README) directory for some self-explanatory examples

### Documentation

See [./docs/README.md](./docs/README) for detailed documentation and reference.

PyDoc is also available; access it from your IDE, pydoc server or python console e.g.:
```python
>>> import simplex_bot
>>> help(simplex_bot)
```

## Roadmap

### v0.1 milestone:
- [x] Automatically message a new contact
- [x] Send and receive text messages
- [ ] Send and receive multimedia messages
- [ ] File transfers
- [ ] Edit and delete messages
- [ ] Message statuses (mark as read/fire when user has read)
- [ ] Reply to messages

### v0.2 milestone:
- [ ] Group chat operations
      - [ ] Create one-time group invite link
      - [ ] User joined/user left events
      - [ ] Mute/unmute
      - [ ] Kick user from group
      - [ ] Manage group chat preferences

### v0.3 milestone:
- [ ] Dialog state management using the `context` object

### v0.4 milestone:
- [ ] Profile management
      - [ ] Set username and profile photo
      - [ ] Generate one-time links
- [ ] Multi user support (run multiple bots using single websocket connection)
- [ ] List connected users and groups

## Contacts

For bug reports and feature requests, use Issues.

## Donations

Toss a coin to your developer, o Valley of Plenty

- Bitcoin: ``
- Bitcoin Cash: ``
- Litecoin: ``
- Ethereum/ERC-20: ``
- Tron/TRC-20: ``
- Solana: ``
- Monero: ``