
from tools.budget_calculator import estimate_budget
from tools.flight import get_flight_info
from tools.hotels import get_hotel_info
from tools.itenary_planner import create_itinerary
from tools.rag_tool import search_travel_knowledge
from tools.tavily_tool import get_tavily_info
from tools.whether import get_weather


TOOLS = [
    create_itinerary,
    get_hotel_info,
    get_weather,
    estimate_budget,
    get_flight_info,
    get_tavily_info,
    # Give the agent access to the indexed PDFs for grounded travel answers.
    search_travel_knowledge,
]