import re

def generate_unique_name(base_name: str, existing_names: list[str]) -> str:
    if base_name not in existing_names:
        return base_name
    """
    Cuando le pase un nombre, detecte sí está ahi en la lista y si lo está. Entonces que devuelve un nombre con el - copia
    """
    def find_missing_number(nums: list[int]) -> int:
        if not nums:
            return 2

        set_nums = set(nums)
        counter = 2
        while counter in set_nums:
            counter+=1
        return counter
    
    pattern = re.compile(rf"^{re.escape(base_name)} \((\d+)\)$")

    sufijos_usados = []
    for name in existing_names:
        match = pattern.match(name)
        if match:
            sufijos_usados.append(int(match.group(1)))

    proximo_sufijo = find_missing_number(sufijos_usados)
    
    return f"{base_name} ({proximo_sufijo})"

