from datetime import datetime

class DBUtils:
    def __init__():
        pass

    @staticmethod
    def _build_date_map(entries: list[dict]) -> dict:
        return {
            (
                entry["report_date"].isoformat()
                if isinstance(entry["report_date"], datetime)
                else entry["report_date"]
            ): entry
            for entry in entries
            if "report_date" in entry if entry["report_date"] is not None
        }
    
    @staticmethod
    def _merge_financials_by_date(standalone: list, consolidated: list) -> list[dict]:
        s_map = DBUtils._build_date_map(standalone)
        c_map = DBUtils._build_date_map(consolidated)


        all_dates = sorted(set(s_map) | set(c_map), reverse=True)
        return [c_map.get(d) or s_map.get(d) for d in all_dates]
    
    @staticmethod
    def _get_nested(doc: dict, dotted_key: str, default=None):
        print("", dotted_key)
        keys = dotted_key.split(".")
        for key in keys:
            doc = doc.get(key)
            if doc is None:
                return default
        return doc
