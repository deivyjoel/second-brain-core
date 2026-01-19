import re
"""
Generate a unique name by appending a numeric suffix if needed.
E.g., "name", "name (2)", "name (3)", etc.
"""
def generate_unique_name(base_name: str, sibling_names: list[str]) -> str:
    clean_name = base_name.strip()
    if clean_name not in sibling_names:
        return clean_name
    
    def find_missing_number(nums: list[int]) -> int:
        if not nums:
            return 2

        set_nums = set(nums)
        counter = 2
        while counter in set_nums:
            counter+=1
        return counter
    
    pattern = re.compile(rf"^{re.escape(clean_name)} \((\d+)\)$")

    used_suffixes = []
    for name in sibling_names:
        match = pattern.match(name)
        if match:
            used_suffixes.append(int(match.group(1)))

    proximo_sufijo = find_missing_number(used_suffixes)
    
    return f"{clean_name} ({proximo_sufijo})"

