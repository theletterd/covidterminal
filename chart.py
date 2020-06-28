import requests
import datetime
from asciichartpy import plot

US_DATA_URL = "https://covidtracking.com/api/v1/us/daily.csv"
#US_STATE_DATA_URL = "https://covidtracking.com/api/v1/states/daily.csv"


def get_data():
    csv_data = requests.get(US_DATA_URL).text.split()
    DATE_INDEX = 0
    DAILY_INCREASE_INDEX = 22 # "positiveIncrease"

    datapoints = []
    dates = []
    csv_data.pop(0) # remove headers

    for row in csv_data:
        row_data = row.split(',')
        unformatted_date = row_data[DATE_INDEX]
        increase = int(row_data[DAILY_INCREASE_INDEX])
        date = datetime.datetime.strptime(unformatted_date, "%Y%m%d").date()

        dates.append(date)
        datapoints.append(increase)

    datapoints.reverse()
    dates.reverse()
    return dates, datapoints


def print_chart(dates, datapoints):
    print("\nCOVID-19 cases in the USA, over time\n\n")
    print(plot(datapoints, dict(height=30, format="{:8.0f}")))


def print_latest_values(dates, datapoints, num_latest=10):
    print("\n\n")
    print(f"Latest {num_latest} values:")

    latest_values = list(zip(dates[-num_latest:], datapoints[-num_latest:]))
    latest_values.reverse()

    for date, value in latest_values:
        formatted_date = date.isoformat()
        print(f"{formatted_date}: {value}")
    print("\n\n")

dates, datapoints = get_data()
print_chart(dates, datapoints)
print_latest_values(dates, datapoints)
