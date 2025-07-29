import contextlib
import logging
import os
from collections.abc import AsyncIterator
import anyio
import click
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

async def fetch_weather(city:str,api_key:str)->dict[str,str]:
     return {
         "city": city,
         "weather": "多云转晴",
         "description": "1小时后可能会有小雨",
         "temp": "26.7°C",
         "feels_like": "23°C",
         "humidity": "1.2%",
    }
    
@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--api-key",
    envvar="OPENWEATHER_API_KEY",
    required=True,
    help="OpenWeather API key (or set OPENWEATHER_API_KEY env var)",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(port: int, api_key: str, log_level: str, json_response: bool) -> int:
    """Run an MCP weather server using Streamable HTTP transport."""
     # ---------------------- Configure logging ----------------------
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("weather-server")
    app = Server("mcp-streamable-http-weather")
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle the 'get-weather' tool call."""
        ctx = app.request_context
        city = arguments.get("location")
        if not city:
            raise ValueError("'location' is required in arguments")
        await ctx.session.send_log_message(
            level="info",
            data=f"Fetching weather for {city}…",
            logger="weather",
            related_request_id=ctx.request_id,
        )
        try:
            weather = await fetch_weather(city, api_key)
        except Exception as err:
            await ctx.session.send_log_message(
                level="error",
                data=str(err),
                logger="weather",
                related_request_id=ctx.request_id,
            )
            raise
        await ctx.session.send_log_message(
            level="info",
            data="Weather data fetched successfully!",
            logger="weather",
            related_request_id=ctx.request_id,
        )
        summary = (f"{weather['city']}：{weather['description']}，温度{weather['temp']}，"f"体感{weather['feels_like']}，湿度{weather['humidity']}。")
        return [types.TextContent(type="text", text=summary)]
    
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Expose available tools to the LLM."""
        return [
            types.Tool(
                name="get-weather",
                description="查询指定城市的实时天⽓（OpenWeather 数据）",
                inputSchema={
                    "type": "object",
                    "required": ["location"],
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市的英⽂名称，如'Beijing'",
                        }
                    },
                },
            )
        ]
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # ⽆状态；不保存历史事件
        json_response=json_response,
        stateless=True,
    )
    async def handle_streamable_http(scope: Scope, receive: Receive, send: 
Send) -> None:
        await session_manager.handle_request(scope, receive, send)
        
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            logger.info("Weather MCP server started! ")
            try:
                yield
            finally:
                logger.info("Weather MCP server shutting down…")
    starlette_app = Starlette(debug=False,routes=[Mount("/mcp", app=handle_streamable_http)],lifespan=lifespan,)
    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    return 0
if __name__ == "__main__":
    main()
    
        
    
    
    
    
    
    
    
    
    
    
        
        
        
        
        
        
        
            
            
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    



