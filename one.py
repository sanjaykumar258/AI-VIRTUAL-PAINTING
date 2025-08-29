class LogisticsChecker:
def __init__(self):
# Allowed combinations that can be transported together
self.allowed_combinations = [
{"electronics", "furniture"},
{"food", "medicines"},
{"chemicals", "cleaning_supplies"},
{"toys", "books"}
]
def can_transport(self, items):
items_set = set(items)
for combo in self.allowed_combinations:
if items_set.issubset(combo):
return "Accepted"
return "Rejected"
# Example usage
items = input("Enter items (comma-separated): ").split(',')
items = [item.strip().lower() for item in items]
checker = LogisticsChecker()
print(checker.can_transport(items))