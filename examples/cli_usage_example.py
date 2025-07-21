"""
Example: List opportunities from CLI
"""
import sys
from src.api.web_api import api_service

def list_opportunities():
    for opp in api_service.get_opportunities():
        print(f"{opp['id']}: {opp['title']} - {opp['description']}")

def submit_proposal():
    title = input("Proposal Title: ")
    content = input("Proposal Content: ")
    proposal = {"title": title, "content": content}
    result = api_service.submit_proposal(proposal)
    print(f"Submitted proposal: {result}")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_opportunities()
        elif sys.argv[1] == "submit":
            submit_proposal()
        else:
            print("Usage: python cli_usage_example.py [list|submit]")
    else:
        print("Usage: python cli_usage_example.py [list|submit]")

if __name__ == "__main__":
    main()
