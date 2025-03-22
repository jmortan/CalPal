import json
from openai import OpenAI
from datetime import datetime
from open_ai_client import OpenAiClient
from tzlocal import get_localzone


class GenerativeSchedulingModule():
    def __init__(self, client):
        self.client = client


    def process_user_goal(self, user_message, user_calendar):
        goal = user_message
        goals = self.generate_goals(goal)
        print(f"Generated goals: {goals}", flush=True)
        scheduled_goals=self.schedule_goals(goals, user_calendar, user_message)
        print(f"Generated schedule: {scheduled_goals}", flush=True)
        return scheduled_goals
    

    def generate_goals(self, user_message):
        response = self.client.chat.completions.create(
			model="gpt-4o",
			messages=[
				{
					"role": "system",
					"content": [
						{
							"type": "text",
							"text": (
								"You are an expert assistant specializing in helping your clients achieve their goal. " +
								"Given their goal you will create a training plan consisting of smaller goals to get there.  " +
								"You will also be given the client's goal and optionally the date they want to accomplish their goal on. \n" +
								"Your job is to break their goal down into a plan consisting of an appropriate amount of detailed individual " +
								"smaller goals that they can accomplish in a day which will help them accomplish their larger goal. " + 
								"These sub goals should be specific and detailed and be relevant to the context of the goal and be a task they can accomplish in a day. \n"+
								"You will return a list of these subgoals where each goal corresponds to a day. " +
								"The goal name should be in goal_name and the description in goal_description. " +
								"Please limit the goal_description to 60 characters. " +
								"Each goal should correspond to an individual task they can accomplish."
							)
						}
					]
				},
				{
					"role": "user",
					"content": [
						{
							"type": "text",
							"text": user_message
						}
					]
				},
          	],
			response_format={
				"type": "json_schema",
				"json_schema": {
					"name": "goal_list",
					"strict": True,
					"schema": {
						"type": "object",
						"properties": {
							"goals": {
								"type": "array",
								"description": "A list of goals.",
								"items": {
									"type": "object",
									"properties": {
									"goal_name": {
										"type": "string",
										"description": "The name of the goal."
									},
									"goal_description": {
										"type": "string",
										"description": "A description of what the goal entails."
									}
									},
									"required": [
										"goal_name",
										"goal_description"
									],
									"additionalProperties": False
								}
							}
						},
						"required": [
							"goals"
						],
						"additionalProperties": False
					}
				}
			},
			temperature=0,
			max_completion_tokens=6000,
			top_p=1,
			frequency_penalty=0,
			presence_penalty=0,
			store=False
        )

        return response.choices[0].message.content

    def schedule_goals(self, gpt_goals, user_calendar, user_message):
        start_date = datetime.now(get_localzone()).isoformat()
        response = self.client.chat.completions.create(
			model="gpt-4o",
			messages=[
				{
					"role": "system",
					"content": [
						{
							"type": "text",
							"text": (
								"You are an expert assistant specializing in scheduling events your client wants to put on their calendar. " +
								"You will receive a list of events with event name and event description, " +
								"your client's current calendar containing a list of events they have scheduled with starting and ending times in RFC 3339 format, "+
								"and a message from them providing additional context for when to schedule the events. " +
								f"Your job is to schedule the new events during free times starting on {start_date} and ending on their desired date if an ending date is provided in the freetext user message. " +
								"The time the events take up should be estimated by you given the event name and event description. " +
								"The events should be scheduled evenly spaced out as your client's schedule allows. \n" +
								"event_name should contain the goal_name passed in to you\n" +
								"event_description should contain the goal_description passed in to you \n" +
								"event_start should contain the start time of the event in RFC 3339 format\n" +
								"event_end should contain the end time of the event in RFC 3339 format"
							)
						},
						{
							"type": "text",
							"text": gpt_goals
						},
						{
							"type": "text",
							"text": user_calendar
						},
					]
				},
				{
					"role": "user",
					"content": [
						{
							"type": "text",
							"text": user_message
						}
					]
				},
			],
			response_format={
				"type": "json_schema",
				"json_schema": {
				"name": "event_list",
				"strict": True,
					"schema": {
						"type": "object",
						"properties": {
							"events": {
								"type": "array",
								"description": "A list of events.",
								"items": {
									"type": "object",
									"properties": {
										"event_name": {
											"type": "string",
											"description": "The name of the event."
										},
										"event_description": {
											"type": "string",
											"description": "The description of the event"
										},
										"event_start": {
											"type": "string",
											"description": "The time the event starts in RFC 3339 format."
										},
										"event_end": {
											"type": "string",
											"description": "The time the event ends in RFC 3339 format."
										}
									},
									"required": [
										"event_name",
										"event_description",
										"event_start",
										"event_end"
									],
									"additionalProperties": False
								}
							}
						},
						"required": [
							"events"
						],
						"additionalProperties": False
					}
				}
			},
			temperature=.5,
			max_completion_tokens=6000,
			top_p=1,
			frequency_penalty=0,
			presence_penalty=0,
			store=False
      	)
        return response.choices[0].message.content

    def main(self):
        pass
        

if __name__ == "__main__":
    client = OpenAiClient.get_client()
    module = GenerativeSchedulingModule(client)
    module.main()