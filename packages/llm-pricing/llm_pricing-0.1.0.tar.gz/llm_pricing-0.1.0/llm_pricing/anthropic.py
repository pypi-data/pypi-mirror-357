"""
Scraper for extracting pricing information from the Anthropic LLM API pricing page.

Give a star to the repository from [here](https://github.com/fswair/llm-pricing) if you find it useful!
"""

from aiohttp import ClientSession

from .scraper import Scraper
from .pricing_schemas import Cost, AnthropicPricing, AnthropicToolCard, AnthropicLLMCosts

import re
import bs4

class AnthropicScraper(Scraper):
    """
    Scraper for extracting pricing information from the Anthropic LLM API pricing page.
    """
    
    _code_exec_cost_pattern = re.compile(r'\$(?P<price>[0-9\.]+)\sper\s(?P<per>.*?)\s(?P<specifier>per container)')
    _web_search_cost_pattern = re.compile(r'\$(?P<price>[0-9\.]+)\s\/\s(?P<per>[0-9\.]+[KMB]?)\s(?P<specifier>searches)')
    
    def __init__(self, session: ClientSession = ClientSession(), **request_params):
        super().__init__('https://www.anthropic.com/pricing#api', session, **request_params)
    
    async def transform_cost(self, tool_cost: str):
        """
        Validates the cost string against known patterns for code execution and web search costs.
        Returns a tuple of (price, per, specifier) if matched, otherwise returns None.
        """
        if code_exec_cost := self._code_exec_cost_pattern.search(tool_cost):
            cost = Cost(**code_exec_cost.groupdict())
        elif web_search_cost := self._web_search_cost_pattern.search(tool_cost):
            cost = Cost(**web_search_cost.groupdict())
        else:
            cost = Cost(price=tool_cost, per="N/A", specifier="N/A")
        
        try:
            price_float = float(cost.price)
            cost.price = int(price_float) if price_float.is_integer() else price_float
        except (ValueError, TypeError):
            pass
        cost.per_k = str(cost.per).upper() in ("1", "1K")
        return cost
    
    async def extract_latest_model_cards(self):
        """
        Extracts the latest model cards from the API pricing section.
        
        Returns:
            filter: Filtered list of model card elements that are not None.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        base = self.select_one("div[data-w-tab='API']")
        model_list = base.select('ul')[0]
        model_cards = [
            model.select_one("div.card") 
            for model in model_list.select('li')
        ]
        return filter(bool, model_cards)

    async def extract_legacy_model_cards(self):
        """
        Extracts legacy model cards from the pricing page.
        
        Returns:
            filter: Filtered list of legacy model card elements that are not None,
                   or empty list if no legacy section is found.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        base = self.select_one("div[data-w-tab='API']")
        legacy = next(
            filter(
                lambda card: 'Explore legacy models' in card.text, 
                base.select("div.u-vflex-stretch-top")
            ), 
            None
        )
        
        if not legacy:
            return []
        
        model_list = legacy.select('ul')[0]
        model_cards = [
            model.select_one("div.card") 
            for model in model_list.select('li')
        ]
        return filter(bool, model_cards)
    
    async def extract_model_card_details(self, model_card: bs4.Tag):
        """
        Extracts detailed pricing information from a model card element.
        
        Args:
            model_card (bs4.Tag): The model card HTML element to extract details from.
            
        Returns:
            AnthropicPricing: Structured pricing data including model name, prices, and features.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        model_card_name = model_card.select_one("h3").text.strip()
        model_features = [
            feature.text.strip() 
            for feature in model_card.select_one('div.u-column-4').select_one("ul").select('li')
        ]
        
        input_section, caching_section = model_card.select("div.u-column-3")[:2]
        output_section = model_card.select_one("div.u-column-2")
        
        output_price = output_section.select_one("div.u-display-xs").text.strip()
        input_price = input_section.select_one("div.u-display-xs").text.strip()
        cache_read, cache_write = caching_section.select_one("div.u-vflex-stretch-top").select("div.u-display-xs")

        return AnthropicPricing(
            model_name=model_card_name,
            input_price=input_price,
            output_price=output_price,
            cache_read_price=cache_read.text.strip(),
            cache_write_price=cache_write.text.strip(),
            features=model_features
        )
    
    async def get_latest_models(self):
        """
        Yields pricing information for all latest models.
        
        Yields:
            AnthropicPricing: Pricing data for each latest model.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        model_cards = await self.extract_latest_model_cards()
        
        for model_card in model_cards:
            yield await self.extract_model_card_details(model_card)
    
    async def get_legacy_models(self):
        """
        Yields pricing information for all legacy models.
        
        Yields:
            AnthropicPricing: Pricing data for each legacy model.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        model_cards = await self.extract_legacy_model_cards()
        
        for model_card in model_cards:
            yield await self.extract_model_card_details(model_card)
    
    async def extract_tool_cards(self):
        """
        Extracts tool cards from the pricing page.
        
        Returns:
            list: List of tool card elements, or empty list if no tools section is found.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        tool_call_card = next(
            filter(
                lambda tag: "Explore pricing for tools" in tag.text, 
                self.select("div.u-vflex-stretch-top")
            ), 
            None
        )
        
        if not tool_call_card:
            return []
        
        tools = tool_call_card.select_one("ul[role='list']").select("li")
        return list(filter(lambda tool: tool and tool.h3, tools))
    
    async def extract_tool_card_details(self, tool_card: bs4.Tag):
        """
        Extracts detailed information from a tool card element.
        
        Args:
            tool_card (bs4.Tag): The tool card HTML element to extract details from.
            
        Returns:
            AnthropicToolCard: Structured tool data including name, cost, and features.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        model_card_name = tool_card.select_one("h3").text.strip()
        model_cost = tool_card.select_one("div.u-vflex-stretch-top").select_one("div.u-display-xs")
        model_features = [
            feature.text.strip() 
            for feature in tool_card.select_one('div.u-column-4').select_one("ul").select('li')
        ]
        
        return AnthropicToolCard(
            cost=await self.transform_cost(model_cost.text.strip()),
            features=model_features,
            model_name=model_card_name,
        )
    
    async def get_tools(self):
        """
        Yields pricing information for all available tools.
        
        Yields:
            AnthropicToolCard: Tool data for each available tool.
        """
        if not hasattr(self, '_manager'):
            await self.init()
        
        tool_cards = await self.extract_tool_cards()
        
        for tool_card in tool_cards:
            yield await self.extract_tool_card_details(tool_card)
    
    async def pricing_overall(self):
        """
        Fetches comprehensive pricing information for all models and tools.
        
        Returns:
            AnthropicLLMCosts: Complete pricing data including tools, latest models, 
                              and legacy models.
        """
        return AnthropicLLMCosts(
            tools=[tool async for tool in self.get_tools()],
            latest_models=[model async for model in self.get_latest_models()],
            legacy_models=[model async for model in self.get_legacy_models()]
        )