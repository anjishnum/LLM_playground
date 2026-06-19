# LLM_playground
Basic command line chatbot

## Insights
- The chatbot is simply a list of messages
- A message is dictionary with 'role' and 'content'
- Choices within the response is a list to accomodate multiple answers from the LLM
- The cli chatbot interface is only a never ending while loop with question from the user appended to the messages at the beginning and response from the LLM appended at the end of the loop
