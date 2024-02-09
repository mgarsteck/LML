import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim as optim
import mysql.connector

import math
import numpy as np


def mean_normalize(data, mean_vals, range_vals):
    return (data - mean_vals) / range_vals


def load_dataset():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234567",
        database="markets"
    )

    cursor = connection.cursor()

    candles_query = "SELECT * FROM coinbase_ETHUSD_1 ORDER BY time"
    cursor.execute(candles_query)
    candles = cursor.fetchall()
    print(f"{len(candles)} Candles \n")
    # Limit to 1000 candles
    candles = candles[:1000]

    # Assuming make_trendlines is a function defined elsewhere that you're using
    trends = make_trendlines(candles)

    cursor.close()
    connection.close()

    # Split the data into 80:20 training and test
    split_index = math.floor(len(candles) * 0.8)
    candles_training = candles[:split_index]
    candles_test = candles[split_index:]

    print(len(candles), "candles", len(trends), "Trends")
    trends_training = trends[:split_index]
    trends_test = trends[split_index:]

    # Extract the relevant features from candles
    candles_training = np.array([[candle[1], candle[2], candle[3], candle[4]] for candle in candles_training])
    candles_test = np.array([[candle[1], candle[2], candle[3], candle[4]] for candle in candles_test])

    # Calculate mean and range for mean normalization using training data
    mean_vals = np.mean(candles_training, axis=0)
    range_vals = np.max(candles_training, axis=0) - np.min(candles_training, axis=0)

    # Normalize the candles data
    candles_training_normalized = mean_normalize(candles_training, mean_vals, range_vals)
    candles_test_normalized = mean_normalize(candles_test, mean_vals, range_vals)

    # Convert normalized candles data to tensors
    X_train_tensor = torch.tensor(candles_training_normalized, dtype=torch.float)
    X_test_tensor = torch.tensor(candles_test_normalized, dtype=torch.float)

    # Convert trends data to tensors
    y_train_tensor = torch.tensor(trends_training, dtype=torch.float)
    y_test_tensor = torch.tensor(trends_test, dtype=torch.float)

    return X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor


# Build trendlines by hand for validation
def make_trendlines(candles):
    trendlines = []
    ts = 1
    trend_state = []

    for index, candle in enumerate(candles):
        # print("CANDLE", candle)
        if candle[4] > candle[1]:
            # print("HIGHER")
            ts = 1
        else:
            # print("LOWER", candle[1], candle[2])
            ts = 0
        trend_state.append(ts)
        # print("TrendSTATE", ts, trend_state)

        # print("CANDLE", index, candle) # [t, o, h, l, c, v]
        # if index == 0:
        #     current = {
        #         "Time": candles[0][0],
        #         "Point": candles[0][2],
        #         "Inv": candles[0][3],
        #         "Direction": -1 if candles[0][2] < candles[0][3] else 1,
        #     }
        #     trendlines.append(current)
        #     trend_state.append(-1 if candles[0][2] < candles[0][3] else 1)
        #     pass
        # else:
        #     # Higher High in uptrend  (continuation)
        #     if candle[2] > current["Point"] and current["Direction"] == 1:
        #         current = {
        #             "Time": candle[0],
        #             "Point": candle[2],
        #             "Inv": candle[3],
        #             "Direction": 1,
        #         }
        #         ts = 1

                
        #     # Higher High in downtrend  (new trend)
        #     if (candle[2] > current["Inv"]  and current["Direction"] == 0):
        #         current = {
        #             "Time": candle[0],
        #             "Point": candle[2],
        #             "Inv": candle[3],
        #             "Direction": 0 if candle[2] < candle[3] else 1,
        #         }
        #         ts = 1
                
        #     # Lower Low in uptrend (new trend)
        #     if (candle[3] < current["Inv"]  and current["Direction"] == 1):
        #         current = {
        #             "Time": candle[0],
        #             "Point": candle[3],
        #             "Inv": candle[2],
        #             "Direction": 0 if candle[2] < candle[3] else 1,
        #         }
        #         ts = 0

                
                
        #     # Lower Low in downtrend  (continuation)
        #     if candle[3] < current["Point"] and current["Direction"] == 0:
        #         current = {
        #             "Time": candle[0],
        #             "Point": candle[3],
        #             "Inv": candle[2],
        #             "Direction": 0 if candle[2] < candle[3] else 1,
        #         }
        #         ts = 0


        #     # Janky fix to get over skipping trends that have the same unique time for start and end
        #     # if current["StartTime"] == current["EndTime"]:
        #     #     current["StartTime"] -= 1
        #     trendlines.append(current)
        #     # print("CANDLE LENGTH", len(current))
        #     # print("TREND", ts)
        #     trend_state.append(ts)
            
        # # print("Trendline", current, "\n")
    return trend_state
