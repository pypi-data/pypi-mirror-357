import os
from .main import Cat

COMMANDS = {
  "run": "Run the agent"
}

def main():
  # print("asdfasdf")
  cat = Cat( 
    env_path=os.getcwd() 
  )
  
  print("what do you want me to do?")
  answer = input("> ")

  if answer:
    cat.run(answer)
  else:
    print("okie, come back later")

if __name__ == "__main__":
  main()