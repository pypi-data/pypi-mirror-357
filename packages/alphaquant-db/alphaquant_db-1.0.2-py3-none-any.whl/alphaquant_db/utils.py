from datetime import datetime

class DBUtils:
    def __init__():
        pass

    @staticmethod
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
    
    @staticmethod
    def _merge_financials_by_date(self, standalone: list, consolidated: list) -> list[dict]:
        s_map = self._build_date_map(standalone)
        c_map = self._build_date_map(consolidated)

        all_dates = sorted(set(s_map) | set(c_map), reverse=True)
        return [c_map.get(d) or s_map.get(d) for d in all_dates]