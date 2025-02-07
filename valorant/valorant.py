import argparse
import json
import os
from pathlib import Path

EVENT = 131700 # champions pass
WEEKS = [15120, 15120, 16800, 21840, 21840, 25200, 25200, 26880]
DEFAULT = {
  "epilogue": 0,
  "current": 0,
  "days": 55, # Episode 5 Act 2
  "week": 0,
  "mission": 3,
  "tier": 1
}
EDAYS = DEFAULT["days"] - 26
CACHE = os.path.expanduser('~/.valorant.json')

def estimate(week=DEFAULT["week"], current=3, days=DEFAULT["days"], end=len(WEEKS)):
    """Rough estimate for how much exp you earn at minimum for daily play"""
    weeks = 0
    for i in range(week, end):
        if i == week:
            weeks += current * WEEKS[i]
        else:
            weeks += 3 * WEEKS[i]
                
    return weeks + days * 5000

def battle_pass(n, epilogue=5, increase=750, start=500, tier1=1250):
    """Show exp left in battlepass for tier n from no progress"""
    return increase * n * (n+1) // 2 + start * n + 36500 * epilogue - tier1

def _parse_args():
    parser = argparse.ArgumentParser(description='Track Valorant BattlePass')
    parser.add_argument('-e', '--epilogue', type=int,
                        help='Current epilogue in progress')
    parser.add_argument('-c', '--current', type=int,
                        help='Current exp progress in current tier')
    parser.add_argument('-d', '--days', type=int,
                        help='How many days are left in the battlepass')
    parser.add_argument('-w', '--week', type=int,
                        help='Current week of weekly missions in progress')
    parser.add_argument('-m', '--mission', type=int,
                        help='Number of current weekly missions left in current week')
    parser.add_argument('-t', '--tier', type=int,
                        help='Current completed tier in battlepass')
    parser.add_argument('--edays', type=int, help='How many days left in event battlepass')
    parser.add_argument('--event', action='store_true', help='Track event progress')
    parser.add_argument('--reset', action='store_true', help='Reset tracker progress')
    parser.add_argument('--show', action='store_true', help='Show current tracker config')
    parser.add_argument('--before', action='store_true', help='Show previous tracker event progress before update')
    return parser.parse_args()

def _read_progress(args):
    with open(CACHE) as json_file:
        data = json.load(json_file)
    if args.epilogue is not None:
        data["epilogue"] = args.epilogue
    if args.current is not None:
        data["current"] = args.current
    if args.days is not None:
        data["days"] = args.days
    if args.week is not None:
        data["week"] = args.week
    if args.mission is not None:
        data["mission"] = args.mission
    if args.tier is not None:
        data["tier"] = args.tier
    if args.edays is not None:
        data["edays"] = args.edays
    return data

def update_progress(args, progress):
    """Update progress for tracker"""
    if not progress.is_file() or args.reset:
        with open(CACHE, 'w') as outfile:
            json.dump(DEFAULT, outfile)
    data = _read_progress(args)
    with open(CACHE, 'w') as outfile:
        json.dump(data, outfile)
    return data

def _print_progress(args, data):
    if args.show:
        with open(CACHE) as json_file:
            config = json.load(json_file)
        print(json.dumps(config, indent=4))
    est = estimate(data["week"], data["mission"], data["days"])
    current = battle_pass(data["tier"], data["epilogue"]) + data["current"]
    bp = battle_pass(50) - current
    print("Expected exp to gain:", est)
    print("Progress exp left:", bp)
    print("Progress to work on:", bp - est)
    if args.event:
        event_est = estimate(data["week"], data["mission"], max(0, data["days"] - EDAYS), 3)
        print("Expected event exp to gain:", event_est)
        event_bp = EVENT - current
        print("Event progress exp left:", event_bp)
        print("Event progress to work on:", event_bp - event_est)

def main():
    args = _parse_args()
    progress = Path(CACHE)
    if args.before and progress.is_file() and not args.reset:
        with open(CACHE) as json_file:
            data = json.load(json_file)
        _print_progress(args, data) 
    data = update_progress(args, progress)
    _print_progress(args, data) 

if __name__ == "__main__":
    main()
