from openai import OpenAI

client = OpenAI(api_key="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")
system_message = "You are a helpful assistant."

def get_chat_response(message):
  response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
      {"role": "system", "content": system_message},
      {"role": "user", "content": message},
    ]
  )
  print(response.choices[0].message.content)  # Debugging line to print the response
  return response.choices[0].message.content

get_chat_response("What is the capital of France?")


def thinking_loop(problem, max_iterations=5):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Solve this problem step by step. Split your reasoning into steps and say 'Final Answer:' when done.\nProblem: {problem}"}
    ]
    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        ai_message = response.choices[0].message.content
        print(f"Step {i+1}: {ai_message}\n")  # Print each step
        messages.append({"role": "assistant", "content": ai_message})
        if "Final Answer:" in ai_message:
            break
        # Optionally, you can prompt the AI to continue if not finished
        messages.append({"role": "user", "content": "Continue reasoning step by step. If you have the answer, say 'Final Answer:'."})

# Example usage:
thinking_loop("What is the sum of the first 10 positive integers?")
