import os
from .main import Cat

COMMANDS = {
  "run": "Run the agent"
}

def main():
  
  cat = Cat( 
    env_path=os.getcwd() 
  )


if __name__ == "__main__":
  main()