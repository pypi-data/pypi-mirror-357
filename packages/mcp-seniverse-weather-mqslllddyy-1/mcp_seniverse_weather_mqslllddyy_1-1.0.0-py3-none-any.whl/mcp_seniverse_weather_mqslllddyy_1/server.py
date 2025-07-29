import os
import requests
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Weather")


@mcp.tool()
def current_weather(citi: str) -> Dict[str, Any]:
    """
    Query the current weather by citi name
    """
    api_key = os.getenv("SENIVERSE_API_KEY")
    if not api_key:
        raise ValueError("SENIVERSE_API_KEY environment variable is not set")
    try:
        weather_response = requests.get(
            "https://api.seniverse.com/v3/weather/now.json",
            params={
                "key": api_key, 
                "location": citi, 
                "language": "zh-Hans", 
                "unit": "c"
            },
        )
        weather_response.raise_for_status()
        data = weather_response.json()
        results = data["results"]
        if not results:
            return {
                "error": f"Could not find weather data for citi: {citi}"
            }
        return results
    except requests.exceptions.RequestException as e:
        error_message = f"Weather API Error: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_message = f"Weather API Error: {error_data['message']}"
            except ValueError:
                pass
        return {"error": error_message}
