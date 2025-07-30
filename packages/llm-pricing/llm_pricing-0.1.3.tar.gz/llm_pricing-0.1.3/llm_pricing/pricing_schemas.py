"""
Schemas for LLM API pricing information.

Give a star to the repository from [here](https://github.com/fswair/llm-pricing) if you find it useful!
"""

from pydantic import BaseModel, Field

class ModelCard(BaseModel):
    """
    Model representing pricing information for an LLM API.
    """
    pass

class Cost(BaseModel):
    """
    Model representing a cost associated with an LLM API.
    """
    per: str | int | float = Field("N/A", description="Range of the cost")
    per_k: bool | str = Field(False, description="Cost based on per k")
    price: str | int | float = Field("N/A", description="Cost price")
    specifier: str = Field("N/A", description="Unit of measurement for the cost")
    
    def __repr__(self) -> str:
        """
        Generate a string representation for better understanding of the model's contents in terminal.
        """
        return f"Costs ${self.price} per {self.per} ({self.specifier})"

class AnthropicPricing(ModelCard):
    """
    Model representing pricing information for the Anthropic LLM API.
    """
    model_name: str = Field(..., description="Name of the model")
    input_price: str = Field(..., description="Price per input token")
    output_price: str = Field(..., description="Price per output token")
    cache_read_price: str = Field(..., description="Price for reading from cache")
    cache_write_price: str = Field(..., description="Price for writing to cache")
    features: list[str] = Field(..., description="List of features provided by the model")
    
    def __repr__(self) -> str:
        lines = []
        lines.append(f"Model Name: {self.model_name}")
        lines.append(f"Input Price: {self.input_price}")
        lines.append(f"Output Price: {self.output_price}")
        lines.append(f"Cache Read Price: {self.cache_read_price}")
        lines.append(f"Cache Write Price: {self.cache_write_price}")
        lines.append("- Features")
        for feature in self.features:
            lines.append(f"  - {feature}")
        max_length = max(len(line) for line in lines)
        lines.append(''.ljust(max_length, "-"))
        return "\n".join(lines)

class AnthropicToolCard(ModelCard):
    """
    Model representing a tool card for the Anthropic LLM API.
    """
    
    cost: Cost = Field(..., description="Cost associated with using the tool")
    features: list[str] = Field(..., description="List of features provided by the tool")
    model_name: str = Field(..., description="Name of the tool")
    
    def __repr__(self) -> str:
        lines = []
        lines.append(f"Tool Name: {self.model_name}")
        lines.append(f"Cost: ${self.cost.price} per {self.cost.per}")
        lines.append("- Features")
        for feature in self.features:
            lines.append(f"  - {feature}")
        max_length = max(len(line) for line in lines)
        lines.append(''.ljust(max_length, "-"))
        return "\n".join(lines)


class AnthropicLLMCosts(BaseModel):
    """
    Model representing the costs associated with using the Anthropic LLM API.
    """
    tools: list[AnthropicToolCard] = Field([], description="List of tool cards with pricing information")
    latest_models: list[AnthropicPricing] = Field([], description="List of latest model cards with pricing information")
    legacy_models: list[AnthropicPricing] = Field([], description="List of legacy model cards with pricing information")
    
    def __repr__(self) -> str:
        """
        Generate a string representation for better understanding of the model's contents in terminal.
        """
        
        lines = []

        lines.append("Latest Models:")
        for model in self.latest_models:
            lines.append(repr(model))
        if self.latest_models:
            length = len(lines[-1].split("\n")[-1])
            lines.append(''.ljust(length, "*"))
            lines.append(''.ljust(length, "-"))

        lines.append("Legacy Models:")
        for model in self.legacy_models:
            lines.append(repr(model))
        if self.legacy_models:
            length = len(lines[-1].split("\n")[-1])
            lines.append(''.ljust(length, "*"))
            lines.append(''.ljust(length, "-"))
        
        lines.append("Tools:")
        for tool in self.tools:
            lines.append(repr(tool))
        
        return "\n".join(lines)