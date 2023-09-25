#########################################
# Run this chat.py using the belwo command
# python chat.py
#########################################

import openai
import requests

# API end points
fdenquiry_url = 'http://127.0.0.1:8000/fdenquiry/'
fdmaturity_url = 'http://127.0.0.1:8000/fdmaturity/'

# Setup your own OpenAI API key
openai.api_key = "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"

class BankChat(object):
    '''
    This class incorporates the design of whole conversation agent system
    '''
    
    INTENT_DETECTION_SETUP_PROMPT = """Nhiệm vụ của bạn là phân loại mục đích của khách hàng từ `Cuộc trò chuyện` bên dưới giữa nhân viên hỗ trợ và khách hàng thành `Danh mục mục đích sau`. Response should follow the `Output Format`.
    
    Conversation:
    {conversation}

    Intent Categories:
    GREETING: Khách hàng đang chào chatbot.
    FIXED_DEPOSIT_ENQUIRY: Thắc mắc chung của khách hàng về những thông tin chung về dịch vụ của công ty.
    FIXED_DEPOSIT_MATURITY_ENQUIRY: Câu hỏi của khách hàng về những dịch vụ mà công ty đang cung cấp
    OUT_OF_CONTEXT: Truy vấn của khách hàng không liên quan và không thể được phân loại trong ba ý định trên.

    Output Format: <PREDICTED_INTENT>
    """

    FD_ENQUIRY_DETAILS_PROMPT = """Your task is to extract the following `Entities` from the below `Conversation` between an agent and a customer. Response should follow the `Output Format`. If some entities are missing provide NULL in the `Output Format`.

    Conversation:
    {conversation}

    Entities:
    TENOR: This is the tenor of the fixed deposit. Convert it into months if it is in years.
    INVESTMENT_AMOUNT: This is the investment amount the customer might want to invest. Conver to digits if it is in letter form.

    Output Format: {{'TENOR': <Tenor in months and only digits nothig else>, 'INVESTMENT_AMOUNT': <Investment amount only in digits not in letters or other forms>}}
    """

    FD_MATURITY_ENQUIRY_DETAILS_PROMPT = """Your task is to extract the following `Entities` from the below `Conversation` between an agent and a customer. Response should follow the `Output Format`. If some entities are missing provide NULL in the `Output Format`.

    Conversation:
    {conversation}

    Entities:
    CUSTOMER_ID: This is the customer id. Conver to digits if it is in letter form.

    Output Format: {{'CUSTOMER_ID': <Customer ID only in digits not in letters or other forms>}}
    """

    CONVERSATION_PROMPT = """You are a smart conversation agent in the chăm sóc khách hàng. shop là 'hamitaspa'. Bạn hỗ trợ các khách hàng spa hỏi về các dịch vụ của chúng tôi. Nhiệm vụ của bạn là theo dõi luồng hội thoại dưới đây để hỗ trợ khách hàng.

    ###
    Conversation Flow:
    1. Greet the customer
    2. Check if they need any assistance.
    3. Answer their requiests
    4. Greet the customer and end the conversation by responding '[END_OF_CONVERSATION]'
    ###

    Please respond 'OK' if you are clear about you task.
    """

    CONVERSATION_AGREE_PROMPT = """OK"""

    CONVERSATION_START_PROMPT = """Great! Start the Conversation."""

    def intent_detection(self, conversation):
        chat_ml = [
                    {"role": "user", "content": self.INTENT_DETECTION_SETUP_PROMPT.format(conversation=conversation)}
                  ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_ml,
        temperature=0)
        
        return response['choices'][0]['message']['content'].strip(" \n'")
    
    def fd_enquiry_details(self, conversation):
        chat_ml = [
                    {"role": "user", "content": self.FD_ENQUIRY_DETAILS_PROMPT.format(conversation=conversation)}
                  ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_ml,
        temperature=0)
        
        return response['choices'][0]['message']['content'].strip(" \n")
    
    def fd_maturity_enquiry_details(self, conversation):
        chat_ml = [
                    {"role": "user", "content": self.FD_MATURITY_ENQUIRY_DETAILS_PROMPT.format(conversation=conversation)}
                  ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_ml,
        temperature=0)
        
        return response['choices'][0]['message']['content'].strip(" \n")
    
    def conversation_chat(self):
        conversation = "" # Captures the conversation between agent and the customer
        end_flag = False # To end the conversation

        chatml_messages = [
            {"role": "user", "content": self.CONVERSATION_PROMPT},
            {"role": "assistant", "content": self.CONVERSATION_AGREE_PROMPT},
            {"role": "user", "content": self.CONVERSATION_START_PROMPT}
        ]

        while True:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chatml_messages
            )

            agent_response = response['choices'][0]['message']['content'].strip(" \n")

            if "END_OF_CONVERSATION" in agent_response:
                print("Agent: Thank you for connecting with us. Have a nice day!")
                break
            elif end_flag==True:
                print("Agent: {}".format(agent_response))
                print("Agent: Thank you for connecting with us. Have a nice day!")
                break

            print("Agent: {}".format(agent_response))
            chatml_messages.append({"role": "assistant", "content": agent_response})
            conversation += "Agent: {}\n".format(agent_response)

            customer_response = input("Customer: ")
            if customer_response == "/end":
                break
            chatml_messages.append({"role": "user", "content": customer_response})
            conversation += "Customer: {}\n".format(customer_response)

            # Classify the intent
            intent = self.intent_detection(conversation)

            if 'OUT_OF_CONTEXT' in intent:
                chatml_messages.append({"role": "user", "content": "Politey say to customer to stay on the topic not to diverge."})
            elif 'GREETING' in intent:
                chatml_messages.append({"role": "user", "content": "Greet the customer and ask how you can help them."})
            elif 'FIXED_DEPOSIT_ENQUIRY' in intent:
                # Extract the entities
                entities = self.fd_enquiry_details(conversation)
                entities = entities.split(",")
                tenor = entities[0].split(":")[-1].strip(" '}{") # Checking the value of tenor
                invest_amt = entities[1].split(":")[-1].strip(" '}{") # Checking the value of investment amount

                if invest_amt.upper() == "NULL":
                    # Ask for the investment amout
                    chatml_messages.append({"role": "user", "content": "Ask the customer for Investemt Amount"})
                elif tenor.upper() == "NULL":
                    # Ask for the tenor
                    chatml_messages.append({"role": "user", "content": "Ask the customer for Tenor in months"})
                else:
                    # If all the data is present then call the API
                    data = {
                                "amount": float(invest_amt),
                                "tenor": int(tenor)
                           }
                    response = requests.post(fdenquiry_url, json=data)
                    resp_json = response.json()

                    if resp_json["status"] == "SUCCESS":
                        resp_json.pop("status")
                        chatml_messages.append({"role": "user", "content": "Provide the details to the customer as depicted in the below json in natural language, don't put it in the json format to the customer:\n{}".format(str(resp_json))})
                        end_flag = True
                    else:
                        resp_json.pop("status")
                        chatml_messages.append({"role": "user", "content": "Some invalid data is provided by the customer. Provide the details to the customer as depicted in the below json in natural language, don't put it in the json format to the customer:\n{}".format(str(resp_json))})
                        end_flag = True

            elif 'FIXED_DEPOSIT_MATURITY_ENQUIRY' in intent:
                # Extract the entities
                entities = self.fd_maturity_enquiry_details(conversation)
                cust_id = entities.split(":")[-1].strip(" '}{") # Checking the value of customer id

                if cust_id.upper() == "NULL":
                    # Ask for the customer id
                    chatml_messages.append({"role": "user", "content": "Ask the customer for Customer ID"})
                else:
                    # If all the data is present then call the API
                    data = {
                                "account_id": int(cust_id)
                           }
                    response = requests.post(fdmaturity_url, json=data)
                    resp_json = response.json()

                    if resp_json["status"] == "SUCCESS":
                        resp_json.pop("status")
                        chatml_messages.append({"role": "user", "content": "Provide the details to the customer as depicted in the below json in natural language, don't put it in the json format to the customer:\n{}".format(str(resp_json))})
                        end_flag = True
                    else:
                        resp_json.pop("status")
                        chatml_messages.append({"role": "user", "content": "Some invalid data is provided by the customer. Provide the details to the customer as depicted in the below json in natural language, don't put it in the json format to the customer:\n{}".format(str(resp_json))})
                        end_flag = True
            




if __name__ == "__main__":
    BC = BankChat()
    BC.conversation_chat()