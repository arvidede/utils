from random import sample
from sys import argv, exit, getrecursionlimit
import argparse
from pathlib import Path

get_group = lambda team, groups: next(
    group for group in groups if team in group
)


def has_met_before(group, seen):
    for team in group:
        if len(seen[team].intersection(group)) > 1:
            return True
    return False


def sample_groups(teams, num_teams_per_group, seen, retries=1000):
    pool = set(teams)
    groups = []
    num_groups = len(teams) // num_teams_per_group

    while len(groups) < num_groups and retries > 0:
        group = set(sample(list(pool), num_teams_per_group))
        if has_met_before(group, seen):
            if retries == 1:
                return None
            retries -= 1
        else:
            pool.difference_update(group)
            groups.append(group)

    if len(pool) > 0:
        for i, team in enumerate(pool):
            groups[i].add(team)

    return groups


def update_seen_teams(groups, seen):
    for team, teams in enumerate(seen):
        group = get_group(team, groups)
        seen[team].update(group)
    return seen


def remove_course(groups, seen):
    for team, teams in enumerate(seen):
        group = get_group(team, groups)
        seen[team].difference_update(group)
    return seen


def generate_courses(*args):
    num_courses, num_teams, num_teams_per_group = args
    teams = range(num_teams)
    courses = []
    seen = [set() for _ in range(num_teams)]

    while len(courses) < num_courses:
        groups = sample_groups(teams, num_teams_per_group, seen)

        if groups is None:
            seen = remove_course(courses.pop(), seen)
            continue

        courses.append(groups)
        seen = update_seen_teams(groups, seen)

    try:
        test_output(courses, teams)
    except:
        return generate_courses(*args)

    return courses


def test_output(courses, teams):
    seen = {(A, B): 0 for A in teams for B in teams if A != B}
    for course in courses:
        for group in course:
            for team1 in group:
                for team2 in group:
                    if team1 != team2:
                        seen[team1, team2] += 1

    assert all(v < 2 for v in seen.values())


def test_input(courses, teams, teams_per_group):
    try:
        assert teams >= teams_per_group * courses
    except:
        print(
            f"Expected number of teams to be at least {teams_per_group * courses} (teams_per_group * courses). "
            + f"Received {teams} teams."
        )
        exit()


def read_file(path):
    try:
        with open(path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"No file {path} exists")
        exit()


def write_output(courses, teams, path):
    num_groups = len(courses[0])
    row = lambda c: f"Course {c};"
    header = lambda c: f"Group {c}"
    new_line = lambda f: f.write("\n")

    with open(path, "w+") as f:
        f.write(";" + ";".join(header(g) for g in range(num_groups)))
        new_line(f)
        for course, groups in enumerate(courses):
            f.write(row(course))
            f.write(
                ";".join(
                    f"{','.join(teams[team] for team in group)}"
                    for group in groups
                )
            )
            new_line(f)


def log(courses):
    for course, teams in enumerate(courses):
        print(f"Course: {course}\n", teams, "\n")


def get_args():
    parser = argparse.ArgumentParser(
        prog="TeamGenerator",
        description="Generates groups of teams in repeated order without overlap",
    )
    parser.add_argument("--courses", type=int, required=True)
    parser.add_argument("--teams_per_group", type=int, required=True)
    parser.add_argument("-f", "--file", type=str, required=True)
    parser.add_argument("-o", "--out", type=str, required=False)
    args = parser.parse_args()
    teams = read_file(args.file)
    out_file = args.out or "./out.csv"
    test_input(args.courses, len(teams), args.teams_per_group)

    return args.courses, teams, args.teams_per_group, out_file


def main():
    courses, teams, teams_per_group, out_file = get_args()
    groups = generate_courses(courses, len(teams), teams_per_group)
    write_output(groups, teams, out_file)


if __name__ == "__main__":
    main()
