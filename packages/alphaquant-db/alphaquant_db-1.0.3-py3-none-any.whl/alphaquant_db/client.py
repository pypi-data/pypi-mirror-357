import logging
from typing import Optional, Literal
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime

logger = logging.getLogger(__name__)

class AlphaQuantDB:
    """
    Motor MongoDB Client for AlphaQuant
    Provides async operations for MongoDB using Motor.
    """
    
    def __init__(
        self, 
        connection_string: Optional[str] = None,
        database_name: Optional[str] = None,
    ):
        """
        Initialize Motor MongoDB client
        
        Args:
            connection_string: MongoDB connection string (default: from MONGO_URL env var)
            database_name: Database name (default: from MONGO_DB env var)
            **kwargs: Additional Motor client options
        """
        self._connection_string = connection_string
        self.database_name = database_name
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
    
    def _ensure_connected(self) -> None:
        """Ensure client is connected"""
        if not self._is_connected or self._database is None:
            raise ConnectionError("Not connected to MongoDB. Call connect() first.")
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """Get MongoDB collection"""
        self._ensure_connected()
        return self._database[collection_name]

    async def get_latest_results(
        self,
        alpha_code: str,
        period: Literal["quarterly", "yearly"],
    ):
        try:
            results = await self._fetch_from_tijori(alpha_code, period)
            if results:
                return results

            results = await self._fetch_from_screener(alpha_code, period)
            if results:
                return results
            
            return {}

        except Exception as e:
            print(f"Error fetching results for {alpha_code}: {e}")
            return {}
    
    async def _fetch_from_screener(self, alpha_code: str, period: Literal["quarterly", "yearly"]):
        financials_collection = self.get_collection("financials")
        cursor = financials_collection.aggregate([
            {
                "$match": {"alpha_code": alpha_code}
            },
            {
                "$project": {
                    "_id": 0,
                    f"financial_results.{period}.screener_consolidated": 1,
                    f"financial_results.{period}.screener_standalone": 1
                }
            },
            {
                "$addFields": {
                    f"financial_results.{period}.screener_consolidated": {
                        "$sortArray": {
                            "input": f"$financial_results.{period}.screener_consolidated",
                            "sortBy": {"report_date": -1}
                        }
                    },
                    f"financial_results.{period}.screener_standalone": {
                        "$sortArray": {
                            "input": f"$financial_results.{period}.screener_standalone",
                            "sortBy": {"report_date": -1}
                        }
                    }
                }
            }
        ])
        print(f"Fetching from Screener for {alpha_code}.")

        async for doc in cursor:
            consolidated = doc.get("financial_results", {}).get(period, {}).get(f"screener_consolidated", [])
            standalone = doc.get("financial_results", {}).get(period, {}).get(f"screener_consolidated", [])
            return self._merge_financials_by_date(standalone, consolidated)

    async def _fetch_from_tijori(self, alpha_code: str, period: Literal["quarterly", "yearly"]):
        financials_collection = self.get_collection("financials")
        cursor = financials_collection.aggregate([
            {
                "$match": {"alpha_code": alpha_code}
            },
            {
                "$project": {
                    "_id": 0,
                    f"financial_results.{period}.tijori_consolidated": 1,
                    f"financial_results.{period}.tijori_standalone": 1
                }
            },
            {
                "$addFields": {
                    f"financial_results.{period}.tijori_consolidated": {
                        "$sortArray": {
                            "input": f"$financial_results.{period}.tijori_consolidated",
                            "sortBy": {"report_date": -1}
                        }
                    },
                    f"financial_results.{period}.tijori_standalone": {
                        "$sortArray": {
                            "input": f"$financial_results.{period}.tijori_standalone",
                            "sortBy": {"report_date": -1}
                        }
                    }
                }
            }
        ])
        print(f"Fetching from Tijori for {alpha_code}.")
        async for doc in cursor:
            consolidated = doc.get("financial_results", {}).get(period, {}).get(f"tijori_consolidated", [])
            standalone = doc.get("financial_results", {}).get(period, {}).get(f"tijori_standalone", [])
            return self._merge_financials_by_date(standalone, consolidated)
    
    def _build_date_map(self, entries: list[dict]) -> dict:
        return {
            (
                entry["report_date"].isoformat()
                if isinstance(entry["report_date"], datetime)
                else entry["report_date"]
            ): entry
            for entry in entries
            if "report_date" in entry
        }

    def _merge_financials_by_date(self, standalone: list, consolidated: list) -> list[dict]:
        s_map = self._build_date_map(standalone)
        c_map = self._build_date_map(consolidated)


        all_dates = sorted(set(s_map) | set(c_map), reverse=True)
        return [c_map.get(d) or s_map.get(d) for d in all_dates]
