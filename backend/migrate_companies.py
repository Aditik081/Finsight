
from database import companies_collection

result = companies_collection.update_many(
    {},
    [
        {
            "$set": {
                "exchange": {
                    "$ifNull": ["$exchange", ""]
                },
                "country": {
                    "$ifNull": ["$country", ""]
                },
                "currency": {
                    "$ifNull": ["$currency", ""]
                },
                "provider_symbols": {
                    "$ifNull": ["$provider_symbols", {}]
                }
            }
        }
    ]
)

print("Total companies:", result.matched_count)
print("Updated companies:", result.modified_count)
