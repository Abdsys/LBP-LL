import numpy as np
import pandas as pd

def calculate_price(usd_balance, ll_balance, ll_weight, usdc_weight, lot_size, swap_fee):
    if ll_balance <= lot_size:
        return float('inf')
    price = (usd_balance * ((ll_balance / (ll_balance - lot_size)) ** (ll_weight / usdc_weight) - 1)) / \
            (1 - swap_fee) / lot_size
    return price

# Inputs
initial_token_balance = 50000000
initial_usd_balance = 300000
start_weights = (0.99, 0.01)
lot_size = 10000
swap_fee = 0.02
steps = 72  # 3 days, 24 hours each

# Create an empty list to store results
results_list = []

# Create an array of ending weights combinations
ending_weights_combinations = np.linspace((0.01, 0.99), (0.5, 0.5), 50)

# Loop over different ending weights combinations
for end_weight in ending_weights_combinations:
    # Loop over different sale rates (1% to 99%)
    for total_sale_rate_percent in np.arange(0.01, 1.00, 0.01):
        # Calculate total sale tokens based on the total sale rate
        total_sale_tokens = initial_token_balance * total_sale_rate_percent

        # Split the total sale tokens across three days
        daily_sale_tokens = [total_sale_tokens * p for p in [0.20, 0.30, 0.50]]

        price_curve = []
        token_balances = [initial_token_balance]
        usd_balances = [initial_usd_balance]

        # Simulation over 3 days (72 hours)
        for day in range(3):
            # Randomly divide the daily sale amount into 24 steps
            hourly_sale_tokens = np.random.dirichlet(np.ones(24), 1).flatten() * daily_sale_tokens[day]

            for hour in range(24):
                step = day * 24 + hour
                current_ll_weight = start_weights[0] + (end_weight[0] - start_weights[0]) * (step / steps)
                current_usdc_weight = start_weights[1] + (end_weight[1] - start_weights[1]) * (step / steps)

                # Calculate price
                price = calculate_price(usd_balances[-1], token_balances[-1], current_ll_weight, current_usdc_weight, lot_size, swap_fee)

                # Ensure not to sell more than available tokens
                hourly_sale_amount = min(hourly_sale_tokens[hour], token_balances[-1])

                # Print hourly sale amount for verification
                print(f"Day {day+1}, Hour {hour+1}: Sale Amount = {hourly_sale_amount:.2f} tokens")

                # Update balances
                usd_received = hourly_sale_amount * price
                new_token_balance = token_balances[-1] - hourly_sale_amount
                new_usd_balance = usd_balances[-1] + usd_received
                token_balances.append(new_token_balance)
                usd_balances.append(new_usd_balance)

                price_curve.append(price)

        # Calculate total proceeds and unsold tokens
        total_proceeds = usd_balances[-1] - initial_usd_balance
        unsold_tokens = token_balances[-1]

        # Calculate the minimum price from the ending balances
        end_ll_weight = start_weights[0] + (end_weight[0] - start_weights[0])
        end_usdc_weight = start_weights[1] + (end_weight[1] - start_weights[1])
        min_price = calculate_price(usd_balances[-1], token_balances[-1], end_ll_weight, end_usdc_weight, lot_size, swap_fee)

        # Append results to the list
        results_list.append({
            'Ending Weight Token': end_weight[0],
            'Ending Weight USD': end_weight[1],
            'Sale Rate': total_sale_rate_percent,
            'Total Proceeds': total_proceeds,
            'Unsold Tokens': unsold_tokens,
            'Min Price': min_price
        })

# Convert to DataFrame
results_df = pd.DataFrame(results_list)

# Save to CSV
results_df.to_csv('lbp_results_random_sale.csv', index=False)
