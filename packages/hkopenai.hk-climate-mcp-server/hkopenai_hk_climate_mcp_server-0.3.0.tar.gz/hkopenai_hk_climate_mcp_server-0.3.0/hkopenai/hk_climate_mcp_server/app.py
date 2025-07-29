import argparse
from fastmcp import FastMCP
from hkopenai.hk_climate_mcp_server import tool_weather
from typing import Dict, Annotated, Optional
from pydantic import Field

def create_mcp_server():
    """Create and configure the HKO MCP server"""
    mcp = FastMCP(name="HKOServer")

    @mcp.tool(
        description="Get current weather observations, warnings, temperature, humidity and rainfall in Hong Kong from Hong Kong Observatory, with optional region or place in Hong Kong",
    )
    def get_current_weather(region: str = "Hong Kong Observatory") -> Dict:
        return tool_weather.get_current_weather(region)

    @mcp.tool(
        description="Get the 9-day weather forecast for Hong Kong including general situation, daily forecasts, sea and soil temperatures",
    )
    def get_9_day_weather_forecast(lang: str = "en") -> Dict:
        return tool_weather.get_9_day_weather_forecast(lang)

    @mcp.tool(
        description="Get local weather forecast for Hong Kong including forecast description, outlook and update time",
    )
    def get_local_weather_forecast(lang: str = "en") -> Dict:
        return tool_weather.get_local_weather_forecast(lang)

    @mcp.tool(
        description="Get weather warning summary for Hong Kong including warning messages and update time",
    )
    def get_weather_warning_summary(lang: str = "en") -> Dict:
        return tool_weather.get_weather_warning_summary(lang)

    @mcp.tool(
        description="Get detailed weather warning information for Hong Kong including warning statement and update time",
    )
    def get_weather_warning_info(lang: str = "en") -> Dict:
        return tool_weather.get_weather_warning_info(lang)

    @mcp.tool(
        description="Get special weather tips for Hong Kong including tips list and update time",
    )
    def get_special_weather_tips(lang: str = "en") -> Dict:
        return tool_weather.get_special_weather_tips(lang)

    @mcp.tool(
        description="Get latest 10-minute mean visibility data for Hong Kong",
    )
    def get_visibility_data(lang: str = "en", rformat: str = "json") -> Dict:
        return tool_weather.get_visibility_data(lang, rformat)

    @mcp.tool(
        description="Get cloud-to-ground and cloud-to-cloud lightning count data",
    )
    def get_lightning_data(lang: str = "en", rformat: str = "json") -> Dict:
        return tool_weather.get_lightning_data(lang, rformat)

    @mcp.tool(
        description="Get times of moonrise, moon transit and moonset",
    )
    def get_moon_times(
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_moon_times(
            year=year,
            month=month,
            day=day,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get hourly heights of astronomical tides for a specific station in Hong Kong",
    )
    def get_hourly_tides(
        station: str,
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_hourly_tides(
            station=station,
            year=year,
            month=month,
            day=day,
            hour=hour,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get times and heights of astronomical high and low tides for a specific station in Hong Kong",
    )
    def get_high_low_tides(
        station: str,
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_high_low_tides(
            station=station,
            year=year,
            month=month,
            day=day,
            hour=hour,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get times of sunrise, sun transit and sunset for Hong Kong",
    )
    def get_sunrise_sunset_times(
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_sunrise_sunset_times(
            year=year,
            month=month,
            day=day,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get Gregorian-Lunar calendar conversion data",
    )
    def get_gregorian_lunar_calendar(
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_gregorian_lunar_calendar(
            year=year,
            month=month,
            day=day,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get daily mean temperature data for a specific station in Hong Kong",
    )
    def get_daily_mean_temperature(
        station: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_daily_mean_temperature(
            station=station,
            year=year,
            month=month,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get daily maximum temperature data for a specific station in Hong Kong",
    )
    def get_daily_max_temperature(
        station: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_daily_max_temperature(
            station=station,
            year=year,
            month=month,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get daily minimum temperature data for a specific station in Hong Kong",
    )
    def get_daily_min_temperature(
        station: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_daily_min_temperature(
            station=station,
            year=year,
            month=month,
            lang=lang,
            rformat=rformat
        )

    @mcp.tool(
        description="Get weather and radiation level report for Hong Kong",
    )
    def get_weather_radiation_report(
        date: Optional[str] = None,
        station: Optional[str] = None,
        lang: str = "en",
        rformat: str = "json"
    ) -> Dict:
        return tool_weather.get_weather_radiation_report(
            date=date,
            station=station,
            lang=lang,
            rformat=rformat
        )
    
    return mcp

def main():
    parser = argparse.ArgumentParser(description='HKO MCP Server')
    parser.add_argument('-s', '--sse', action='store_true',
                       help='Run in SSE mode instead of stdio')
    args = parser.parse_args()

    server = create_mcp_server()
    
    if args.sse:
        server.run(transport="streamable-http")
        print("HKO MCP Server running in SSE mode on port 8000")
    else:
        server.run()
        print("HKO MCP Server running in stdio mode")

if __name__ == "__main__":
    main()
