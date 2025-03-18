import json
from openai import OpenAI

class GenerativeSchedulingModule():
    def __init__(self):
        f = open('./state_data/open_ai_token.json')
        self.api_token = json.load(f)['goal_requestor_token']
        
    def query(self, goal):
        prompt = """" You are an expert assistant specializing in scheduling events for your clients.
        You will be given a json consisting of your client's schedule where each entry in the json is a time block where they are busy.
        You will also be given the client's goal and a date for when they wish to accomplish their goal.
        Your job is to break their goal down to individual subtasks that will help them accomplish their goal and schedule these subtasks by returning a JSON.
        The scheduling of these tasks should match with the current user profile. 
        For example if given: {events: [{start: ENTER HERE, end: ENTER HERE},]} you must not schedule events which take place in between the start and end for each event in events.
        """
        client = OpenAI(
            api_key=self.api_token
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
              {"role": "user", "content": prompt}
            ]
        )

        print(completion.choices[0].message)

    
    def main(self):
        pass
        

if __name__ == "__main__":
    module = GenerativeSchedulingModule()
    module.main()
