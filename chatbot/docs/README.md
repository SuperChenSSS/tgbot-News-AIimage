# Table of Contents

* [ChatGPT\_HKBU](#ChatGPT_HKBU)
  * [HKBU\_ChatGPT](#ChatGPT_HKBU.HKBU_ChatGPT)
    * [submit](#ChatGPT_HKBU.HKBU_ChatGPT.submit)
* [chatbot](#chatbot)
  * [echo](#chatbot.echo)
  * [help\_command](#chatbot.help_command)
  * [hello](#chatbot.hello)
  * [add](#chatbot.add)
  * [delete](#chatbot.delete)
  * [set](#chatbot.set)
  * [get](#chatbot.get)

<a id="ChatGPT_HKBU"></a>

# ChatGPT\_HKBU

<a id="ChatGPT_HKBU.HKBU_ChatGPT"></a>

## HKBU\_ChatGPT Objects

```python
class HKBU_ChatGPT()
```

A class for interacting with the HKBU ChatGPT service.

**Methods**:

- `submit(message)` - Submits a message to the HKBU ChatGPT service and returns the response.

<a id="ChatGPT_HKBU.HKBU_ChatGPT.submit"></a>

#### submit

```python
def submit(message)
```

Submit a message to the HKBU ChatGPT service and get a response.

**Arguments**:

- `message` (`str`): The message to send to the ChatGPT service.

**Returns**:

`str`: The response from the ChatGPT service, or an error message.

<a id="chatbot"></a>

# chatbot

<a id="chatbot.echo"></a>

#### echo

```python
def echo(update, context)
```

Echo the user message in lowercase.

:param: args[0] as message
:return: lowercase of the message
:rtype: send_message


<a id="chatbot.help_command"></a>

#### help\_command

```python
def help_command(update: Update, context: CallbackContext) -> None
```

A placeholder when the command /help is issued.

<a id="chatbot.hello"></a>

#### hello

```python
def hello(update: Update, context: CallbackContext) -> None
```

Greetings with hello with /hello <keyword>.

:param: None
:return context: Good day, <keyword>!


<a id="chatbot.add"></a>

#### add

```python
def add(update: Update, context: CallbackContext) -> None
```

Add a message to DB when the command /add is issued.

:param: args[0] as the keyword
:return: You have said args[0] for <value> times.
:rtype: reply_text


<a id="chatbot.delete"></a>

#### delete

```python
def delete(update: Update, context: CallbackContext) -> None
```

Delete a message when the command /delete is issued.

:param: args[0] as the keyword
:return: You have deleted <keyword>.
:rtype: reply_text


<a id="chatbot.set"></a>

#### set

```python
def set(update: Update, context: CallbackContext) -> None
```

Set args[0] to args[1] when the command /set is issued.

:param: args[0] as the keyword to be changed, args[1] as the new keyword
:return: args[0] changed to args[1]
:rtype: reply_text


<a id="chatbot.get"></a>

#### get

```python
def get(update: Update, context: CallbackContext) -> None
```

Get the number of occurence with keyword: args[0] when the command /get is issued.

:param: args[0] as the keyword
:return: Number of occurence of the keyword.
:rtype: reply_text


