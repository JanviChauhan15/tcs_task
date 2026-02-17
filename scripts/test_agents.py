from agents.graph import get_graph
from langchain_core.messages import HumanMessage

def test_agents():
    graph = get_graph()
    
    queries = [
        "What is the refund policy?",
        "Who has a Platinum membership?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        try:
            inputs = {"messages": [HumanMessage(content=query)]}
            result = graph.invoke(inputs)
            messages = result["messages"]
            ai_response = messages[-1]
            print(f"Response: {ai_response.content}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    test_agents()
