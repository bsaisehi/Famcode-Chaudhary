import os
import json
import requests
from datetime import datetime


API_URL = "https://raw.githubusercontent.com/drmlive/fancode-live-events/main/fancode.json" 

def transform_url(base_url, replacement):
    if not base_url:
        return ""
    return base_url.replace("index.m3u8", replacement)

def main():
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        print(f"Error fetching API: {e}")
        return

    raw_matches = raw_data.get("matches", [])
    transformed_matches = []
    
    live_count = 0
    upcoming_count = 0

    for match in raw_matches:
        status = match.get("status", "UPCOMING").upper()
        if status == "LIVE":
            live_count += 1
        else:
            upcoming_count += 1

        # base url के रूप में dai_url का इस्तेमाल कर रहे हैं
        dai_url = match.get("dai_url", "")
        
        # Streams Object Setup (अलग-अलग CDN के लिए URL बदलना)
        # अगर आपके पास फिक्स डोमेन हैं, तो इन्हें .replace() से बदला जा सकता है, अभी के लिए ये dai_url को अडाप्ट कर रहे हैं
        primary_url = dai_url.replace("-fb", "") # उदहारण: flive के लिए
        bd_url = dai_url.replace("in-mc-fblive", "bd-mc-flive")
        np_url = dai_url.replace("in-mc-fblive", "np-mc-flive")
        lk_url = dai_url.replace("in-mc-fblive", "lk-mc-flive")
        v1_url = dai_url.replace("in-mc-fblive", "in-mc-pdlive")
        partner_url = dai_url.replace("in-mc-fblive.fancode.com/mumbai", "dai-partner.fancode.com/primary")

        # Resolution streams बनाना (index.m3u8 हटाकर क्वालिटी जोड़ना)
        resolutions = ["240p", "360p", "480p", "540p", "720p", "1080p"]
        auto_streams_dict = {}
        for res in resolutions:
            auto_streams_dict[res] = transform_url(dai_url, f"{res}.m3u8")

        match_obj = {
            "category": match.get("event_category", "Cricket"),
            "title": match.get("title", ""),
            "tournament": match.get("event_name", ""),
            "match_id": match.get("match_id", 0),
            "status": status,
            "startTime": match.get("startTime", ""),
            "image": match.get("src", ""),
            "language": "ENGLISH",
            "streams": {
                "primary": primary_url,
                "fancode_cdn": primary_url,
                "fancode_bd_cdn": bd_url,
                "fancode_np_cdn": np_url,
                "fancode_lk_cdn": lk_url,
                "backup": {
                    "fancode_cdn": dai_url,
                    "fancode_cdn_v1": v1_url,
                    "fancode_dai_cdn": partner_url
                }
            },
            "auto_streams": {
                "ENGLISH": {
                    "streams": auto_streams_dict,
                    "cookie": "",
                    "expires": "1783167966",
                    "expire_date": "Saturday, July 4, 2026, 5:56:06 PM"
                }
            }
        }
        transformed_matches.append(match_obj)

    now = datetime.now()
    final_output = {
        "Author": "Shiv Chaudhary",
        "Telegram": "https://t.me/VoidXDevs",
        "name": "FanCode Live Matches API",
        "updatedAt": now.strftime("%d/%m/%Y, %I:%M:%S %p").lower(),
        "_src_updated": raw_data.get("last update time", now.strftime("%I:%M:%S %p %d-%m-%Y")),
        "total_matches": len(raw_matches),
        "live_matches": live_count,
        "upcoming_matches": upcoming_count,
        "matches": transformed_matches
    }

    with open("fancode.json", "w", encoding="utf-8") as f:
        json.dump(final_output, indent=2, ensure_ascii=False)
    print("fancode.json successfully updated!")

if __name__ == "__main__":
    main()
