import os
import logging
from enum import StrEnum

from typing import Optional, List, Protocol
from dataclasses import dataclass

from mcp_amazon_paapi._vendor.paapi5_python_sdk.api.default_api import DefaultApi
from mcp_amazon_paapi._vendor.paapi5_python_sdk.models import PartnerType, SearchItemsResource, SearchItemsRequest, SearchItemsResponse, GetItemsRequest, GetItemsResponse
from mcp_amazon_paapi._vendor.paapi5_python_sdk.models.item import Item as ItemResponse

logger = logging.getLogger(__name__)


@dataclass
class ItemImage:
    """
    Represents an image of an item at the Amazon marketplace.
    
    Args:
    - url: The URL of the image.
    - height: The height of the image in pixels.
    - width: The width of the image in pixels.
    """
    url: str
    height: int
    width: int


@dataclass
class Item:
    """
    Represents an item at the Amazon marketplace.
    
    Args:
    - asin: The Amazon Standard Identification Number of the item.
    - title: The title of the item.
    - detail_page_url: The URL of the detail page of the item.
    - bying_price: The price of the item if available.
    - audience_rating: The audience rating of the item if available.
    - is_adult_product: Whether the item is an adult product if available.
    - image: The primary image of the item if available.
    """
    asin: str
    title: Optional[str] = None
    detail_page_url: Optional[str] = None
    bying_price: Optional[float] = None
    audience_rating: Optional[str] = None
    is_adult_product: Optional[bool] = None
    image: Optional[ItemImage] = None


class SearchSort(StrEnum):
    """
    The sort order of the search results.
    """
    AVG_CUSTOMER_REVIEWS = "AvgCustomerReviews" # Sorts results according to average customer reviews
    FEATURED = "Featured" # Sorts results with featured items having higher rank
    NEWEST_ARRIVALS = "NewestArrivals" # Sorts results with according to newest arrivals
    PRICE_HIGH_TO_LOW = "Price:HighToLow" # Sorts results according to most expensive to least expensive
    PRICE_LOW_TO_HIGH = "Price:LowToHigh" # Sorts results according to least expensive to most expensive
    RELEVANCE = "Relevance" # Sorts results with relevant items having higher rank


class PAAPIClientProtocol(Protocol):
    """Protocol for Amazon PA-API client to enable easy mocking in tests"""
    def search_items(self, request: SearchItemsRequest) -> SearchItemsResponse:
        ...

    def get_items(self, request: GetItemsRequest) -> GetItemsResponse:
        ...


@dataclass
class PAAPIClientConfig:
    """Configuration for the Amazon PA-API client"""
    access_key: str
    secret_key: str
    host: str
    region: str
    marketplace: str
    partner_tag: str   
    partner_type: PartnerType = PartnerType.ASSOCIATES


class AmazonPAAPIService:
    """Service class for managing Amazon PA-API client and operations"""

    ITEM_RESOURCES : List[SearchItemsResource] = [
        SearchItemsResource.ITEMINFO_TITLE,
        SearchItemsResource.ITEMINFO_CONTENTRATING,
        SearchItemsResource.ITEMINFO_PRODUCTINFO,
        SearchItemsResource.OFFERS_LISTINGS_PRICE,
        SearchItemsResource.IMAGES_PRIMARY_LARGE,
    ]
    
    def __init__(self, client: Optional[PAAPIClientProtocol] = None, config: Optional[PAAPIClientConfig] = None):
        """
        Initialize the service with an optional client and config (useful for testing)
        
        Args:
            client: Optional client instance. If None, creates from config.
            config: Optional config instance. If None, creates from environment variables.
        """
        self._client: Optional[PAAPIClientProtocol] = client
        self._config: Optional[PAAPIClientConfig] = config

    @property
    def config(self) -> PAAPIClientConfig:
        """Lazy initialization of the config"""
        if self._config is None:
            self._config = self._create_config()
        return self._config
    
    def _create_config(self) -> PAAPIClientConfig:
        """Create a new Amazon PA-API client config from environment variables"""
        return PAAPIClientConfig(
            access_key=os.getenv("PAAPI_ACCESS_KEY"),
            secret_key=os.getenv("PAAPI_SECRET_KEY"),
            host=os.getenv("PAAPI_HOST", "webservices.amazon.de"),
            region=os.getenv("PAAPI_REGION", "eu-west-1"),
            partner_tag=os.getenv("PAAPI_PARTNER_TAG"),
            partner_type=PartnerType.ASSOCIATES,
            marketplace=os.getenv("PAAPI_MARKETPLACE", "www.amazon.de"),
        )
        
    @property
    def client(self) -> PAAPIClientProtocol:
        """Lazy initialization of the client"""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> PAAPIClientProtocol:
        """Create a new Amazon PA-API client from environment variables"""
        access_key = self.config.access_key
        secret_key = self.config.secret_key
        host = self.config.host
        region = self.config.region

        return DefaultApi(
            access_key=access_key, 
            secret_key=secret_key, 
            host=host, 
            region=region,
        )
    
    def _map_item_response(self, item: ItemResponse) -> Item:
        """
        Map the item response to the Item class.
        """
        asin = item.asin

        title = ""
        if item.item_info and item.item_info.title:
            title = item.item_info.title.display_value

        detail_page_url = ""
        if item.detail_page_url:
            detail_page_url = item.detail_page_url

        bying_price = None
        if item.offers and item.offers.listings and item.offers.listings[0] and item.offers.listings[0].price:
            bying_price = item.offers.listings[0].price.amount
        
        audience_rating = ""
        if item.item_info and item.item_info.content_rating and item.item_info.content_rating.audience_rating:
            audience_rating = item.item_info.content_rating.audience_rating.display_value

        is_adult_product = False
        if item.item_info and item.item_info.product_info and item.item_info.product_info.is_adult_product:
            is_adult_product = item.item_info.product_info.is_adult_product.display_value

        image = None
        if item.images and item.images.primary and item.images.primary.large:
            primary_img = item.images.primary.large
            image = ItemImage(url=primary_img.url, height=primary_img.height, width=primary_img.width)

        return Item(asin, title, detail_page_url, bying_price, audience_rating, is_adult_product, image)
    
    def search_items(self, search_term: str, category: Optional[str] = None, item_count: Optional[int] = 10, sort_by: Optional[SearchSort] = None) -> List[Item]:
        """
        Search for items using the Amazon PA-API 5.0
        (https://webservices.amazon.com/paapi5/documentation/)

        Args:
            search_term (str): The search term to use.
            category (Optional[str]): The category (browse node) to search in.
            item_count (Optional[int]): Maximum number of items to return (default 10).
            sort_by (Optional[SearchSort]): Sort order of the search results.

        Returns:
            List[Item]: Items that match the search criteria.
        """
        search_items_request = SearchItemsRequest(
            partner_tag=self.config.partner_tag,
            partner_type=self.config.partner_type,
            keywords=search_term,
            item_count=item_count,
            resources=self.ITEM_RESOURCES,
            marketplace=self.config.marketplace,
        )

        if category:
            search_items_request.search_index = category

        if sort_by:
            search_items_request.sort_by = sort_by.value

        logger.info(f"Searching for items with request: {search_items_request}")
        response : SearchItemsResponse = self.client.search_items(search_items_request)

        if response.errors:
            logger.error(f"Search failed with errors: {response.errors}")
            return []

        if not response.search_result or not response.search_result.items:
            logger.warning("Search found no items")
            return []

        logger.info(f"Search found {len(response.search_result.items)} items")
        
        return [self._map_item_response(item) for item in response.search_result.items]

    def get_item(self, asin: str) -> Optional[Item]:
        """
        Get a specific item by its ASIN using the Amazon PA-API 5.0
        (https://webservices.amazon.com/paapi5/documentation/)

        Args:
            asin (str): The ASIN of the item to get.

        Returns:
            Optional[Item]: The item with the given ASIN if found, otherwise None.
        """
        get_items_request = GetItemsRequest(
            partner_tag=self.config.partner_tag,
            partner_type=self.config.partner_type,
            item_ids=[asin],
            resources=self.ITEM_RESOURCES,
            marketplace=self.config.marketplace,
        )

        logger.info(f"Getting item with request: {get_items_request}")
        response = self.client.get_items(get_items_request)

        if response.errors:
            logger.error(f"Get item failed with errors: {response.errors}")
            return None

        if not response.items_result or not response.items_result.items:
            logger.warning("Get item found no items")
            return None
        
        return self._map_item_response(response.items_result.items[0])