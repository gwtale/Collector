from slacker import Slacker

#https://hooks.slack.com/services/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 
slack = Slacker('wRDEqqfmlOHXBJcoDTM147x1')

# Send a message to #general channel
#slack.chat.post_message('#general', 'Hello fellow slackers!')

# Get users list
response = slack.users.list()
users = response.body['members']

print users

# Upload a file
#slack.files.upload('hello.txt')