 # Select user state and try to select District if possible
        state_in_data = False
        district_in_data = False

        if state and state in markets:
            search_space = markets[state]
            state_in_data = True
        else:
            search_space = markets

        if state_in_data and district:
            if district in search_space:
                search_space = search_space[district]
                district_in_data = True

        if state_in_data and district_in_data:
            for market in search_space:
                if not market or len(market) < 2: continue

                market_coord = (market[0], market[1])

                dist_to_user = calculate_distance((lat, lon), market_coord)

                if dist_to_user < min_distance:
                    min_distance = dist_to_user
                    nearest_market = market
        elif state_in_data:
            for district in search_space:
                for market in district:
                    if not market or len(market) < 2: continue

                    market_coord = (market[0], market[1])

                    dist_to_user = calculate_distance((lat, lon), market_coord)

                    if dist_to_user < min_distance:
                        min_distance = dist_to_user
                        nearest_market = market
        else:
            for state in search_space:
                for district in state:
                    for market in district:
                        if not market or len(market) < 2: continue

                        market_coord = (market[0], market[1])

                        dist_to_user = calculate_distance((lat, lon), market_coord)

                        if dist_to_user < min_distance:
                            min_distance = dist_to_user
                            nearest_market = market

        return {nearest_market, min_distance}
    except Exception as e:
        raise e

def main():
    # test
    print("Getting location info for various coordinates: ")
    coords = [
        [30.74632, 76.64689],
        [31.583, 78.417],
        [9.85, 76.94]
    ]

    for i, (lat, lon) in enumerate(coords):
        res = get_nearest_market(lat, lon)
        print(f"Nearest market for coord {i}: {res}")

if __name__ == "__main__":
    main()