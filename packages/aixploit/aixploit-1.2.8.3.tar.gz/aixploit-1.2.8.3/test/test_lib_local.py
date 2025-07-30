import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # Automatically detect the current folder # Adjust this path as necessary

from dotenv import load_dotenv
load_dotenv()


from aixploit.plugins import PromptInjection, Privacy, Integrity, Availability, Abuse
from aixploit.core import run


#target1 = ["Ollama", "http://localhost:11434/v1", "mistral"]
#target2 = ["Openai", "", "gpt-3.5-turbo"]
#target3 = ["Openai", "", "gpt-4o"]
target4 = ["deepseek", os.getenv("DEEPSEEK_URL"), "deepseek-chat"]


attackers = [
    #PromptInjection("quick"),
    #Privacy("quick"),
    Integrity("quick"),
    #Availability("quick"),
    #Abuse("quick"),
    #PromptInjection("full")
    ]


start_time = datetime.now()
print('Redteaming exercise started at : ', start_time.strftime("%H:%M:%S"))  

try:
    conversation, attack_prompts_malicious, success_rates_percentage, total_tokens, total_cost = run(attackers, target4, os.getenv("DEEPSEEK_KEY"))

    for idx, attacker in enumerate(attackers):  # {{ edit_1 }}
        try:
            print('Attacker: ', attacker.__class__.__name__)  
            prompts = conversation[idx]  # Get the conversation for the current attacker
            #print(f'\U0001F4AC Conversation for attacker {idx + 1}: \n {prompts} \n End of conversation')  # {{ edit_1 }}
            print(f' \U00002705  Number of prompts tested for attacker {idx + 1}: {len(prompts)}')  # {{ edit_2 }}
            #
            malicious_prompts = attack_prompts_malicious[idx]
            print(f' \U00002705  Number of successful prompts for attacker {idx + 1}: {len(malicious_prompts)}')
            print(f' \U00002705  Attack success rate for attacker {idx + 1}: {success_rates_percentage[idx] * 100:.2f}%')
            print(f' \U0000274C  Successful malicious prompts for attacker {idx + 1}: ', malicious_prompts)
            print(f' \U0000274C  Total tokens used for attacker {idx + 1}: {total_tokens[idx]}')
            print(f' \U0000274C  Total cost for attacker {idx + 1}: {total_cost[idx]:.2f} USD' )
            print('--------------------------------')
        except:
            print(' ⚠️  No Prompts Found for attacker: ', attacker.__class__.__name__)

# ... existing code ...
except Exception as e:  # {{ edit_1 }}
    print(' ⚠️  Error preventing launch of the attack: ', str(e))  # {{ edit_2 }}
# ... existing code ...
try:
    conversation, attack_prompts_malicious, success_rates_percentage, total_tokens, total_cost = run(attackers, target2, os.getenv("OPENAI_KEY"))

    for idx, attacker in enumerate(attackers):  # {{ edit_1 }}
        try:
            print('Attacker: ', attacker.__class__.__name__)  
            prompts = conversation[idx]  # Get the conversation for the current attacker
            #print(f'\U0001F4AC Conversation for attacker {idx + 1}: \n {prompts} \n End of conversation')  # {{ edit_1 }}
            print(f' \U00002705  Number of prompts tested for attacker {idx + 1}: {len(prompts)}')  # {{ edit_2 }}
            #
            malicious_prompts = attack_prompts_malicious[idx]
            print(f' \U00002705  Number of successful prompts for attacker {idx + 1}: {len(malicious_prompts)}')
            print(f' \U00002705  Attack success rate for attacker {idx + 1}: {success_rates_percentage[idx] * 100:.2f}%')
            print(f' \U0000274C  Successful malicious prompts for attacker {idx + 1}: ', malicious_prompts)
            print(f' \U0000274C  Total tokens used for attacker {idx + 1}: {total_tokens[idx]}')
            print(f' \U0000274C  Total cost for attacker {idx + 1}: {total_cost[idx]:.2f} USD' )
            print('--------------------------------')
        except:
            print(' ⚠️  No Prompts Found for attacker: ', attacker.__class__.__name__)

except Exception as e:  # {{ edit_1 }}
    print(' ⚠️  Error preventing launch of the attack: ', str(e))  # {{ edit_2 }}
# ...

try:
    conversation, attack_prompts_malicious, success_rates_percentage, total_tokens, total_cost = run(attackers, target3, os.getenv("OPENAI_KEY"))

    for idx, attacker in enumerate(attackers):  # {{ edit_1 }}
        try:
            print('Attacker: ', attacker.__class__.__name__)  
            prompts = conversation[idx]  # Get the conversation for the current attacker
            #print(f'\U0001F4AC Conversation for attacker {idx + 1}: \n {prompts} \n End of conversation')  # {{ edit_1 }}
            print(f' \U00002705  Number of prompts tested for attacker {idx + 1}: {len(prompts)}')  # {{ edit_2 }}
            #
            malicious_prompts = attack_prompts_malicious[idx]
            print(f' \U00002705  Number of successful prompts for attacker {idx + 1}: {len(malicious_prompts)}')
            print(f' \U00002705  Attack success rate for attacker {idx + 1}: {success_rates_percentage[idx] * 100:.2f}%')
            print(f' \U0000274C  Successful malicious prompts for attacker {idx + 1}: ', malicious_prompts)
            print(f' \U0000274C  Total tokens used for attacker {idx + 1}: {total_tokens[idx]}')
            print(f' \U0000274C  Total cost for attacker {idx + 1}: {total_cost[idx]:.2f} USD' )
            print('--------------------------------')
        except:
            print(' ⚠️  No Prompts Found for attacker: ', attacker.__class__.__name__)

except Exception as e:  # {{ edit_1 }}
    print(' ⚠️  Error preventing launch of the attack: ', str(e))  # {{ edit_2 }}
# ...

print('Redteaming exercise ended at : ', datetime.now().strftime("%H:%M:%S"))
print('Total time taken: ', datetime.now() - start_time)