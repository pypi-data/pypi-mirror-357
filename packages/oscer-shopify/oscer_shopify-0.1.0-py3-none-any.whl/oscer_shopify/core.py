import requests
import datetime
import time
import csv

class shopify:
    def __init__(self, shop_url, access_token, api_version="2023-10"):
        self.shop_url = shop_url
        self.token = access_token
        self.api_version = api_version
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token
        }

    def get_recent(self, days=0, hours=0, minutes=15, csv="products_images.csv"):
        since_date = (datetime.datetime.utcnow() - datetime.timedelta(days=days, hours=hours, minutes=minutes)).isoformat() + "Z"
        print(f"🕒 Fetching products created after: {since_date}")

        products_url = f"https://{self.shop_url}/admin/api/{self.api_version}/products.json?created_at_min={since_date}&limit=250"
        response = requests.get(products_url, headers=self.headers)

        if response.status_code != 200:
            print(f"❌ Error fetching products: {response.status_code} - {response.text}")
            return

        products = response.json().get("products", [])
        print(f"✅ Found {len(products)} products.\n")

        with open(csv, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Product Title", "Product ID", "Image Count"])

            for idx, product in enumerate(products, start=1):
                product_id = product["id"]
                product_title = product["title"]

                images_url = f"https://{self.shop_url}/admin/api/{self.api_version}/products/{product_id}/images.json"
                img_resp = requests.get(images_url, headers=self.headers)
                time.sleep(0.6)

                if img_resp.status_code == 200:
                    images = img_resp.json().get("images", [])
                    image_count = len(images)
                    print(f"🔍 [{idx}/{len(products)}] {product_title} - Images: {image_count}")
                    writer.writerow([product_title, product_id, image_count])

                elif img_resp.status_code == 429:
                    print(f"⚠️ 429 Rate Limit hit for {product_title}. Retrying...")
                    time.sleep(2)
                    retry_resp = requests.get(images_url, headers=self.headers)
                    if retry_resp.status_code == 200:
                        images = retry_resp.json().get("images", [])
                        image_count = len(images)
                        print(f"🔁 Retried: {product_title} - Images: {image_count}")
                        writer.writerow([product_title, product_id, image_count])
                    else:
                        print(f"❌ Retry failed for {product_title}: {retry_resp.status_code}")
                        writer.writerow([product_title, product_id, "Error after retry"])
                else:
                    print(f"❌ Error for {product_title}: {img_resp.status_code}")
                    writer.writerow([product_title, product_id, f"Error {img_resp.status_code}"])

        print(f"\n✅ Done! Image count saved to {csv}")