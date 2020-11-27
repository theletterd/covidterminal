import argparse
import requests
import datetime
import shutil
import math
from asciichartpy import plot

US_DATA_URL = "https://covidtracking.com/api/v1/us/daily.csv"
US_STATE_DATA_URL = "https://covidtracking.com/api/v1/states/daily.csv"
METRIC_CHOICES = ["positiveIncrease", "positive", "deathIncrease", "death", "hospitalized", "hospitalizedIncrease", "hospitalizedCurrently", "hospitalizedCumulative"]

class CovidData(object):

    def __init__(self):
        self.setup_parser()
        self.process_args()

    def setup_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--state", type=str, help="2-character State")
        parser.add_argument(
            "--metric",
            type=str,
            help="metric to draw",
            choices=METRIC_CHOICES,
            default=METRIC_CHOICES[0]
        )
        self.args = parser.parse_args()

    def process_args(self):
        self.state = self.args.state
        self.metric = self.args.metric


    def get_data(self, metric, state):
        url = US_DATA_URL
        if state:
            url = US_STATE_DATA_URL

        # TODO don't download the data every time, cache it locally.
        # maybe just save to a file, and then check against modified time
        csv_data = requests.get(url).text.split('\n')
        headers = csv_data.pop(0).split(',') # remove headers

        DATE_INDEX = headers.index("date")
        DAILY_INCREASE_INDEX = headers.index(metric)
        STATE_INDEX = None
        if state:
            STATE_INDEX = headers.index('state')

        datapoints = []
        dates = []

        for row in csv_data:
            row_data = row.split(',')
            # skip over rows (usually the last row) that doesn't have the right number of entries
            if len(row_data) != len(headers):
                continue

            # if we're looking at one state's data, only show that
            if state and state != row_data[STATE_INDEX]:
                continue

            unformatted_date = row_data[DATE_INDEX]
            try:
                increase = int(row_data[DAILY_INCREASE_INDEX])
                date = datetime.datetime.strptime(unformatted_date, "%Y%m%d").date()
            except:
                increase = 0

            dates.append(date)
            datapoints.append(increase)

        datapoints.reverse()
        dates.reverse()

        # how many leading zeros do we have?
        zeros = 0
        for i in datapoints:
            if i != 0:
                break
            zeros += 1
        return dates[zeros:], datapoints[zeros:]

    def print_chart(self, dates, datapoints, metric, state=None):
        state_string = state or "the USA"
        print(f"\nCOVID-19 {metric} in {state_string}, over time\n\n")
        print(plot(datapoints, dict(height=30, format="{:8.0f}")))

    def print_latest_values(self, dates, datapoints, num_latest=10):
        print("\n\n")
        print(f"Latest {num_latest} values:")

        latest_values = list(zip(dates[-num_latest:], datapoints[-num_latest:]))
        latest_values.reverse()

        for date, value in latest_values:
            formatted_date = date.isoformat()
            print(f"{formatted_date}: {value}")
        print("\n\n")

    def scale_data(self, dates, datapoints):
        columns, _ = shutil.get_terminal_size()
        MARGIN = 12
        scale_factor = math.ceil(len(datapoints) / (columns - MARGIN))
        print("Scale factor: " + str(scale_factor))

        chunks = []
        for i in range(0, len(datapoints), scale_factor):
            chunk = datapoints[i:i+scale_factor]
            chunks.append(chunk)

        mean_chunks = [(sum(chunk) / len(chunk)) for chunk in chunks]
        trimmed_dates = dates[::scale_factor]
        return trimmed_dates, mean_chunks

    def show_data(self):
        state = self.state
        metric = self.metric
        dates, datapoints = self.get_data(metric, state)

        scaled_dates, scaled_datapoints = self.scale_data(dates, datapoints)
        self.print_chart(scaled_dates, scaled_datapoints, metric, state=state)
        self.print_latest_values(dates, datapoints)


if __name__ == '__main__':
    CovidData().show_data()
