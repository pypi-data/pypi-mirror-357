# Parser bot

## Configuring

1. Copy `.env.example` to `.env`
2. Edit `.env` and set values you want

## Running

```bash
pip install -r requirements.txt
python3 parser_bot.py
```

## Operation manual:

At any time, 

1. Authenticating in a bot:
   `/a PASSWORD` - authenticate current user as a bot admin

2. Configuring channels:
   Channels are chats the bot forwards messages to
   - `/chats`: show list of available chats
   - `/channels`: show list of configured channels
   - `/channel add CHANNEL_ID CHAT_ID`: add chat CHAT_ID as channel CHANNEL_ID
   - `/channel add CHANNEL_ID`: add current chat as CHANNEL_ID
   - `/channel del CHANNEL_ID`: delete channel (does not delete chat)

2. Adding parser bot to a group chat;
   `/join SIMPLEX_LINK`: join a chat.
   - In case it's a group chat: join right away
   - In case it's directory bot: forward messages (so you can solve captcha)
   Respond to forwarded messages to make bot reply in the chat the message was forwarded from.

   Use `/leave CHAT_ID` to leave any chat at any time. The chat, contact, respective sources and channels will be deleted

3. Configuring sources:
   Sources are chats bots looks for messages in:
   - `/chats`: see above
   - `/sources`: show list of configured sources
   - `/source add SOURCE_ID CHAT_ID`: add chat CHAT_ID as source SOURCE_ID
   - `/source del SOURCE_ID`: delete SOURCE_ID

4. Configuring message filters:
   - `/filters`: show all filters
   - `/filter add TYPE ARGS... action ACTION ARGS...`: add a filter
     + TYPE ARGS... can be a mix of:
       - `[src SOURCE_ID]`: filter messages from SOURCE_ID
       - `[text some text]`: filter messages containing "some text"
       - `[re regexp]`: filter messages by regular expression r"regexp"
       - `[image]`, `[audio]`, `[file]`: message should contain an image/audio/file
       - `[or FLT1 FLT2 ...]`: message should match FLT1 or FLT2 
     + ACTION ARGS... can be a mix of:
       - `[text_replace "SEARCH" "REPLACE"]`; replace SEARCH with REPLACE
       - `[re_replace "SEARCH PATTERN" "REPLACE EXPRESSION"]`: replace SEARCH PATTERN with REPLACE EXPRESSION. 
       - `[run CUSTOM_FN]`: run a custom user-defined function
       - `[forward CHANNEL_ID]`: forward a filtered message to CHANNEL_ID
   - `/filter del FILTER_ID`: completely remove a filter
   - `/filter enable FILTER_ID`: enable a filter
   - `/filter disable FILTER_ID`: disable a filter
   - `/filter edit FILTER_ID TYPE ARGS... action ACTION ARGS...`: edit a filter

   You can chain multiple filter types like this:
   `/filter add [image][or [text job] [text offer] [text recruit]] action [run capitalize][run save_to_db][forward job_offers]`
   Explanation:
   1. No src filter - look for messages from all sources;
   2. message should have an image and "job", "offer" or "recruit" in its body;
   3. when found,
      1. run custom user method "capitalize",
      2. then run custom user method "save_to_db",
      3. then forward message to channel which CHANNEL_ID is "job_offers"

