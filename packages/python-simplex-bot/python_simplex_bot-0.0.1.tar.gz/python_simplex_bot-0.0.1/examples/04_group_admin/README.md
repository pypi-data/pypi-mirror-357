# Example group admin bot

Add this bot to your group chat.

The bot operates in two modes:

1. Group member (admin):
   1. accepts group connection requests (users don't have to wait for you to approve group join request while the bot is online)
   2. Bad words list: delete any messages containing bad words
   3. Ban words list: kick users for sending messages containing ban words
2. Private chat:
   1. For admin:
      - /help - get command help
      - /stats - get statistics
      - /badwords - get list of bad words
      - /badwords add WORD - add a word to badwords list
      - /badwords padd EXPRESSION - add a regular expression to badwords list
      - /banwords - get list of ban words
      - /banwords add WORD - add a word to banwords list
      - /banwords padd EXPRESSION - add a regular expression to banwords list
      - /banmode - get current ban mode (KICK or MUTE)
      - /banmode kick - set ban mode to KICK
      - /banmode mute - set ban mode to MUTE
      - /ban list - show banned users
      - /unban USER_ID - lift ban (unmute or send new invite link if kicked)
   2. For non-admin:
      - User is prompted to solve a captcha. Once the user has solved the captcha, add him to the group chat
      - /a PASSWORD - authenticate as admin

