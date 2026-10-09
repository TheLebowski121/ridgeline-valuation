import requests
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("MARKETCHECK_API_KEY", "").strip()

if api_key:
    print("API key loaded successfully.")
else:
    print("API key missing. Check your .env file.")

if not api_key:
    raise SystemExit("API key missing. Check your .env file.")

search_params = {
    "api_key": api_key,
    "car_type": "used",
    "make": "Honda",
    "model": "Ridgeline",
    "year_range": "2006-2014",
    "zip": "94559",
    "radius": 100,
    "rows": 50,
    "start": 0,
}
all_usable = []
try:
    for page in range(2):
        search_params["start"] = page * 50

        response = requests.get(
            "https://api.marketcheck.com/v2/search/car/recents",
            params=search_params,
            timeout=30,
        )

        print(f"HTTP status: {response.status_code}")

        if response.status_code != 200:
            print("Search unsuccessful. Stopping.")
            break

        data = response.json()
        listings = data.get("listings", [])

        print(f"Page {page + 1}: {len(listings)} listings")
        usable = [
            listing for listing in listings
            if listing.get("price") is not None
            and listing.get("miles") is not None
        ]
        print(f"Listings with price and mileage: {len(usable)}")
        all_usable.extend(usable)
        for listing in usable:
            print("Vehicle:", listing.get("heading"))
            print("Price:", listing.get("price"))
            print("Mileage:", listing.get("miles"))
            print("VIN:", listing.get("vin"))
            print("First seen:", listing.get("first_seen_at_date"))
            print("Last seen:", listing.get("last_seen_at_date"))
            print("Listing URL:", listing.get("vdp_url"))
            print()

        if len(listings) < 50:
            break

except requests.RequestException:
    print("Could not complete the request. Check your connection.")

print(f"Total listings with price and mileage: {len(all_usable)}")
target_mileage = 270453
closest_by_mileage = sorted(
    all_usable,
    key=lambda listing: abs(listing["miles"] - target_mileage),
)
print("\nFive closest listings by mileage:")

for listing in closest_by_mileage[:5]:
    print("Vehicle:", listing.get("heading"))
    print("Price:", listing["price"])
    print("Mileage:", listing["miles"])
    print("Mileage gap:", abs(listing["miles"] - target_mileage))
    print("VIN:", listing.get("vin"))
    print("First seen:", listing.get("first_seen_at_date"))
    print("Last seen:", listing.get("last_seen_at_date"))
    print("Listing URL:", listing.get("vdp_url"))
    print()
vins = [listing.get("vin") for listing in all_usable if listing.get("vin")]
print(f"Listings with VINs: {len(vins)}")
print(f"Unique VINs: {len(set(vins))}")
print(f"Listings missing a VIN: {len(all_usable) - len(vins)}")
print("\nVehicle details for the closest listing:")
if closest_by_mileage:
    print(closest_by_mileage[0].get("build", {}))
same_year_trim = [
    listing for listing in all_usable
    if listing.get("build", {}).get("year") == 2010
    and listing.get("build", {}).get("trim") == "RT"
]
print(f"2010 RT listings with price and mileage: {len(same_year_trim)}")
for listing in same_year_trim:
    print("Vehicle:", listing.get("heading"))
    print("Price:", listing["price"])
    print("Mileage:", listing["miles"])
    print("Drivetrain:", listing.get("build", {}).get("drivetrain"))
    print("VIN:", listing.get("vin"))
    print("First seen:", listing.get("first_seen_at_date"))
    print("Last seen:", listing.get("last_seen_at_date"))
    print("Listing URL:", listing.get("vdp_url"))

same_trim = [
    listing for listing in all_usable
    if listing.get("build", {}).get("trim") == "RT"
    and listing.get("build", {}).get("drivetrain") == "4WD"
]
print(f"RT 4WD listings across all searched years: {len(same_trim)}")
for listing in sorted(
    same_trim,
    key=lambda listing: abs(listing["miles"] - target_mileage),
):
    print("Vehicle:", listing.get("heading"))
    print("Price:", listing["price"])
    print("Mileage:", listing["miles"])
    print("Mileage gap:", abs(listing["miles"] - target_mileage))
    print("VIN:", listing.get("vin"))
    print()
high_mileage = [
    listing for listing in all_usable
    if listing["miles"] >= 200000
]
print(f"Listings with at least 200,000 miles: {len(high_mileage)}") 

for listing in sorted(high_mileage, key=lambda item: item["miles"], reverse=True):
    print("Vehicle:", listing.get("heading"))
    print("Trim:", listing.get("build", {}).get("trim"))
    print("Price:", listing["price"])
    print("Mileage:", listing["miles"])
    print("VIN:", listing.get("vin"))
    print("First seen:", listing.get("first_seen_at_date"))
    print("Last seen:", listing.get("last_seen_at_date"))
    print("Listing URL:", listing.get("vdp_url"))
    print()
same_year = [
    listing for listing in all_usable
    if listing.get("build", {}).get("year") == 2010
]
print(f"2010 listings across all trims: {len(same_year)}")
for listing in sorted(same_year, key=lambda item: item["miles"], reverse=True):
    print("Trim:", listing.get("build", {}).get("trim"))
    print("Price:", listing["price"])
    print("Mileage:", listing["miles"])
    print("VIN:", listing.get("vin"))
    print()
year_counts = {}
for listing in all_usable:
    year = listing.get("build", {}).get("year")
    year_counts[year] = year_counts.get(year, 0) + 1

print("Listings by model year:", year_counts)
trim_counts = {}
for listing in all_usable:
    trim = listing.get("build", {}).get("trim") or "Unknown"
    trim_counts[trim] = trim_counts.get(trim, 0) + 1

print("Listings by trim:", trim_counts)
for trim in trim_counts:
    mileages = [
        listing["miles"] for listing in all_usable
        if (listing.get("build", {}).get("trim") or "Unknown") == trim
    ]
    print(f"{trim}: {min(mileages):,}–{max(mileages):,} miles")
valid_numeric = [
    listing for listing in all_usable
    if isinstance(listing["price"], (int, float))
    and isinstance(listing["miles"], (int, float))
    and listing["price"] > 0
    and listing["miles"] >= 0
]
print(f"Listings with valid numeric values: {len(valid_numeric)}")
rt_model_data = [
    listing for listing in valid_numeric
    if listing.get("build", {}).get("trim") == "RT"
    and listing.get("build", {}).get("drivetrain") == "4WD"
]
X = np.array([
    [1, listing["build"]["year"] - 2010, listing["miles"] / 1000]
    for listing in rt_model_data
], dtype=float)

y = np.array([
    listing["price"] for listing in rt_model_data
], dtype=float)
if len(rt_model_data) >= 4 and np.linalg.matrix_rank(X) == 3:
    coefficients, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    print("RT model coefficients:", coefficients)
    fitted_prices = X @ coefficients
    residuals = y - fitted_prices
    print(f"Average absolute fitting error: ${np.mean(np.abs(residuals)):,.0f}")
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        if np.linalg.matrix_rank(X[keep]) == 3:
            trial, _, _, _ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
            held_out_price = X[i] @ trial
            print(f"Held-out prediction error: ${abs(y[i] - held_out_price):,.0f}")
            print(
                f"Without {rt_model_data[i].get('vin')}: "
                f"${trial[2]:,.2f} per 1,000 miles"
            )
else:
    print("Not enough independent data to fit the RT model.")
rtl_model_data = [
    listing for listing in valid_numeric
    if listing.get("build", {}).get("trim") == "RTL"
    and listing.get("build", {}).get("drivetrain") == "4WD"
]
print(f"RTL 4WD listings available for comparison: {len(rtl_model_data)}")
X_rtl = np.array([
    [1, listing["build"]["year"] - 2010, listing["miles"] / 1000]
    for listing in rtl_model_data
], dtype=float)

y_rtl = np.array([
    listing["price"] for listing in rtl_model_data
], dtype=float)
if len(rtl_model_data) >= 4 and np.linalg.matrix_rank(X_rtl) == 3:
    rtl_coefficients, _, _, _ = np.linalg.lstsq(X_rtl, y_rtl, rcond=None)
    rtl_errors = y_rtl - X_rtl @ rtl_coefficients
    print("RTL model coefficients:", rtl_coefficients)
    print(f"RTL average absolute fitting error: ${np.mean(np.abs(rtl_errors)):,.0f}")
    rtl_held_out_errors = []
    for i in range(len(y_rtl)):
        keep = np.arange(len(y_rtl)) != i
        if np.linalg.matrix_rank(X_rtl[keep]) == 3:
            trial, _, _, _ = np.linalg.lstsq(
                X_rtl[keep], y_rtl[keep], rcond=None
            )
            rtl_held_out_errors.append(abs(y_rtl[i] - X_rtl[i] @ trial))

    if rtl_held_out_errors:
        print(f"RTL average held-out error: ${np.mean(rtl_held_out_errors):,.0f}")
else:
    print("Not enough independent data to fit the RTL model.")
print("\nRT model listing dates:")
for listing in rt_model_data:
    print(
        listing.get("vin"),
        listing.get("first_seen_at_date"),
        listing.get("last_seen_at_date"),
    )
print("\nRTL model listing dates:")
for listing in rtl_model_data:
    print(
        listing.get("vin"),
        listing.get("first_seen_at_date"),
        listing.get("last_seen_at_date"),
    )
fig, ax = plt.subplots(figsize=(11, 7))

for year in sorted(year_counts):
    vehicles = [
        listing for listing in all_usable
        if listing.get("build", {}).get("year") == year
    ]
    ax.scatter(
        [listing["miles"] for listing in vehicles],
        [listing["price"] for listing in vehicles],
        label=str(year),
        s=65,
        alpha=0.8,
    )

ax.set_xlabel("Mileage (miles)")
ax.set_ylabel("Asking price ($)")
ax.set_title("Honda Ridgeline listings: asking price vs. mileage")
ax.axvline(
    target_mileage,
    color="black",
    linestyle="--",
    label="Your truck: 270,453 miles",
)
ax.legend(title="Model year")
ax.grid(alpha=0.2)
fig.tight_layout()
plt.show()