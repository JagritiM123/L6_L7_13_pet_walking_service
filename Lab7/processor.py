import math


def parse_walk_schedule(schedule_spec):
    """Parse '<pets>-<minutes>-<weekend>' and calculate the walk fee."""
    if not isinstance(schedule_spec, str):
        raise TypeError("schedule_spec must be a string")

    parts = schedule_spec.strip().split("-")
    if len(parts) != 3:
        raise ValueError("Schedule must be in the format pets-minutes-YES/NO")

    pets_str, mins_str, weekend_str = parts

    try:
        pets = int(pets_str.strip())
        mins = int(mins_str.strip())
    except ValueError as exc:
        raise ValueError("Pets and minutes must be integers") from exc

    if pets <= 0:
        raise ValueError("Number of pets must be greater than zero")
    if mins <= 0:
        raise ValueError("Minutes must be greater than zero")

    weekend = weekend_str.strip().upper()
    weekend_map = {"YES": 15.0, "NO": 0.0}
    if weekend not in weekend_map:
        raise ValueError("Weekend must be YES or NO")

    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + pets * 5.0 + weekend_map[weekend]
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Calculate minutes per pet from '<minutes>/<pets>'."""
    if not isinstance(walk_metrics_str, str):
        raise TypeError("walk_metrics_str must be a string")

    parts = walk_metrics_str.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Metrics must be in the format minutes/pets")

    try:
        mins = float(parts[0].strip())
        pets = float(parts[1].strip())
    except ValueError as exc:
        raise ValueError("Minutes and pets must be numeric") from exc

    if not math.isfinite(mins) or not math.isfinite(pets):
        raise ValueError("Minutes and pets must be finite numbers")
    if mins <= 0:
        raise ValueError("Minutes must be greater than zero")
    if pets <= 0:
        raise ValueError("Pets must be greater than zero")

    return round(mins / pets, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return surcharge for CALM, PLAYFUL, REACTIVE, or AGGRESSIVE."""
    if not isinstance(temperament_code, str):
        raise TypeError("temperament_code must be a string")

    code = temperament_code.strip().upper()
    surcharges = {
        "CALM": 0.0,
        "PLAYFUL": 5.0,
        "REACTIVE": 12.0,
        "AGGRESSIVE": 20.0,
    }

    if code not in surcharges:
        raise ValueError(
            "Unknown temperament; use CALM, PLAYFUL, REACTIVE, or AGGRESSIVE"
        )

    return surcharges[code]


def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    try:
        print(parse_walk_schedule(s_input))
    except (TypeError, ValueError) as exc:
        print("Invalid schedule:", exc)

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    try:
        print("Pace (min/pet):", compute_pace_per_pet(p_input))
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        print("Invalid metrics:", exc)

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    try:
        print("Surcharge: $", lookup_temperament_surcharge(t_input))
    except (TypeError, ValueError) as exc:
        print("Invalid temperament:", exc)


if __name__ == "__main__":
    main()
