from typing import Callable

import datetime as dat
import dateutil

# Import matplotlib before pandas to avoid import ordering issues.
import matplotlib.pyplot as plt
import pandas as pd
import requests
import numpy as np
from tqdm import tqdm
import itertools
import re
import time


class NotionHeaders:
    def __init__(self, notion_token: str, notion_version: str = "2022-06-28"):
        self.__notion_token__ = notion_token
        self.__notion_version__ = notion_version

    def __repr__(self) -> str:
        return (
            "NotionHeaders(",
            'authorization="Bearer <SECRET_NOTION_TOKEN>", ',
            'content_type="application/json", ',
            f'notion_version="{self.__notion_version__}")',
        )

    def __str__(self) -> str:
        return (
            "NotionHeaders(",
            'authorization="Bearer <SECRET_NOTION_TOKEN>", ',
            'content_type="application/json", ',
            f'notion_version="{self.__notion_version__}")',
        )

    def to_dict(self) -> dict:
        return {
            "Authorization": "Bearer " + self.__notion_token__,
            "Content-Type": "application/json",
            "Notion-Version": f"{self.__notion_version__}",
        }


def get_notion_pages(
    url_endpoint,
    headers,
    num_pages=None,
    sort_by=None,
    filter_by=None,
):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    get_all = num_pages is None
    # TODO: Logic for getting correct number of pages seems wrong. Check this.
    max_notion_pages_per_request = 100
    page_size = max_notion_pages_per_request if get_all else num_pages

    payload = {"page_size": page_size}
    if sort_by is not None:
        payload["sorts"] = sort_by
    if filter_by is not None:
        payload["filter"] = filter_by

    progress = tqdm()
    response = requests.post(url_endpoint, json=payload, headers=headers)

    data = response.json()

    if response.status_code != 200:
        print(f"status: {response.status_code}")
        print(f"reason: {response.reason}")
        # Calling code can handle a failed request, so return an empty result.

    results = data.get("results", [])
    progress.update()

    while data.get("has_more", False) and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        if sort_by is not None:
            payload["sorts"] = sort_by

        response = requests.post(url_endpoint, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200:
            print(f"status: {response.status_code}")
            print(f"reason: {response.reason}")
            continue

        results.extend(data["results"])
        progress.update()

    return results


# TODO: Update this to fetch by date range rather than a prescribed number of
# pages and a single database. Provisonally, store all related DBs in a dict,
# fetch from the ones with the relevant data, and paginate on any edge cases.
def get_notion_pages_from_db(
    db_id,
    headers,
    sort_column: str | None = "date",
    sort_direction: str = "ascending",
    filter_by: dict | None = None,
    num_pages=None,
):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    # The 'date' column should be standard across all personal DBs in Notion.
    # However, it would be ideal to minimise the amount of data processing,
    # including sorting. If checking Notion personally, typically only need the
    # latest data, so having it stored in descending order makes sense. On the
    # other hand, most code assumes/prefers ascending order. Importantly, if
    # the data is always inserted in some sorted order, then re-sorting is
    # either trivial or not needed at all.
    # TODO: Decide how to deal with sorting.
    sort_by = [{"property": sort_column, "direction": sort_direction}]
    if sort_column is None:
        sort_by = None

    results = get_notion_pages(
        url,
        headers.to_dict(),
        num_pages=num_pages,
        sort_by=sort_by,
        filter_by=filter_by,
    )

    return results


# This function compresses event-like data (could be generalised to arbitrary
# data.)
# Several optimisations are implemented vs baseline of '[datetime+TZ]: [DATA]':
# 1. The date component is grouped - entries with a common day do not repeat the
# day, entries with a common month, etc. Time is left alone as less likely to
# benefit.
# 2. The time component removes the second and millisecond components as they
# are always 0.
# 3. Spaces are removed. Newlines are required however and kept.
# 4. Short-codes are used for event names, and events on the same timestamp are
# grouped, separated with commas (this is assumed via the events being lists
# rather than scalar values).
# Rough testing suggests a 122x to 128x reduction in relevant database sizes,
# drastically improving loading times (in particular saving on paginated calls).
def compress_event_data(
    ts: list[dat.datetime],
    events: list[list[str]],
    compression_map: dict[str, str],
    db_id: str,
) -> list[dict]:
    pages = []
    counter = 0
    chunk_idx = 0
    payload = ""
    payload_dates = []
    while counter < len(ts):
        date = ts[counter]
        datetime_prefix = compressed_date(payload_dates, date)
        payload_dates.append(date)

        categories = events[counter]
        compressed_categories = [compression_map[c] for c in categories]

        entry = f"{datetime_prefix}:{','.join(compressed_categories)}\n"
        payload += entry

        if len(payload) < 2000:
            counter += 1
            continue

        # +1 to remove the trailing newline.
        payload = payload[: -(len(entry) + 1)]
        assert len(payload) <= 2000
        chunked_page = new_page_schema(
            db_id,
            chunk_idx,
            payload,
        )
        pages.append(chunked_page)

        time.sleep(1 / 3)
        payload = ""
        payload_dates = []
        chunk_idx += 1

    # Dump the remaining entries in the last chunked page.
    payload = payload[:-1]
    pages.append(
        new_page_schema(
            db_id,
            chunk_idx,
            payload,
        )
    )

    return pages


def new_page_schema(db_id, idx, payload):
    return {
        "parent": {
            "type": "database_id",
            "database_id": db_id,
        },
        "properties": {
            "id": {"title": [{"text": {"content": str(idx)}}]},
            "payload": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": payload,
                        },
                    }
                ],
            },
        },
    }


def patch_page_schema(new_page):
    properties = new_page["properties"]
    new_page_payload = properties["payload"]["rich_text"][0]["text"]["content"]
    return {
        "properties": {
            "payload": {
                "type": "rich_text",
                "rich_text": [
                    {"type": "text", "text": {"content": new_page_payload}},
                ],
            }
        }
    }


def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def upload_payload_to_notion(
    headers: NotionHeaders,
    db_id: str,
    batch_idx: int,
    payload: str,
):
    NOTION_MAX_TEXT_SIZE = 2000
    assert len(payload) <= NOTION_MAX_TEXT_SIZE

    batched_page = new_page_schema(db_id, batch_idx, payload)
    response = requests.post(
        url="https://api.notion.com/v1/pages",
        json=batched_page,
        headers=headers.to_dict(),
    )
    print(response.status_code)
    if response.status_code != 200:
        print(response.reason)


def compressed_date(dates: list[dat.datetime], d: dat.datetime):
    # Base case: dates is len(0).
    if len(dates) == 0:
        date = str(d.year) + "\n" + str(d.month) + "\n" + str(d.day) + "\n"
    else:
        # Compare the date to the previous entry's date.
        # Sneaky one, but if two entries had the same day but on different months
        # we would still want to re-generate the month *and* day lines. So
        # the month and day checks assume the previous conditions are all true
        # as well. Similar for years.
        same_year = dates[-1].year == d.year
        same_month = dates[-1].month == d.month and same_year
        same_day = dates[-1].day == d.day and same_month and same_year

        year = str(d.year) + "\n" if not same_year else ""
        month = str(d.month) + "\n" if not same_month else ""
        day = str(d.day) + "\n" if not same_day else ""

        date = year + month + day

    # Add the tzinfo from the isoformat to avoid making mistakes.
    time = "T" + str(d.hour) + ":" + str(d.minute) + "+" + d.isoformat()[-5:]
    return date + time


def group_data(
    ts: list[dat.datetime],
    events: list[str],
) -> tuple[list[dat.datetime], list[list[str]]]:
    assert len(ts) == len(events), (
        f"ts and events have unequal length: {len(ts)} vs {len(events)}"
    )
    grouped_ts: list[dat.datetime] = [ts[0]]
    grouped_events: list[list[str]] = [[events[0]]]
    for t, e in zip(ts[1:], events[1:]):
        if t == grouped_ts[-1]:
            grouped_events[-1].append(e)
        else:
            grouped_ts.append(t)
            grouped_events.append([e])
    return grouped_ts, grouped_events


# This enables reading from a (chunked) database with good compression and
# substantially faster reads for older data, and only a small amount of syncing
# required with the slower database.
# This does assume the presence of a 'date' column in the un-chunked database,
# however. This enables the filtering on the slower database.
def get_notion_pages_from_db_sync_with_chunked(
    db_id: str,
    chunked_db_id: str,
    headers: NotionHeaders,
    extract_chunked_func: Callable,
    decompression_map: dict,
    compression_map: dict,
    extract_func: Callable,
    compress_func: Callable,
    patch_chunked_page: Callable,
    post_new_chunked_page: Callable,
):
    # Read all the data from chunked_db in ascending order of id.
    chunked_pages = get_notion_pages_from_db(
        chunked_db_id,
        headers,
        sort_column="id",
        sort_direction="ascending",
    )

    # Get the latest date from the chunked data.
    latest_chunked_page = [chunked_pages[-1]] if chunked_pages else []
    chunked_page_ts, chunked_page_events = get_all_entries_chunked(
        latest_chunked_page, extract_chunked_func, decompression_map
    )
    latest_chunked_date: dat.datetime | None = (
        chunked_page_ts[-1] if chunked_page_ts else None
    )
    chunked_page_id: str | None = chunked_pages[-1]["id"] if chunked_pages else None
    print(f"Latest chunked timestamp: {latest_chunked_date}")
    print(f"Latest chunked page ID: {chunked_page_id = }")

    # Read all the data from slower_db s.t. date >= latest chunked date.
    # Typicall this should be a small amount of data - only on an empty chunked
    # database should this pay the full cost of loading/syncing all the data.
    filter_by = None
    if latest_chunked_date:
        filter_by = {
            "property": "date",
            "date": {"on_or_after": latest_chunked_date.isoformat()},
        }
    unchunked_pages = get_notion_pages_from_db(
        db_id,
        headers,
        sort_column="date",
        sort_direction="ascending",
        filter_by=filter_by,
    )
    unchunked_ts, unchunked_events = get_all_entries(
        unchunked_pages,
        extract_func,
    )

    if not latest_chunked_date:
        # Useful debugging utility when creating a new chunked DB.
        unchunked_event_freqs = {}
        for event in unchunked_events:
            if event not in unchunked_event_freqs:
                unchunked_event_freqs[event] = 0
            unchunked_event_freqs[event] += 1
        print(f"{unchunked_event_freqs = }")

    earliest_unchunked = None if len(unchunked_ts) == 0 else unchunked_ts[0]
    latest_unchunked = None if len(unchunked_ts) == 0 else unchunked_ts[-1]
    print(f"Earliest unchunked timestamp: {earliest_unchunked}")
    print(f"Latest unchunked timestamp: {latest_unchunked}")

    # De-duplicate the data and transform into standardised chunked pages (i.e.
    # update the latest chunked page and add any new chunked pages).
    if latest_chunked_date:
        dedup_chunked_pairs = [
            (t, e)
            for t, e in zip(chunked_page_ts, chunked_page_events)
            if t < latest_chunked_date
        ]
        dedup_ts, dedup_events = zip(*dedup_chunked_pairs)
        chunked_page_ts = list(dedup_ts)
        chunked_page_events = list(dedup_events)

    ts = chunked_page_ts + unchunked_ts
    events = chunked_page_events + unchunked_events
    # Group data for better compression.
    grouped_ts, grouped_events = group_data(ts, events)
    new_chunked_pages = compress_event_data(
        grouped_ts,
        grouped_events,
        compression_map,
        chunked_db_id,
    )

    # PATCH/POST the latest chunked page and any new chunked pages.
    for idx, chunked_page in enumerate(new_chunked_pages):
        if idx == 0 and chunked_page_id:
            patch_chunked_page(
                headers,
                chunked_page_id,
                chunked_page,
            )
            continue
        post_new_chunked_page(
            headers,
            chunked_page,
        )

    # Return the chunked pages.
    return chunked_pages[:-1] + new_chunked_pages


def patch_chunked_page(
    headers: NotionHeaders,
    page_id: str,
    chunked_page: dict,
) -> None:
    patch_payload = patch_page_schema(chunked_page)
    response = requests.patch(
        url=f"https://api.notion.com/v1/pages/{page_id}",
        json=patch_payload,
        headers=headers.to_dict(),
    )
    print(response.status_code)
    if response.status_code != 200:
        print(response.reason)


def post_new_chunked_page(headers: NotionHeaders, chunked_page: dict) -> None:
    response = requests.post(
        url="https://api.notion.com/v1/pages",
        json=chunked_page,
        headers=headers.to_dict(),
    )
    print(response.status_code)
    if response.status_code != 200:
        print(response.reason)


def check_page_valid(page, idx):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")


def get_notion_date(page, property):
    properties = page["properties"]
    return dateutil.parser.isoparse(properties[property]["date"]["start"])


def get_notion_number(page, property):
    return page["properties"][property]["number"]


def get_notion_multi_select(page, property):
    items = page["properties"][property]["multi_select"]
    return [item["name"] for item in items]


def get_notion_text(page, property):
    properties = page["properties"]
    return properties[property]["rich_text"][0]["text"]["content"]


def extract_airflow_entry(timestamps, data, idx, page):
    check_page_valid(page, idx)
    ts = get_notion_date(page, "date")
    vals = [get_notion_number(page, f"recording_{i}") for i in [1, 2, 3]]
    timestamps.append(ts)
    data.append(vals)
    return None


def extract_categorical_entry(timestamps, data, idx, page):
    check_page_valid(page, idx)
    ts = get_notion_date(page, "date")
    categories = get_notion_multi_select(page, "category")
    for category in categories:
        timestamps.append(ts)
        data.append(category)
    return None


def extract_weight_entry(timestamps, data, idx, page):
    check_page_valid(page, idx)
    ts = get_notion_date(page, "date")
    weight = get_notion_number(page, "weight")
    categories = get_notion_multi_select(page, "category")
    timestamps.append(ts)
    data.append((weight, *categories))
    return None


def extract_sleep_entry(timestamps, data, idx, page):
    check_page_valid(page, idx)
    start = get_notion_date(page, "start_date")
    end = get_notion_date(page, "end_date")
    duration = get_notion_text(page, "duration")
    timestamps.append((start, end))
    data.append(duration)
    return None


def extract_pomodoro_entry(timestamps, data, idx, page):
    check_page_valid(page, idx)
    ts = get_notion_date(page, "date")
    pomodoro_length = get_notion_number(page, "pomodoro_length")
    break_length = get_notion_number(page, "break_length")
    score = get_notion_number(page, "score")
    comment = get_notion_text(page, "comment")
    categories = get_notion_multi_select(page, "category")
    timestamps.append(ts)
    data.append((pomodoro_length, break_length, score, comment, *categories))
    return None


def prepend_zero(s):
    return "0" + s if len(s) == 1 else s


def decompress_lines(lines, timestamps, data, idx, decompression_map):
    if lines == []:
        raise Exception(f"Found empty payload at page with index {idx}.")
    current_year = lines[0]
    current_month = prepend_zero(lines[1])
    current_day = prepend_zero(lines[2])

    counter = 3
    while counter < len(lines):
        current_line: str = lines[counter]
        # Four cases: line containing categories, a day line, a month line
        # followed by a day line, or a year line followed by etc.
        if current_line.isdigit():
            next_line = lines[counter + 1]
            has_month_line = next_line.isdigit()
            next_next_line = lines[counter + 2] if (counter + 2) < len(lines) else ""
            has_year_line = has_month_line and next_next_line.isdigit()

            if has_year_line:
                # year line
                current_year = current_line
                current_month = prepend_zero(next_line)
                current_day = prepend_zero(next_next_line)
                counter += 3
            elif has_month_line:
                # month line
                current_month = prepend_zero(current_line)
                current_day = prepend_zero(next_line)
                counter += 2
            else:
                # day line
                current_day = prepend_zero(current_line)
                counter += 1
            continue

        # Case when the line contains categories.
        date_component = f"{current_year}-{current_month}-{current_day}"

        # Add back in the 0s for the hour and minute.
        hour_component = current_line.split(":")[0][1:]
        hour_component = prepend_zero(hour_component)
        minute_component = (current_line.split("+")[0]).split(":")[-1]
        minute_component = prepend_zero(minute_component)
        time_component = f"{hour_component}:{minute_component}" + ":00.000"
        pattern = re.compile("\+\d{2}:\d{2}")
        timezone_component = pattern.search(current_line).group(0)
        datetime_component = f"{date_component}T{time_component}{timezone_component}"
        ts = dat.datetime.fromisoformat(datetime_component)
        categories = current_line.split(":")[-1].split(",")
        for category in categories:
            timestamps.append(ts)
            data.append(decompression_map[category])
        counter += 1


def extract_chunked_categorical_entry(
    timestamps,
    data,
    idx,
    page,
    decompression_map,
):
    check_page_valid(page, idx)
    try:
        text = get_notion_text(page, "payload")
        lines = text.split("\n")
        decompress_lines(
            lines,
            timestamps,
            data,
            idx,
            decompression_map,
        )
    except Exception as e:
        page_name = page["properties"]["id"]["title"][0]["text"]["content"]
        print(f"error raised for page {page_name}!")
        raise e
    return None


def get_all_entries(pages, add_data_entry):
    timestamps, data = [], []

    for idx, page in enumerate(pages):
        add_data_entry(timestamps, data, idx, page)

    return timestamps, data


def get_all_entries_chunked(pages, add_data_entry, decompression_map):
    timestamps, data = [], []

    for idx, page in enumerate(pages):
        add_data_entry(timestamps, data, idx, page, decompression_map)

    return timestamps, data


def get_n_weeks_ago(n):
    now = dat.datetime.now().astimezone()
    current_week_start = now - dat.timedelta(days=now.weekday())
    n_weeks_ago_start = current_week_start - dat.timedelta(weeks=n - 1)
    return n_weeks_ago_start


# TODO: Check how to perform copy-on padding with dataframes, in order to
# drop/simplify this function.
def get_moving_average_trend(data, k, padding="copy-on"):
    """
    Compute a moving average trend with window size `k` over over `data`.

    The padding used for the start and end is 'copy-on' - that is, the start
    and end values are duplicated akin to 'same' padding.
    """
    if padding != "copy-on":
        raise Exception("This type of padding is not supported!")

    if k % 2 == 0 or k == 1:
        raise Exception("k must be an odd number greater than 1!")

    j = (k - 1) / 2
    padded_data = np.concatenate(
        [np.repeat(data[0], j), data, np.repeat(data[-1], j)], axis=0
    )
    rolling_average = np.convolve(padded_data, np.ones(k) / k, "valid")
    return rolling_average


# TODO: Figure out how to append to KDE plots so that the lines all start and
# end at the same place.
# TODO: Figure out how to 'project'/'predict' for recent data. Look into
# conditional density estimation.
def kde_over_all_categories(ts, events, bw_vals, combine=[], exclude=[]):
    # Share the same axes across the various plots.
    _, ax = plt.subplots(1)
    for category, bw in zip(set(events), bw_vals):
        if category in exclude:
            continue
        # Fetch all timestamps where the event matches the category.
        cat_ts = list(
            map(
                lambda tup: tup[1],
                filter(lambda tup: tup[0] == category, zip(events, ts)),
            )
        )
        cat_timeframe = cat_ts[-1] - cat_ts[0]
        total_timeframe = ts[-1] - ts[0]
        # Exclude short-lived KDEs - these tend to skew the graphs.
        if cat_timeframe < (0.3 * total_timeframe):
            continue
        df = pd.DataFrame(cat_ts, columns=["dates"])
        df["ordinal"] = [x.toordinal() for x in df.dates]
        ax = df["ordinal"].plot(
            kind="kde",
            bw_method=bw,
            ax=ax,
            label=category,
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Density")
    ax.set_xlim(ts[0].toordinal(), ts[-1].toordinal())

    # Take every other tick to reduce clutter.
    x_ticks = ax.get_xticks()[::2]
    ax.set_xticks(x_ticks)
    xlabels = list(
        map(
            lambda x: dat.datetime.fromordinal(int(x)).strftime("%Y-%m-%d"),
            x_ticks,
        )
    )
    ax.set_xticklabels(xlabels)
    ax.legend()
    return ax


def kde_over_combined_categories(ts, bw):
    df = pd.DataFrame(set(ts), columns=["dates"])
    df["ordinal"] = [x.toordinal() for x in df.dates]
    ax = df["ordinal"].plot(kind="kde", bw_method=bw, label="Combined")

    ax.set_xlabel("Time")
    ax.set_ylabel("Density")
    ax.set_xlim(ts[0].toordinal(), ts[-1].toordinal())

    # Take every other tick to reduce clutter.
    x_ticks = ax.get_xticks()[::2]
    ax.set_xticks(x_ticks)
    xlabels = list(
        map(
            lambda x: dat.datetime.fromordinal(int(x)).strftime("%Y-%m-%d"),
            x_ticks,
        )
    )
    ax.set_xticklabels(xlabels)
    ax.legend()
    return ax


def day_kde_over_all_categories(ts, events, bw_vals, exclude):
    # Share the same axes across the various plots.
    _, ax = plt.subplots(1, figsize=(8, 6))
    for category, bw in zip(set(events), bw_vals):
        if category in exclude:
            continue
        # Fetch all timestamps where the event matches the category.
        cat_ts = list(
            map(
                lambda tup: tup[1],
                filter(lambda tup: tup[0] == category, zip(events, ts)),
            )
        )
        cat_timeframe = cat_ts[-1] - cat_ts[0]
        total_timeframe = ts[-1] - ts[0]
        # Exclude short-lived KDEs - these tend to skew the graphs.
        if cat_timeframe < (0.3 * total_timeframe):
            continue

        df = pd.DataFrame(cat_ts, columns=["dates"])
        df["time"] = pd.to_datetime(df["dates"], utc=True).dt.time
        df["time_delta"] = pd.to_timedelta([str(t) for t in df["time"]])
        df["time_delta_float"] = df["time_delta"] // pd.Timedelta(minutes=1)
        # Default size of the graph makes the labels too large, might as well
        # have a bigger plot.
        ax = df["time_delta_float"].plot(
            kind="kde",
            bw_method=bw,
            label=category,
            ax=ax,
        )

    ax.set_xlabel("Time (Clock)")
    ax.set_ylabel("Density")

    ax.set_xlim(0, pd.Timedelta(days=1) // pd.Timedelta(minutes=1))
    hours = [i for i in range(0, 25, 2)]
    ax.set_xticks(
        [i * 60 for i in hours], [str(i).rjust(2, "0") + ":00" for i in hours]
    )
    ax.set_yticks([])
    ax.legend()
    return ax


def day_kde_over_combined_categories(ts, bw):
    df = pd.DataFrame(set(ts), columns=["dates"])
    df["time"] = pd.to_datetime(df["dates"], utc=True).dt.time
    df["time_delta"] = pd.to_timedelta([str(t) for t in df["time"]])
    df["time_delta_float"] = df["time_delta"] // pd.Timedelta(minutes=1)
    # Default size of the graph makes the labels too large, might as well have
    # a bigger plot.
    _, ax = plt.subplots(1, figsize=(8, 6))
    ax = df["time_delta_float"].plot(
        kind="kde",
        bw_method=bw,
        label="Combined",
        ax=ax,
    )

    ax.set_xlabel("Time (Clock)")
    ax.set_ylabel("Density")

    ax.set_xlim(0, pd.Timedelta(days=1) // pd.Timedelta(minutes=1))
    hours = [i for i in range(0, 25, 2)]
    ax.set_xticks(
        [i * 60 for i in hours], [str(i).rjust(2, "0") + ":00" for i in hours]
    )
    ax.set_yticks([])
    ax.legend()
    return ax


def week_kde_over_all_categories(ts, events, bw_vals, combine=[], exclude=[]):
    _, ax = plt.subplots(1, figsize=(8, 6))
    for category, bw in zip(set(events), bw_vals):
        if category in exclude:
            continue
        # Fetch all timestamps where the event matches the category.
        cat_ts = list(
            map(
                lambda tup: tup[1],
                filter(lambda tup: tup[0] == category, zip(events, ts)),
            )
        )
        df = pd.DataFrame(cat_ts, columns=["dates"])
        df["day"] = pd.to_datetime(df["dates"], utc=True).dt.day_of_week + 0.5
        # Default size of the graph makes the labels too large, might as well
        # have a bigger plot.
        ax = df["day"].plot(
            kind="kde",
            bw_method=bw,
            label=category,
            ax=ax,
        )

    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Density")

    days_of_week = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    offsets = [i + 0.5 for i in range(len(days_of_week))]
    ax.set_xlim(0, len(days_of_week))
    ax.set_xticks(offsets, [(d + "day").title() for d in days_of_week])
    ax.legend()
    ax.grid()
    return ax


def week_kde_over_combined_categories(ts, bw):
    df = pd.DataFrame(set(ts), columns=["dates"])
    df["day"] = pd.to_datetime(df["dates"], utc=True).dt.day_of_week + 0.5
    _, ax = plt.subplots(1, figsize=(10, 4))
    ax = df["day"].plot(
        kind="kde",
        bw_method=bw,
        label="Combined",
        ax=ax,
    )

    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Density")

    days_of_week = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    offsets = [i + 0.5 for i in range(len(days_of_week))]
    ax.set_xlim(0, len(days_of_week))
    ax.set_xticks(offsets, [(d + "day").title() for d in days_of_week])
    y_max = max(ax.get_lines()[0].get_xydata()[:, 1])
    num_y_ticks = 4
    y_interval = round(y_max / num_y_ticks, ndigits=2)
    ax.set_yticks([y_interval * (i + 1) for i in range(num_y_ticks + 1)])
    ax.set_ylim(0.0, y_max * 1.5)
    ax.legend()
    ax.grid()
    return ax


def get_aggregated_event_counts(ts, events, period):
    data = {"value": [1] * len(events), "categories": events, "date": ts}
    df = pd.DataFrame(data)
    # Make sure to set the date column to datetimes recognisable by pandas.
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.pivot_table(
        index="date", columns="categories", values="value", aggfunc="sum"
    )
    if period.lower() not in ["monthly", "weekly", "daily"]:
        raise Exception("Period argument not recognised")

    if period == "monthly":
        grouped_df = df.groupby([pd.Grouper(freq="ME")]).sum()

    if period == "weekly":
        df.index = df.index - pd.to_timedelta(7, unit="d")
        grouped_df = df.groupby([pd.Grouper(freq="W")]).sum()

    if period == "daily":
        grouped_df = df.groupby([pd.Grouper(freq="D")]).sum()

    return grouped_df


# TODO: Add 'get all events where equal to' function. Do not want a dense df.


def populate_with_events(ax, events, from_date):
    for event in events:
        event_date, event_colour, event_style, event_label = event
        if event_date < from_date:
            continue
        ax.axvline(
            event_date,
            color=event_colour,
            linestyle=event_style,
            linewidth=1,
            label=event_label,
        )
    return ax


def plot_category(
    title, df, categories, window_size, round_size, round_unit, from_date=None
):
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_title(title)
    for category in categories:
        if from_date is not None:
            ax = df[from_date:].plot(y=category, ax=ax)
        else:
            ax = df.plot(y=category, ax=ax)
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency")
    ax.legend(
        [
            f"{category} ({str(round_size) + round_unit}, k={window_size})"
            for category in categories
        ],
    )
    return fig, ax
