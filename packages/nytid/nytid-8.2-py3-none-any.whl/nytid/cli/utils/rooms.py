import logging
import typer
import typerconf
from typing_extensions import Annotated

import csv
import datetime
import urllib.parse
import urllib.request
import sys

cli = typer.Typer(name="rooms", help="Finding free rooms for courses")

BOOKED_ROOMS_URL = "utils.rooms.url"


def free_rooms(csv_url: str) -> list[tuple]:
    """
    Given a URL or path to a TimeEdit CSV file ([[csv_url]]),
    return a CSV (list of tuples) of the free rooms:

    [(start, end, unbooked_rooms), ...]

    where start and end are datetime objects and unbooked_rooms is a set of
    strings.
    """
    results = []

    parsed_url = urllib.parse.urlparse(csv_url)
    if parsed_url.scheme == "":
        csv_file = open(csv_url, "r")
    else:
        csv_file = urllib.request.urlopen(csv_url)
    with csv_file:
        reader = csv.reader(csv_file)

        # Skip the first two rows
        next(reader)
        next(reader)
        # Get the row containing the sought for rooms
        rooms_row = next(reader)
        all_rooms = rooms_row[0].split(",")
        extra_chars = " $-§&%¤#!@/=?*+"
        all_rooms = set([room.strip(extra_chars) for room in all_rooms])

        # skip the header row
        next(reader)

        # read the data
        for row in reader:
            # Get the date and time from the first four columns
            start_date = datetime.date.fromisoformat(row[0])
            start_time = datetime.time.fromisoformat(row[1])
            start = datetime.datetime.combine(start_date, start_time)

            end_date = datetime.date.fromisoformat(row[2])
            end_time = datetime.time.fromisoformat(row[3])
            end = datetime.datetime.combine(end_date, end_time)

            # Get the booked rooms from the last column,
            # these are already clean.
            booked_rooms = row[7].split(",")
            if len(booked_rooms) == 1 and booked_rooms[0] == "":
                booked_rooms = set()
            else:
                booked_rooms = set(booked_rooms)
            unbooked_rooms = all_rooms - booked_rooms

            results.append((start, end, unbooked_rooms))

    time_dict = {}
    for start, end, unbooked_rooms in results:
        if (start, end) in time_dict:
            time_dict[(start, end)] &= unbooked_rooms
        else:
            time_dict[(start, end)] = unbooked_rooms

    results = [
        (start, end, unbooked_rooms)
        for (start, end), unbooked_rooms in time_dict.items()
    ]

    return results


def booked_rooms(csv_url: str) -> list[tuple]:
    """
    Given a URL or path to a TimeEdit CSV file ([[csv_url]]),
    return a CSV (list of tuples) of the booked rooms:

    [(start, end, booked_rooms), ...]

    where start and end are datetime objects and booked_rooms is a set of
    strings.
    """
    results = []

    parsed_url = urllib.parse.urlparse(csv_url)
    if parsed_url.scheme == "":
        csv_file = open(csv_url, "r")
    else:
        csv_file = urllib.request.urlopen(csv_url)
    with csv_file:
        reader = csv.reader(csv_file)

        # Skip the first two rows.
        next(reader)
        next(reader)

        # Ignore the row containing the sought for rooms.
        next(reader)

        # Skip the header row.
        next(reader)

        # read the data
        for row in reader:
            # Get the date and time from the first four columns
            start_date = datetime.date.fromisoformat(row[0])
            start_time = datetime.time.fromisoformat(row[1])
            start = datetime.datetime.combine(start_date, start_time)

            end_date = datetime.date.fromisoformat(row[2])
            end_time = datetime.time.fromisoformat(row[3])
            end = datetime.datetime.combine(end_date, end_time)

            # Get the booked rooms from the last column,
            # these are already clean.
            booked_rooms = row[7].split(",")
            if len(booked_rooms) == 1 and booked_rooms[0] == "":
                booked_rooms = set()
            else:
                booked_rooms = set(booked_rooms)
            if booked_rooms:
                results.append((start, end, booked_rooms))

    return results


delimiter_opt = Annotated[
    str,
    typer.Option(
        "-d", "--delimiter", help="CSV delimiter, default tab.", show_default=False
    ),
]


@cli.command(name="set-url")
def set_url_cmd(
    url: Annotated[str, typer.Argument(help="URL to CSV file with " "TimeEdit export")]
):
    """
    Search for all the rooms that you're interested in in TimeEdit.
    Set the relevant time intervals to something future proof: you
    don't want it to be too short, then you have to update the URL
    too often. Get the URL for downloading the schedule in CSV
    format.
    """
    try:
        typerconf.set(BOOKED_ROOMS_URL, url)
    except Exception as err:
        logging.error(f"Can't set URL: {err}")
        raise typer.Exit(1)


@cli.command(name="unbooked")
def unbooked_cmd(
    delimiter: delimiter_opt = "\t",
):
    """
    Shows date and time and which rooms are free.
    """
    try:
        rooms_url = typerconf.get(BOOKED_ROOMS_URL)
    except Exception as err:
        logging.error(f"Can't get URL from config: {err}")
        logging.info("Please set it with " "'nytid utils rooms set-url <url>'")
        raise typer.Exit(1)

    try:
        csv_out = csv.writer(sys.stdout, delimiter=delimiter)

        for start, end, rooms in free_rooms(rooms_url):
            csv_out.writerow([start, end, ", ".join(sorted(rooms))])
    except Exception as err:
        logging.error(f"Can't get free rooms: {err}")
        raise typer.Exit(1)


@cli.command(name="booked")
def booked_cmd(
    delimiter: delimiter_opt = "\t",
):
    """
    Shows date and time and which rooms are booked.
    """
    try:
        rooms_url = typerconf.get(BOOKED_ROOMS_URL)
    except Exception as err:
        logging.error(f"Can't get URL from config: {err}")
        logging.info("Please set it with " "'nytid utils rooms set-url <url>'")
        raise typer.Exit(1)

    try:
        csv_out = csv.writer(sys.stdout, delimiter=delimiter)

        for start, end, rooms in booked_rooms(rooms_url):
            csv_out.writerow([start, end, ", ".join(sorted(rooms))])
    except Exception as err:
        logging.error(f"Can't get booked rooms: {err}")
        raise typer.Exit(1)


if __name__ == "__main__":
    cli()
