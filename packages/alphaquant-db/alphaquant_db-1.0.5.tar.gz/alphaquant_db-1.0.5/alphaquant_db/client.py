import logging
from typing import Optional, Literal
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from .utils import DBUtils

logger = logging.getLogger(__name__)

class AlphaQuantDB:
    """
    Motor MongoDB Client for AlphaQuant
    Provides async operations for MongoDB using Motor.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize Motor MongoDB client
        
        Args:
            connection_string: MongoDB connection string (default: from MONGO_URL env var)
        """
        self._connection_string = connection_string
        self.database_name = "quant"
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._is_connected = False
        
    async def connect(self) -> None:
        """Establish connection to MongoDB"""
        try:
            self._client = AsyncIOMotorClient(self._connection_string)
            await self._client.admin.command('ping')
            
            self._database = self._client[self.database_name]
            self._is_connected = True
            
            logger.info(f"Connected to MongoDB database: {self.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}") from e
    
    async def close(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("MongoDB connection closed")
    
    def __ensure_connected(self) -> None:
        """Ensure client is connected"""
        if not self._is_connected or self._database is None:
            raise ConnectionError("Not connected to MongoDB. Call connect() first.")
    
    def __get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """Get MongoDB collection"""
        self.__ensure_connected()
        return self._database[collection_name]

    async def get_merged_financials(
        self,
        alpha_code: str,
        financial: Literal["financial_results.quarterly", "financial_results.yearly", "balance_sheet", "cash_flow"],
    ):
        """
        Fetch and merge financial results from both Screener and Tijori for a given alpha_code.
        Args:
            alpha_code: Unique identifier for the company.
            financial: Type of financial results to fetch (quarterly, yearly, balance sheet, cash flow).
        Returns:
            Merged financial results from both sources, sorted by report date in descending order.
            Returns an empty dict if no results found.
        """
        try:
            results = await self.__fetch_from_tijori(alpha_code, financial)
            if results:
                return results

            results = await self.__fetch_from_screener(alpha_code, financial)
            if results:
                return results
            
            return {}

        except Exception as e:
            print(f"Error fetching results for {alpha_code}: {e}")
            return {}
    
    async def __fetch_from_screener(self, alpha_code: str, financial: Literal["financial_results.quarterly", "financial_results.yearly", "balance_sheet", "cash_flow"]):
        financials_collection = self.__get_collection("financials")
        cursor = financials_collection.aggregate([
            {
                "$match": {"alpha_code": alpha_code}
            },
            {
                "$project": {
                    "_id": 0,
                    f"{financial}.screener_consolidated": 1,
                    f"{financial}.screener_standalone": 1
                }
            },
            {
                "$addFields": {
                    f"{financial}.screener_consolidated": {
                        "$sortArray": {
                            "input": f"${financial}.screener_consolidated",
                            "sortBy": {"report_date": -1}
                        }
                    },
                    f"{financial}.screener_standalone": {
                        "$sortArray": {
                            "input": f"${financial}.screener_standalone",
                            "sortBy": {"report_date": -1}
                        }
                    }
                }
            }
        ])
        print(f"Fetching from Screener for {alpha_code}.")

        async for doc in cursor:
            consolidated = DBUtils._get_nested(doc, f"{financial}.screener_consolidated", [])
            standalone = DBUtils._get_nested(doc, f"{financial}.screener_standalone", [])
            return DBUtils._merge_financials_by_date(standalone, consolidated)

    async def __fetch_from_tijori(self, alpha_code: str, financial: Literal["financial_results.quarterly", "financial_results.yearly", "balance_sheet", "cash_flow"]):
        financials_collection = self.__get_collection("financials")
        cursor = financials_collection.aggregate([
            {
                "$match": {"alpha_code": alpha_code}
            },
            {
                "$project": {
                    "_id": 0,
                    f"{financial}.tijori_consolidated": 1,
                    f"{financial}.tijori_standalone": 1
                }
            },
            {
                "$addFields": {
                    f"{financial}.tijori_consolidated": {
                        "$sortArray": {
                            "input": f"${financial}.tijori_consolidated",
                            "sortBy": {"report_date": -1}
                        }
                    },
                    f"{financial}.tijori_standalone": {
                        "$sortArray": {
                            "input": f"${financial}.tijori_standalone",
                            "sortBy": {"report_date": -1}
                        }
                    }
                }
            }
        ])
        print(f"Fetching from Tijori for {alpha_code}.")
        async for doc in cursor:
            consolidated = DBUtils._get_nested(doc, f"{financial}.tijori_consolidated", [])
            standalone = DBUtils._get_nested(doc, f"{financial}.tijori_standalone", [])
            return DBUtils._merge_financials_by_date(standalone, consolidated)
