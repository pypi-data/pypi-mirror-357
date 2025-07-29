# python-simplex-bot documentation

# !!! WARNING !!!
# Docs are in early stage! Documentation will be here by the 0.1.0 release

## Bot class

[`simplex_bot.Bot`](./Bot) handles connection to simplex-chat CLI and is used to build bot application

## Updates

[Updates](./Updates) are objects that contain various event data and are received by your handlers

## BaseContext

[`simplex_bot.types.BaseContext`](./BaseContext) is a context object that contains `Bot` instance, dialog state, and can be used to quickly deal with incoming messages (reply, delete etc.)

## State management

[State management](./StateManagement) document describes how to store dialog state and build a state machine

## Type reference

See [types](./types/README) for detailed reference of all underlying types