# A game setup helper for the Pirates! constructable strategy game.
# The purpose of this script is to calculate a recommended number of
#   Home starting islands
#   Wild Islands
#   Number of coins
#   Total treasure value from coins
#   Distribution of treasure values on the coins
# From a given number of players for a game.
import math
from collections import Counter

# Define the base values for each part of the game as stated in the official rules.
BASE_POINTS = 40
BASE_ISLANDS = 3
BASE_COINS = 8
BASE_TREASURE = 15

def main():
    print("Welcome to the Pirates CSG game setup helper.\n---------------------------------------------")

    # Prompt the user to input values needed to calculate their game values.
    # The max values are relatively arbitrary.
    players = getIntInputInRange(2, 20, "Enter the number of players for your game: ")
    points = getIntInputInRange(10, 1000, "Enter the number of points available for each player's fleet: ")
    maxCoinVal = getIntInputInRange(2, 7, "What is the largest valued coin you wish to be in the treasure? \nMaximum value is 7, minimum value is 2, recommended is 4.\n")

    # Determine a multiplier for all values from the ratio of the input fleet points to official rules fleet points.
    multiplier = points / BASE_POINTS

    # Get simple derived values from the input values.
    totalIslands = math.ceil(BASE_ISLANDS * players * multiplier)
    totalCoins = math.ceil(BASE_COINS * players * multiplier)
    totalTreasure = math.ceil(BASE_TREASURE * players * multiplier)
    wildIslands = totalIslands - players
    averageCoinPerIsland = totalCoins / wildIslands

    # Calculate the recommended coin distribution
    coinDistribution = getCoinDistribution(totalCoins, totalTreasure, players, maxCoinVal)

    # Construct strings and print all calculated values
    coinDistributionStr = "Coin Distribution:\n"
    for key, value in coinDistribution:
        coinDistributionStr += ("    # of " + str(key) + " value coins: " + str(value) + "\n")
    
    outputStrList = ["for a " + str(players) + " player game with " + str(points) + " point fleets:",
    "----------------------------------------------------",
    "Total Islands: " + str(totalIslands),
    "    Home Islands: " + str(players),
    "    Wild Islands: " + str(wildIslands),
    "Coins: " + str(totalCoins),
    "    Total treasure value: " + str(totalTreasure),
    "    Average # of coins per wild island: " + str(round(averageCoinPerIsland, 1)),
    coinDistributionStr]

    print("\n".join(outputStrList))


def getIntInputInRange(min, max, inputMessage):
    while True:
        try:
            num = int(input(inputMessage))
            if (num <= max and num >= min):
                return num
            else:
                raise ValueError("Input exceeded the minimum or maximum value.")
        except ValueError:
            print("That was not a valid input, try again.")
    

def getCoinDistribution(totalCoins, totalTreasure, players, maxCoinVal):
    # Official rules state that players select their coins in such a fashion that their total value equals the treasure value per player.
    # I instead wish to calculate recommended coins to select.
    # A mathmatician somewhere has probably written a proof and paper on how to fill x size with y items of smaller sizes along curve z.
    # But I do not know of it, so I made my own algorithm.
    # My preference is for a majority of coins to be of low value and a small number to be of the max value, with a geometric-ish curve in-between.
    # So I developed my algorithm to create that kind of outcome.
    coinList = []

    countdownCoin = maxCoinVal
    while (countdownCoin > 0):
        coinQty = countdownCoin

        # Make the candidate list
        # We will need to check to see if it has too many coins or value
        # compared to the remaining coins or value before officially adding it.
        # if so, we reduce the maximum coin value, and try again.
        candidateCoinList = []

        # Add a number and value of coins based on the max value coin
        # For example, if the max value coin is 5, add five 1 valued coins, then four 2 valued coins,
        # And so on until we add one 5 valued coin and cannot decrement any more.
        for i in range(1, countdownCoin + 1):
            while(coinQty > 0):
                candidateCoinList.append(i)
                coinQty -= 1

            # Set the coin quanitity for the next batch to add.
            coinQty = countdownCoin - i

        # Check to see if the number and total value of coins added can be added again.
        if (len(coinList) + len(candidateCoinList) < totalCoins and
                sum(coinList) + sum(candidateCoinList) < totalTreasure):
            coinList += candidateCoinList
        # If not, try again with a smaller range
        else:
            countdownCoin -= 1

    # There may be coins and treasure value remaining after this.
    # Check to see which is greater, as they require different actions.
    remainingCoins = totalCoins - len(coinList)
    remainingTreasure = totalTreasure - sum(coinList)

    # If there is more total treasure to add than coins to add...
    if (remainingCoins <= remainingTreasure):
        # add 1 value coins until one coin remains.
        remainingCoins = totalCoins - len(coinList)
        remainingTreasure = totalTreasure - sum(coinList)
        for i in range(1, remainingCoins):
            coinList.append(1)
            remainingTreasure -= 1
            
        # Then, so long as the remaining value is less than the max value coin,
        # add one final coin of that value.
        # Otherwise, add the max value coin, then begin enhancing coins by +1,
        # starting with the lowest value coins and moving to larger value ones.
        # (TODO: maybe it would be better to use the 'coins encountered' method like in the else case below?)
        if (remainingTreasure <= maxCoinVal):
            coinList.append(remainingTreasure)
        else:
            coinList.append(maxCoinVal)
            remainingTreasure -= maxCoinVal
            coinList.sort()

            while (remainingTreasure != 0):
                coinList[i] = coinList[i] + 1
                remainingTreasure -= 1
                i += 1
    else:
        # If there is more coins than treasure value left, some existing coins must have their value reduced.
        # Add as many 1 value coins as possible to meet the total coins. This will make the remaining treasure negative.
        for i in range(0, remainingCoins):
            coinList.append(1)
            remainingCoins -= 1
            remainingTreasure -= 1

        # Sort the coin list so that the low value coins are at the front.
        coinList.sort()

        # Iterate through the list, and subtract 1 from the first coin found of each distinct value.
        i = 0
        coinsEncountered = []
        while (remainingTreasure != 0):
            currentCoin = coinList[i]
            if (currentCoin not in coinsEncountered):
                coinsEncountered.append(currentCoin)

                # If we haven't encountered the coin in this iteration, subtract 1 from its value
                # We cannot decrease the value of 1 coins, and should not decrease the value of max coins.
                if(coinList[i] != 1 and coinList[i] != maxCoinVal):
                    coinList[i] = currentCoin - 1
                    remainingTreasure += 1
            i += 1

            # If the whole coin list has been iterated and the remaining treasure has not been met,
            # clear the encountered list and start again.
            if (i == len(coinList)):
                coinsEncountered.clear()
                i = 0

    return sorted(Counter(coinList).items())


main()

